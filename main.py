import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine   # lo mejoramos abajo

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

archivo = st.file_uploader("Sube captura de cualquier liga (Caliente.mx)", 
                          type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("🔍 Detectando partidos con IA visual..."):
        games = analyze_betting_image(archivo)   # ← ahora list[dict]
    
    if games:
        # === VERIFICACIÓN MEJORADA ===
        st.subheader("🏟️ Verificación de Partidos")
        check_df = []
        for i, g in enumerate(games, 1):
            check_df.append({
                "Partido": i,
                "Local": g["home"],
                "Odd Local": g["home_odd"],
                "Empate": g["draw_odd"],
                "Visitante": g["away"],
                "Odd Visitante": g["away_odd"]
            })
        st.dataframe(check_df, use_container_width=True)
        
        # === ANÁLISIS EV + PARLAY ===
        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)   # ← nuevo formato
        
        st.header("📊 Análisis de Valor IA")
        col1, col2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (col1 if idx % 2 == 0 else col2):
                st.info(f"**{r['partido']}**\nPick: {r['pick']} | Prob: {r['probabilidad']}% | Cuota: {r['cuota']}")
        
        if parlay:
            st.markdown("---")
            st.header("🔥 Parlay Maestro Detectado")
            monto = st.number_input("💰 Monto a apostar", value=100.0, step=10.0)
            sim = engine.simulate_parlay_profit(parlay, monto)
            
            for p in parlay:
                st.write(f"✅ {p['partido']} → {p['pick']}")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']}")
            m2.metric("Pago Total", f"${sim['pago_total']:.2f}")
            m3.metric("Ganancia Neta", f"${sim['ganancia_neta']:.2f}")
    else:
        st.error("No se detectaron partidos. Prueba otra captura.")
else:
    st.info("Sube una captura de cualquier liga...")



