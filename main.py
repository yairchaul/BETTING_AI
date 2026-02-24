import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Parlay Maestro IA", layout="wide")

# --- SIDEBAR (Recuperamos el monto) ---
st.sidebar.header("💰 Configuración")
monto_apuesta = st.sidebar.number_input("Monto a apostar ($)", value=100.0, step=10.0)

st.title("🤖 Parlay Maestro — Betting AI")

archivo = st.file_uploader("Subir captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando imagen..."):
        equipos = analyze_betting_image(archivo)

    if equipos:
        # --- TABLA DE VERIFICACIÓN ---
        st.subheader("🏟️ Partidos Detectados")
        datos_tabla = []
        for i in range(0, len(equipos) - 1, 2):
            datos_tabla.append({"Partido": (i//2)+1, "Local": equipos[i], "Visitante": equipos[i+1]})
        st.table(datos_tabla)

        if len(equipos) >= 2:
            engine = EVEngine()
            resultados, parlay = engine.build_parlay(equipos)

            # --- RESULTADOS INDIVIDUALES ---
            st.header("📊 Análisis IA")
            col1, col2 = st.columns(2)
            for idx, r in enumerate(resultados):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    st.info(f"**{r['partido']}**\n\nPick: {r['pick']} | Prob: {r['probabilidad']}% | Cuota: {r['cuota']}")

            # --- PARLAY Y SIMULACIÓN ---
            if parlay:
                st.markdown("---")
                st.header("🔥 Parlay Sugerido (Confianza Alta)")
                
                simulacion = engine.simulate_parlay_profit(parlay, monto_apuesta)
                
                for p in parlay:
                    st.write(f"✅ {p['partido']} → {p['pick']}")

                c1, c2, c3 = st.columns(3)
                c1.metric("Cuota Total", simulacion['cuota_total'])
                c2.metric("Pago Total", f"${simulacion['pago_total']}")
                c3.metric("Ganancia Neta", f"${simulacion['ganancia_neta']}", delta="ROI Positivo")
    else:
        st.error("No se detectaron equipos. Verifica que la imagen sea clara.")

