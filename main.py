import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.results_tracker import registrar_parlay_automatico, actualizar_resultados_api

# Configuración inicial
st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

# Sincronización automática de resultados al iniciar/refrescar
actualizar_resultados_api()

st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# --- BARRA LATERAL: MÉTRICAS GENERALES ---
with st.sidebar:
    st.header("📊 Panel de Control")
    if os.path.exists("data/parlay_history.csv"):
        df_stats = pd.read_csv("data/parlay_history.csv")
        finalizadas = df_stats[df_stats['Estado'] != 'Pendiente']
        total_profit = finalizadas['Ganancia_Neta'].sum() if not finalizadas.empty else 0.0
        st.metric("Profit Total Real", f"${total_profit:.2f}")
    else:
        st.info("Sin historial de testeo")

# --- CARGA DE CAPTURA ---
archivo = st.file_uploader("Sube tu captura de Caliente / Odds", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando mercados y cuotas..."):
        # Procesar imagen
        games = analyze_betting_image(archivo)
    
    if games:
        # 🏟️ VERIFICACIÓN DE PARTIDOS (OCULTABLE)
        with st.expander("🏟️ Verificación de Partidos Detectados", expanded=False):
            st.dataframe(games, use_container_width=True)

        # Iniciar motor de análisis
        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        # --- SIMULADOR DE TICKET ---
        st.header("🔥 Simulación de Parlay Sugerido")
        
        # Entrada de monto con lógica de negocio
        monto_inversion = st.number_input("💰 Inversión para este Parlay (MXN)", value=100.0, step=50.0)
        
        # Obtener cálculos reales (Multiplicación de decimales)
        sim = engine.simulate_parlay_profit(parlay, monto_inversion)
        sim['monto'] = monto_inversion

        # Mostrar Picks del Ticket
        for p in parlay:
            st.markdown(f"""
            <div style="background:#1e1e1e; padding:12px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:8px;">
                <b style="color:#00ff9d; font-size:1.1em;">{p['pick']}</b><br>
                <span style="color:#888; font-size:0.9em;">{p['partido']} | Momio Detectado: {p['cuota']}</span>
            </div>
            """, unsafe_allow_html=True)

        # Métricas del Ticket
        c1, c2, c3 = st.columns(3)
        c1.metric("Cuota Total (Real)", f"{sim['cuota_total']}x")
        c2.metric("Pago Potencial", f"${sim['pago_total']}")
        c3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

        # Botón de Registro
        if st.button("🚀 Registrar para Seguimiento Automático", use_container_width=True):
            picks_summary = " | ".join([p['pick'] for p in parlay])
            registrar_parlay_automatico(sim, picks_summary)
            st.balloons()
            st.success("✅ Registrado con éxito. El sistema cerrará la apuesta cuando termine el partido.")

# --- SECCIÓN DE SEGUIMIENTO (AUTOMÁTICO) ---
st.markdown("---")
st.subheader("⏳ Estatus de Apuestas en Curso")

if os.path.exists("data/parlay_history.csv"):
    df_h = pd.read_csv("data/parlay_history.csv")
    
    # Función para dar color a la tabla
    def color_status(val):
        if val == 'Ganada': return 'background-color: #004d2c; color: #00ff9d'
        if val == 'Perdida': return 'background-color: #4d0000; color: #ff4b4b'
        return 'background-color: #333; color: #ffcc00'

    st.dataframe(
        df_h.style.applymap(color_status, subset=['Estado']),
        use_container_width=True
    )
else:
    st.info("No hay parlays registrados para seguimiento automático.")
