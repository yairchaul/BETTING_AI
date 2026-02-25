import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico

st.set_page_config(page_title="BETTING AI", layout="wide")

# --- SIDEBAR: HISTORIAL SEGURO ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        try:
            hist = pd.read_csv("parlay_history.csv")
            if not hist.empty:
                apostado = hist.get('monto', pd.Series([0])).sum()
                ganancia = hist.get('ganancia_neta', pd.Series([0])).sum()
                st.metric("ROI", f"{(ganancia/apostado*100 if apostado>0 else 0):.1f}%")
                st.metric("Total Apostado", f"${apostado:.2f}")
                st.markdown("---")
                for _, r in hist.tail(5).iterrows():
                    st.write(f"📅 {r.get('Fecha','S/F')} | **${r.get('ganancia_neta',0):.1f}**")
        except: st.error("Error al leer historial")
    else: st.info("Sin registros")

# --- APP PRINCIPAL ---
st.title("🤖 PARLAY MAESTRO")
archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Leyendo momios..."):
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación OCR", expanded=False):
            st.dataframe(games)

        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("🎯 Análisis de Valor (>85%)")
        if not resultados:
            st.warning("Ninguna opción superó el 85% de probabilidad.")
        
        c1, c2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (c1 if idx % 2 == 0 else c2):
                st.info(f"**{r['partido']}**\n\nPick: **{r['pick']}** | Prob: {r['probabilidad']}%")

        if parlay:
            st.markdown("---")
            monto = st.number_input("Inversión (MXN)", value=100.0)
            sim = engine.simulate_parlay_profit(parlay, monto)
            
            # Tarjetas de picks
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:10px; border-radius:8px; border-left:4px solid #00ff9d; margin-bottom:5px;">
                <b>{p['pick']}</b> | Cuota: {p['cuota']} | {p['probabilidad']}%
                </div>
                """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']}x")
            m2.metric("Pago Total", f"${sim['pago_total']}")
            
            if st.button("💾 REGISTRAR APUESTA"):
                sim['monto'] = monto
                registrar_parlay_automatico(sim, " | ".join([p['pick'] for p in parlay]))
                st.balloons()
                st.rerun()

