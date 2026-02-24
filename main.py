import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Parlay Maestro IA", layout="wide")
st.title("🤖 Parlay Maestro — Betting AI")

archivo = st.file_uploader("Subir captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Leyendo imagen..."):
        equipos = analyze_betting_image(archivo)

    if equipos:
        # --- NUEVA TABLA DE VERIFICACIÓN ---
        st.subheader("🏟️ Partidos Detectados (Verifica si son correctos)")
        
        datos_tabla = []
        for i in range(0, len(equipos) - 1, 2):
            datos_tabla.append({
                "Partido #": (i // 2) + 1,
                "Local": equipos[i],
                "Visitante": equipos[i+1]
            })
        
        st.table(datos_tabla)
        # ----------------------------------

        if len(equipos) >= 2:
            engine = EVEngine()
            resultados, parlay = engine.build_parlay(equipos)

            st.header("📊 Análisis de Valor")
            for r in resultados:
                st.write(f"**{r['partido']}** | Pick: {r['pick']} | Prob: {r['probabilidad']}% | Cuota: {r['cuota']}")

            if parlay:
                st.header("🔥 Parlay Sugerido")
                cuota_total = 1.0
                for p in parlay:
                    cuota_total *= p["cuota"]
                    st.success(f"✅ {p['partido']} → {p['pick']}")
                
                st.metric("Cuota Total Estimada", f"{cuota_total:.2f}")
    else:
        st.error("No se detectaron partidos. Intenta con una imagen más clara o sin recortes.")
