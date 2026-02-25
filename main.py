import streamlit as st
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico, obtener_metricas_sidebar

st.set_page_config(page_title="BETTING AI", layout="wide")

# --- SIDEBAR DINÁMICO ---
with st.sidebar:
    st.header("📊 Historial")
    metrics = obtener_metricas_sidebar()
    if metrics:
        st.metric("ROI Total", f"{metrics['roi']:.1f}%")
        st.metric("Apostado", f"${metrics['apostado']:.2f}")
        st.markdown("---")
        for r in metrics['ultimos']:
            st.write(f"📅 {r['Fecha']} | **${r['ganancia_neta']:.1f}**")
    else:
        st.info("Sin registros")

st.title("🤖 PARLAY MAESTRO")
archivo = st.file_uploader("Sube captura", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando..."):
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación OCR"):
            st.write(games)

        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("📊 Análisis IA (85%+)")
        if not resultados:
            st.warning("⚠️ Ningún mercado superó el filtro del 85% para estos partidos.")
        
        c1, c2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (c1 if idx % 2 == 0 else c2):
                st.info(f"**{r['partido']}**\n\nPick: **{r['pick']}** ({r['probabilidad']}%)")

        if parlay:
            st.markdown("---")
            monto = st.number_input("💰 Inversión", value=100.0)
            sim = engine.simulate_parlay_profit(parlay, monto)
            
            # Tarjetas de apuesta
            for p in parlay:
                st.markdown(f"""<div style="background:#1e1e1e; padding:10px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:5px;">
                    <b>{p['pick']}</b> | Prob: {p['probabilidad']}%</div>""", unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota", f"{sim['cuota_total']}x")
            m2.metric("Pago", f"${sim['pago_total']}")
            
            if st.button("💾 REGISTRAR"):
                sim['monto'] = monto
                registrar_parlay_automatico(sim, " | ".join([p['pick'] for p in parlay]))
                st.balloons()
                st.rerun()
