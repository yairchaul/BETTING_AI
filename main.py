import streamlit as st
import os
import sys

# Asegurar que Streamlit encuentre tus módulos locales
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

from modules.vision_reader import analyze_betting_image
from modules.ev_engine import calcular_ev
from modules.tracker import guardar_pick_automatico # Importamos el guardado

st.title("🏀 Ticket Pro - Vision Terminal")

# Sidebar: Gestión de Bankroll
bankroll = st.sidebar.number_input("Bankroll actual (MXN)", value=1000.0)
st.sidebar.markdown("---")
st.sidebar.info("La API Key se lee directamente desde los Secrets de Streamlit Cloud.")

# Carga de Imagen
st.header("📸 Scanner de Mercados")
archivo = st.file_uploader("Sube captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

if archivo:
    st.image(archivo, caption="Captura subida", use_column_width=True)
    
    if st.button("🔥 Analizar con IA"):
        with st.spinner("IA leyendo mercados..."):
            # Llama a Gemini Vision usando la API Key de tus Secrets
            datos = analyze_betting_image(archivo)
            
            if datos and "juegos" in datos:
                st.success(f"Se detectaron {len(datos['juegos'])} mercados")
                
                for juego in datos["juegos"]:
                    # Validamos nombres de equipos para evitar errores de despliegue
                    home = juego.get('home', 'Equipo Local')
                    away = juego.get('away', 'Equipo Visitante')
                    
                    with st.expander(f"📌 {away} @ {home}"):
                        col1, col2 = st.columns(2)
                        
                        # Extraemos datos limpios de la IA
                        linea = juego.get('total_line', 'N/A')
                        momio = juego.get('odds_over', 'N/A')
                        
                        col1.write(f"**Línea Total:** {linea}")
                        col1.write(f"**Momio Over:** {momio}")
                        
                        # Cálculo de EV (Ejemplo con probabilidad del 54%)
                        probabilidad_modelo = 0.54 
                        ev = calcular_ev(probabilidad_modelo)
                        col2.metric("Expected Value", f"{ev*100:.2f}%")
                        
                        # BOTÓN DE GUARDADO: Registra la apuesta en el historial
                        stake_sugerido = bankroll * 0.05 # 5% del bankroll
                        if st.button(f"Guardar Pick: {away} vs {home}", key=f"btn_{home}"):
                            guardar_pick_automatico(juego, ev, stake_sugerido)
                            st.toast(f"✅ Pick guardado en historial")
            else:
                st.error("No se pudieron extraer datos. Verifica que la imagen sea clara y la API Key sea válida.")
