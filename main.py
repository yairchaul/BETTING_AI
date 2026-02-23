# main.py - Ticket Pro - NBA AI +EV (versión funcional y modular Streamlit)
import streamlit as st

# Imports limpios
from modules.autopicks import generar_picks_auto
from modules.bankroll import obtener_stake_sugerido, calcular_roi
from modules.telegram_bot import enviar_pick  # Asume existe; si no, cambia a nombre real o comenta
from modules.connector import get_live_data
from modules.montecarlo import simular_total  # Nueva simulación Monte Carlo
from modules.ev_engine import calcular_ev
from modules.injuries import verificar_lesiones
from modules.ranking import ranking_edges
from modules.tracker import guardar_pick

# Configuración de página
st.set_page_config(page_title="Ticket Pro - NBA AI", layout="wide")

# Estilo oscuro "Ticket Pro"
st.markdown("""
    <style>
        body {background-color: #121212; color: #ffffff;}
        .stApp {background-color: #121212;}
        .sidebar .sidebar-content {background-color: #0e1117;}
        .high {border-left: 5px solid #00ff00; padding: 10px; margin: 5px 0; border-radius: 4px;}
        .medium {border-left: 5px solid #ffff00; padding: 10px; margin: 5px 0; border-radius: 4px;}
        .low {border-left: 5px solid #ff0000; padding: 10px; margin: 5px 0; border-radius: 4px;}
    </style>
""", unsafe_allow_html=True)

st.title("🔥 Ticket Pro - NBA AI +EV v10.0")

# Sidebar: Bankroll y métricas
with st.sidebar:
    st.header("Bankroll")
    bankroll = st.number_input("💰 Bankroll actual (MXN)", min_value=0.0, value=10000.0, step=100.0)
    st.metric("Inversión Sugerida (10%)", f"${bankroll * 0.10:,.2f}")
    st.metric("ROI Objetivo", "550%")
    
    if st.button("Actualizar ROI"):
        try:
            roi = calcular_roi(0, 0)  # Placeholder - ajusta con datos reales de tracker
            st.success(f"ROI calculado: {roi:.2f}%")
        except Exception as e:
            st.error(f"Error calculando ROI: {e}")

# Extracción de datos vivos
with st.spinner("Extrayendo mercados de Caliente.mx..."):
    try:
        juegos = get_live_data()
    except Exception as e:
        st.error(f"Error en conector: {e}")
        juegos = []

if not juegos:
    st.warning("No hay juegos o mercados disponibles hoy. Revisa conexión o Caliente.mx.")
else:
    st.success(f"Encontrados {len(juegos)} eventos/juegos.")
    
    picks = []
    
    for g in juegos:
        try:
            # Ajusta según la estructura real de g (de get_live_data)
            line = g.get("line", 0.0)
            media_modelo = line + 4  # Tu ajuste original
            
            # Nueva simulación Monte Carlo para prob
            prob = simular_total(media_modelo)  # De montecarlo.py
            
            ev = calcular_ev(prob)
            
            if ev <= 0:
                continue
            
            # Clasificación de confianza (numérica para stake)
            if ev > 0.08:
                confianza = "🔥 EXCELENTE"
                css_class = "high"
                confianza_num = 90
            elif ev > 0.04:
                confianza = "⚡ BUENA"
                css_class = "medium"
                confianza_num = 80
            else:
                confianza = "➖ BAJA"
                css_class = "low"
                confianza_num = 60
            
            stake = obtener_stake_sugerido(bankroll, confianza_num)
            lesiones = verificar_lesiones(g.get("home", "Unknown"))
            juego_txt = f"{g.get('away', '?')} @ {g.get('home', '?')}"
            
            # Tarjeta visual
            with st.container():
                st.markdown(f"""
                    <div class="{css_class}">
                        <strong>{juego_txt}</strong><br>
                        Prob Over: {prob*100:.1f}%  
                        EV: {ev*100:.2f}%  
                        Confianza: {confianza}<br>
                        Stake sugerido: ${stake:.2f} MXN  
                        Lesiones: {lesiones}
                    </div>
                """, unsafe_allow_html=True)
            
            # Guardar y enviar si buena
            guardar_pick(juego_txt, stake, ev)
            picks.append({"game": juego_txt, "ev": ev})
            
            if ev > 0.04:
                texto = f"""
🔥 AUTO PICK
Juego: {juego_txt}
EV: {ev*100:.2f}%
Stake: ${stake:.2f}
                """
                try:
                    enviar_pick(texto)
                    st.info(f"Pick enviado a Telegram: {juego_txt}")
                except Exception as e:
                    st.error(f"Error enviando a Telegram: {e}")
        
        except Exception as e:
            st.error(f"Error procesando juego {g}: {e}")
            continue
    
    # Resumen final
    if picks:
        try:
            ranking_edges(picks)
            st.subheader("Resumen de Picks")
            st.write(f"Picks con +EV encontrados: {len(picks)}")
        except Exception as e:
            st.error(f"Error en ranking: {e}")
    else:
        st.info("No se encontraron picks con valor esperado positivo hoy.")
    
# Picks auto (opcional al final)
if st.button("Generar Picks Auto"):
    auto_picks = generar_picks_auto()
    st.write("Picks Automáticos:", auto_picks)
