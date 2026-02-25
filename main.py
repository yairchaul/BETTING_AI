import streamlit as st
import pandas as pd
import datetime
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración Responsive
st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# --- SIDEBAR: HISTORIAL ---
with st.sidebar:
    st.header("📊 Historial")
    file_path = "parlay_history.csv"
    if os.path.exists(file_path):
        try:
            hist = pd.read_csv(file_path)
            if not hist.empty:
                apostado = hist['monto'].sum()
                ganancia = hist['ganancia_neta'].sum()
                roi = (ganancia / apostado * 100) if apostado > 0 else 0
                
                st.metric("ROI Total", f"{roi:.1f}%")
                st.metric("Apostado", f"${apostado:.2f}")
                
                st.markdown("---")
                st.subheader("📝 Últimos Registros")
                # Mostrar los últimos 5 parlays con indicador visual
                for _, row in hist.tail(5).iterrows():
                    color = "🟢" if row['ganancia_neta'] > 0 else "⚪"
                    st.write(f"{color} **{row['Fecha']}**")
                    st.caption(f"Neto: ${row['ganancia_neta']:.2f} | Cuota: {row['cuota_total']}x")
        except Exception as e:
            st.error("Error al cargar historial")
    else:
        st.info("Aún no hay parlays registrados")

# --- CARGA DE ARCHIVO ---
archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando imagen con Google Vision..."):
        games = analyze_betting_image(archivo)
    
    if games:
        # SECCIÓN COLAPSABLE (Debug)
        with st.expander("🏟️ Verificación de Partidos (Click para ver/ocultar)", expanded=False):
            st.dataframe(games, use_container_width=True)

        # MOTOR DE ANÁLISIS (CASCADA)
        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis de Valor IA")
        col1, col2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (col1 if idx % 2 == 0 else col2):
                st.info(f"**{r['partido']}**\n\nPick: **{r['pick']}** | Prob: {r['probabilidad']}%")

        # --- SECCIÓN DEL TICKET (PARLAY) ---
        if parlay:
            st.markdown("---")
            st.header("🔥 Tu Ticket Profesional")
            monto = st.number_input("💰 Monto (MXN)", value=100.0, step=10.0)
            
            # Cálculo de simulación
            sim = engine.simulate_parlay_profit(parlay, monto)

            # Tarjetas visuales de los picks elegidos
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:10px;">
                    <small style="color:gray;">{p['partido']}</small><br>
                    <b style="color:#00ff9d; font-size:18px;"> {p['pick']}</b><br>
                    <small>Cuota: {p['cuota']} | Confianza: {'⭐' * (max(1, int(p['probabilidad']/20)))}</small>
                </div>
                """, unsafe_allow_html=True)

            # Métricas del Parlay
            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']}x")
            m2.metric("Pago Total", f"${sim['pago_total']}")
            m3.metric("Ganancia", f"${sim['ganancia_neta']}")

            # --- BLOQUE DE REGISTRO ADAPTADO ---
            if st.button("💾 Registrar como Apostado"):
                from modules.tracker import registrar_parlay_automatico
                
                # Preparamos el texto de los picks para el historial
                picks_string = " | ".join([p['pick'] for p in parlay])
                
                # Pasamos los datos calculados al tracker
                sim['monto'] = monto  # Nos aseguramos que el monto vaya en el diccionario
                registrar_parlay_automatico(sim, picks_string)
                
                st.balloons()
                st.success("✅ ¡Apuesta registrada exitosamente!")
                st.rerun() # Esto refresca el Sidebar con los nuevos datos
