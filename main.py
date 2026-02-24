import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Parlay Maestro IA", layout="wide")

st.title("🤖 Parlay Maestro — Betting AI")
st.markdown("---")

# Sidebar para configuración
st.sidebar.header("Configuración de Simulación")
monto_base = st.sidebar.number_input("💰 Monto a apostar ($)", value=100.0, step=10.0)

archivo = st.file_uploader("Subir captura de pantalla (Caliente, Codere, etc.)", type=["png", "jpg", "jpeg"])

if archivo:
    # 1. Procesamiento de imagen
    with st.spinner("IA analizando mercados..."):
        equipos = analyze_betting_image(archivo)

    if equipos:
        st.success(f"Se detectaron {len(equipos)} posibles equipos/mercados.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📍 Equipos Detectados")
            st.write(equipos)

        # 2. Motor de Análisis
        if len(equipos) >= 2:
            engine = EVEngine()
            resultados, parlay = engine.build_parlay(equipos)

            with col2:
                st.subheader("📊 Análisis de Valor (EV+)")
                for r in resultados:
                    color = "green" if r['probabilidad'] >= 80 else "white"
                    st.markdown(f"**{r['partido']}**")
                    st.caption(f"Pick: {r['pick']} | Prob: {r['probabilidad']}% | Cuota: {r['cuota']}")

            # 3. Generación de Parlay
            st.markdown("---")
            if parlay:
                st.header("🔥 Parlay Sugerido (Alta Probabilidad)")
                
                cuota_total = 1.0
                for p in parlay:
                    cuota_total *= p["cuota"]
                    st.info(f"✅ {p['partido']} → {p['pick']} (Prob: {p['probabilidad']}%)")

                pago_total = monto_base * cuota_total
                ganancia_neta = pago_total - monto_base

                # Métricas finales
                c1, c2, c3 = st.columns(3)
                c1.metric("Cuota Total", f"{cuota_total:.2f}")
                c2.metric("Pago Estimado", f"${pago_total:.2f}")
                c3.metric("Ganancia Neta", f"${ganancia_neta:.2f}", delta=f"{cuota_total:.1f}x")
            else:
                st.warning("La IA no encontró picks con probabilidad > 80% para armar un parlay seguro.")
    else:
        st.error("No se pudieron extraer equipos. Intenta con una imagen más clara.")
else:
    st.info("Esperando imagen para iniciar análisis...")

