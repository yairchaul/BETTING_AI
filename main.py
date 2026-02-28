import streamlit as st
from modules.vision_reader import read_ticket_image, procesar_texto_manual
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Analizador de Apuestas", layout="wide", page_icon="🎯")

st.markdown("""
    <style>
    .match-card {
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 12px;
        background-color: #0d1117;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Analizador de Apuestas Pro")

# --- Tabs de Entrada ---
tab_manual, tab_img = st.tabs(["📝 Entrada Manual", "📸 Cargar Imagen"])

with tab_manual:
    manual_input = st.text_area("Pega los partidos (Ej: Cambaceres vs Argentino De Rosario)", height=100)

with tab_img:
    uploaded = st.file_uploader("Sube tu captura", type=['png', 'jpg', 'jpeg'])

# Procesar datos
games_data = []
if manual_input:
    games_data = procesar_texto_manual(manual_input)
elif uploaded:
    games_data = read_ticket_image(uploaded)

if games_data:
    st.subheader("🔍 Resultados del Análisis")
    final_picks = []
    
    for partido in games_data:
        # Validación Inteligente
        res_h = validar_y_obtener_stats(partido['home'])
        res_a = validar_y_obtener_stats(partido['away'])
        
        if res_h['valido'] and res_a['valido']:
            sh = obtener_forma_reciente(res_h['id'])
            sa = obtener_forma_reciente(res_a['id'])
            pick = obtener_mejor_apuesta(partido, sh, sa)
            
            with st.container():
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <img src="{res_h['logo']}" width="40">
                        <b>{res_h['nombre_real']}</b> vs <b>{res_a['nombre_real']}</b>
                        <img src="{res_a['logo']}" width="40">
                    </div>
                    <p style="color: #4cd964; margin-top: 10px;">📢 Pick: {pick['selection']} | Probabilidad: {round(pick['probability']*100, 1)}%</p>
                </div>
                """, unsafe_allow_html=True)
                final_picks.append(pick)
        else:
            # Sugerencia inteligente si falla
            st.error(f"❌ No se encontró: **{partido['home']}** o **{partido['away']}**. Prueba escribiendo solo la ciudad o el nombre principal.")

    if final_picks:
        parlay = build_smart_parlay(final_picks)
        st.sidebar.header("🚀 Parlay Sugerido")
        st.sidebar.metric("Cuota Final", f"{parlay['total_odd']}x")
        st.sidebar.metric("Probabilidad Combinada", f"{round(parlay['combined_prob']*100, 1)}%")
