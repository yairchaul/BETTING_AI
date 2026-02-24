import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")

st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# --- PANEL DE CONTROL ---
archivo = st.file_uploader("Sube tu captura de Caliente.mx / Liga MX", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("IA Procesando mercados y detectando equipos..."):
        equipos = analyze_betting_image(archivo)

    if equipos:
        # 1. Tabla de Verificación (Para asegurar que no hay errores como León vs Chivas)
        st.subheader("🏟️ Verificación de Partidos")
        check_data = []
        for i in range(0, len(equipos) - 1, 2):
            check_data.append({"Partido": (i//2)+1, "Local": equipos[i], "Visitante": equipos[i+1]})
        st.table(check_data)

        if len(equipos) >= 2:
            engine = EVEngine()
            resultados, parlay = engine.build_parlay(equipos)

            # 2. Análisis de Valor (Misma estructura de antes)
            st.header("📊 Análisis de Valor IA")
            col1, col2 = st.columns(2)
            for idx, r in enumerate(resultados):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    st.info(f"**{r['partido']}**\n\nPick: {r['pick']} | Prob: {r['probabilidad']}% | Cuota: {r['cuota']}")

            # 3. Parlay y Simulador (Misma estructura de antes)
            if parlay:
                st.markdown("---")
                st.header("🔥 Parlay Maestro Detectado")
                
                # Monto a apostar
                monto = st.number_input("💰 Monto a apostar", value=100.0, step=10.0)
                
                # Usamos el simulador del engine
                sim = engine.simulate_parlay_profit(parlay, monto)
                
                for p in parlay:
                    st.write(f"✅ {p['partido']} → {p['pick']}")

                # Métricas visuales
                m1, m2, m3 = st.columns(3)
                m1.metric("Cuota Total", f"{sim['cuota_total']}")
                m2.metric("Pago Total", f"${sim['pago_total']}")
                m3.metric("Ganancia Neta", f"${sim['ganancia_neta']}", delta="ROI Sugerido")
    else:
        st.error("No se detectaron equipos. Asegúrate de que los nombres sean visibles en la captura.")
else:
    st.info("Esperando captura de pantalla para iniciar el análisis...")



