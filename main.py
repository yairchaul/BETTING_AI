import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico

st.set_page_config(page_title="BETTING AI", layout="wide")

# --- SIDEBAR: BLINDAJE TOTAL ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        try:
            hist = pd.read_csv("parlay_history.csv")
            if not hist.empty:
                # Normalizamos nombres de columnas para evitar KeyError
                hist.columns = [c.lower() for c in hist.columns]
                apostado = hist.get('monto', pd.Series([0])).sum()
                ganancia = hist.get('ganancia_neta', pd.Series([0])).sum()
                st.metric("ROI Total", f"{(ganancia/apostado*100 if apostado > 0 else 0):.1f}%")
                st.markdown("---")
                for _, r in hist.tail(5).iterrows():
                    # Usamos .get() para evitar errores si la columna no existe
                    f = r.get('fecha', 'S/F')
                    g = r.get('ganancia_neta', 0.0)
                    st.write(f"📅 {f} | **${g:.1f}**")
        except: st.error("Error de lectura")
    else: st.info("Sin registros")

# --- APP PRINCIPAL ---
st.title("🤖 PARLAY MAESTRO — Filtro 85%")
archivo = st.file_uploader("Sube captura", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando con Visión..."):
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos"):
            st.dataframe(games, use_container_width=True)

        # Ahora el constructor sí acepta el threshold
        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("🎯 Análisis de Valor IA")
        c1, c2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (c1 if idx % 2 == 0 else c2):
                # Verificamos si pasa el filtro del 85%
                if r.get('pasa_filtro', False):
                    st.success(f"✅ **{r['partido']}**\n\n{r['pick']} | **{r['probabilidad']}%**")
                else:
                    st.warning(f"❌ **{r['partido']}**\n\n{r['pick']} | {r['probabilidad']}%")

        if parlay:
            st.markdown("---")
            monto = st.number_input("Inversión (MXN)", value=100.0)
            sim = engine.simulate_parlay_profit(parlay, monto)
            
            # SOLUCIÓN AL SYNTAX ERROR (Cierre de f-string)
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:10px; border-radius:8px; border-left:4px solid #00ff9d; margin-bottom:5px;">
                    <b>{p['pick']}</b> | {p['probabilidad']}% | Cuota: {p.get('cuota', '1.0')}
                </div>
                """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota", f"{sim['cuota_total']}x")
            m2.metric("Pago", f"${sim['pago_total']}")
            
            if st.button("💾 REGISTRAR APUESTA"):
                sim['monto'] = monto
                registrar_parlay_automatico(sim, " | ".join([p['pick'] for p in parlay]))
                st.balloons()
                st.rerun()
