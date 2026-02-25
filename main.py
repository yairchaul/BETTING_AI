import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.tracker import registrar_parlay_automatico

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

# --- SIDEBAR: HISTORIAL SEGURO ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        try:
            hist = pd.read_csv("parlay_history.csv")
            if not hist.empty:
                # Usamos .get() para evitar KeyError si la columna no existe
                apostado = hist.get('monto', pd.Series([0])).sum()
                ganancia = hist.get('ganancia_neta', pd.Series([0])).sum()
                st.metric("ROI Total", f"{(ganancia/apostado*100 if apostado > 0 else 0):.1f}%")
                st.markdown("---")
                for _, r in hist.tail(5).iterrows():
                    fecha = r.get('Fecha', 'S/F')
                    neta = r.get('ganancia_neta', 0.0)
                    st.write(f"📅 {fecha} | **${neta:.2f}**")
        except Exception:
            st.error("Error al cargar historial")
    else:
        st.info("Sin registros aún")

# --- APP PRINCIPAL ---
st.title("🤖 PARLAY MAESTRO — Filtro 85%")
archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando con Visión por Proximidad..."):
        # Llamada a tu función optimizada de coordenadas
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos Detectados (OCR)"):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine(threshold=0.85)
        resultados, parlay = engine.build_parlay(games)

        st.header("🎯 Análisis de Capas (>85%)")
        
        c1, c2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (c1 if idx % 2 == 0 else c2):
                if r.get('pasa_filtro', False):
                    st.success(f"✅ **{r['partido']}**\n\nPick: **{r['pick']}** | **{r['probabilidad']}%**")
                else:
                    st.warning(f"❌ **{r['partido']}**\n\nPick: **{r['pick']}** | {r['probabilidad']}% (Bajo el 85%)")

        if parlay:
            st.markdown("---")
            st.header("🔥 Sugerencia de Parlay Élite")
            
            monto = st.number_input("💰 Inversión (MXN)", value=100.0, step=50.0)
            sim = engine.simulate_parlay_profit(parlay, monto)
            
            # Tarjetas visuales corregidas (Sin errores de string literal)
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:10px;">
                    <small style="color:gray;">{p['partido']}</small><br>
                    <b style="color:#00ff9d; font-size:18px;">{p['pick']}</b><br>
                    <small>Probabilidad: {p['probabilidad']}% | Cuota: {p['cuota']}</small>
                </div>
                """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']}x")
            m2.metric("Pago Estimado", f"${sim['pago_total']}")
            m3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")
            
            if st.button("💾 REGISTRAR APUESTA"):
                sim['monto'] = monto
                picks_txt = " | ".join([p['pick'] for p in parlay])
                registrar_parlay_automatico(sim, picks_txt)
                st.balloons()
                st.rerun()
        else:
            st.error("🚫 Ninguna opción alcanzó el 85% de probabilidad mínima.")
