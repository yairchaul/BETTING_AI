import streamlit as st
from modules.vision_reader import read_ticket_image
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Bet Detector Pro", layout="wide")
st.title("🎯 Detector de Apuestas Real-Time")

uploaded = st.file_uploader("Sube tu captura de Caliente/Bet365", type=['png', 'jpg', 'jpeg'])

if uploaded:
    with st.spinner("Analizando imagen y consultando API..."):
        games_data = read_ticket_image(uploaded)
        
        if not games_data:
            st.error("No se detectaron apuestas. Intenta con otra imagen.")
        else:
            final_picks = []
            st.subheader("✅ Equipos Identificados y Análisis de Forma")
            
            for partido in games_data:
                # 1. Validar equipos en la API
                res_h = validar_y_obtener_stats(partido['home'])
                res_a = validar_y_obtener_stats(partido['away'])
                
                if res_h['valido'] and res_a['valido']:
                    # Mostrar validación visual
                    with st.container():
                        c1, c2, c3, c4 = st.columns([1, 0.5, 1, 2])
                        c1.image(res_h['logo'], width=40)
                        c1.caption(res_h['nombre_real'])
                        c2.write("vs")
                        c3.image(res_a['logo'], width=40)
                        c3.caption(res_a['nombre_real'])
                        
                        # 2. Obtener goles reales últimos 5 partidos
                        stats_h = obtener_forma_reciente(res_h['id'])
                        stats_a = obtener_forma_reciente(res_a['id'])
                        
                        # 3. Calcular mejor pick
                        pick = obtener_mejor_apuesta(partido, stats_h, stats_a)
                        if pick:
                            c4.success(f"Propuesta: {pick['selection']} ({pick['odd']})")
                            final_picks.append(pick)
                else:
                    st.warning(f"⚠️ No se encontró en API: {partido['home']} vs {partido['away']}")

            # 4. Generar Parlay Inteligente
            if final_picks:
                st.divider()
                parlay = build_smart_parlay(final_picks)
                if parlay:
                    st.header("🚀 Parlay Sugerido (Basado en Datos Reales)")
                    col_a, col_b = st.columns(2)
                    col_a.metric("Cuota Total", f"{parlay['total_odd']}x")
                    col_b.metric("Probabilidad", f"{round(parlay['combined_prob']*100, 2)}%")
                    st.write("---")
                    for m in parlay['matches']:
                        st.write(f"🔹 {m}")

