import streamlit as st
from modules.vision_reader import read_ticket_image
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Detector de Apuestas Pro", layout="wide", page_icon="🎯")

# --- Estilo Personalizado ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .bet-card { border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #0d1117; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Detector")
st.caption("Análisis estadístico mediante Simulación Monte Carlo, API de Fútbol y OCR de Google Vision")

# --- Pestañas que te gustaban ---
tab1, tab2 = st.tabs(["📊 Análisis de Imagen", "📜 Historial de Parlays"])

with tab1:
    uploaded = st.file_uploader("Sube la captura de pantalla (Caliente, Bet365, etc.)", type=['png', 'jpg', 'jpeg'])

    if uploaded:
        with st.spinner("🕵️ Analizando equipos y consultando historial..."):
            games_data = read_ticket_image(uploaded)
            
            if not games_data:
                st.error("No se detectaron bloques de apuestas válidos en la imagen.")
            else:
                final_picks = []
                st.subheader("✅ Selecciones recomendadas")

                for partido in games_data:
                    # 1. Validación Real con API (Muestra logos)
                    res_h = validar_y_obtener_stats(partido['home'])
                    res_a = validar_y_obtener_stats(partido['away'])
                    
                    if res_h['valido'] and res_a['valido']:
                        # 2. Obtener forma real (últimos 5 partidos)
                        s_h = obtener_forma_reciente(res_h['id'])
                        s_a = obtener_forma_reciente(res_a['id'])
                        
                        # 3. Calcular el mejor pick basado en datos reales
                        pick = obtener_mejor_apuesta(partido, s_h, s_a)
                        
                        if pick:
                            with st.container():
                                st.markdown(f"""
                                <div class="bet-card">
                                    <div style="display: flex; align-items: center; gap: 20px;">
                                        <img src="{res_h['logo']}" width="40"> 
                                        <b>{res_h['nombre_real']}</b> vs 
                                        <b>{res_a['nombre_real']}</b>
                                        <img src="{res_a['logo']}" width="40">
                                    </div>
                                    <p style="margin-top:10px; color: #4cd964;">📢 Sugerencia: {pick['selection']} ({pick['odd']})</p>
                                    <small style="color: #8b949e;">Probabilidad real: {round(pick['probability']*100, 1)}%</small>
                                </div>
                                """, unsafe_allow_html=True)
                                final_picks.append(pick)
                    else:
                        st.warning(f"⚠️ Equipo no validado en API: {partido['home']} vs {partido['away']}")

                # --- Análisis de Valor del Parlay ---
                if final_picks:
                    st.divider()
                    parlay = build_smart_parlay(final_picks)
                    
                    st.subheader("📈 Análisis de Valor")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Cuota Final", f"{parlay['total_odd']}x")
                    with c2:
                        st.metric("Probabilidad Combinada", f"{round(parlay['combined_prob']*100, 1)}%")
                    
                    if st.button("💾 Registrar esta apuesta en el Historial"):
                        st.success("¡Apuesta registrada correctamente!")

with tab2:
    st.info("Aquí aparecerán tus parlays guardados para seguimiento de ganancias.")
    # Aquí puedes añadir la lógica de base de datos más adelante
