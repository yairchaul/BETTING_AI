import streamlit as st
from modules.vision_reader import read_ticket_image, procesar_texto_manual
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Detector Pro", layout="wide")

st.title("🎯 Detector de Apuestas")

# --- Sección de Entrada Mixta ---
st.info("💡 Puedes subir una imagen o simplemente pegar los nombres de los equipos abajo.")
c_input, c_upload = st.columns(2)

with c_input:
    manual_text = st.text_area("Pegar equipos (Ej: Real Madrid vs Barcelona)", height=100)

with c_upload:
    uploaded = st.file_uploader("O sube la captura de Caliente", type=['png', 'jpg', 'jpeg'])

# Prioridad al texto manual si el usuario escribió algo
games_data = []
if manual_text:
    games_data = procesar_texto_manual(manual_text)
elif uploaded:
    games_data = read_ticket_image(uploaded)

if games_data:
    final_picks = []
    st.divider()
    
    for partido in games_data:
        # Validación visual con logos
        res_h = validar_y_obtener_stats(partido['home'])
        res_a = validar_y_obtener_stats(partido['away'])
        
        if res_h['valido'] and res_a['valido']:
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(res_h['logo'], width=40)
                    st.image(res_a['logo'], width=40)
                with col2:
                    st.write(f"**{res_h['nombre_real']} vs {res_a['nombre_real']}**")
                    
                    # Análisis real basado en historial
                    s_h = obtener_forma_reciente(res_h['id'])
                    s_a = obtener_forma_reciente(res_a['id'])
                    pick = obtener_mejor_apuesta(partido, s_h, s_a)
                    
                    if pick:
                        st.success(f"Sugerencia: {pick['selection']} ({pick['odd']})")
                        final_picks.append(pick)
        else:
            st.warning(f"⚠️ No pude encontrar a: {partido['home']} o {partido['away']} en la base de datos.")

    if final_picks:
        parlay = build_smart_parlay(final_picks)
        st.sidebar.title("🚀 Parlay Sugerido")
        st.sidebar.metric("Cuota", f"{parlay['total_odd']}x")
        st.sidebar.metric("Probabilidad", f"{round(parlay['combined_prob']*100, 1)}%")
