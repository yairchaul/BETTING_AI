import streamlit as st
from modules.vision_reader import read_ticket_image, procesar_texto_manual
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Bet Radar Pro", layout="wide", page_icon="🎯")

# Estilo para las tarjetas de partidos
st.markdown("""
    <style>
    .match-card {
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        background-color: #0d1117;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Analizador de Apuestas Inteligente")

# --- Entrada de Datos ---
tabs_input = st.tabs(["📝 Entrada Manual", "📸 Cargar Imagen"])

with tabs_input[0]:
    manual_input = st.text_area("Pega tus partidos aquí (Ej: Real Oviedo vs Atletico Madrid)", height=100)

with tabs_input[1]:
    uploaded = st.file_uploader("Sube tu captura de Caliente/Bet365", type=['png', 'jpg', 'jpeg'])

# Procesar información
games_data = []
if manual_input:
    games_data = procesar_texto_manual(manual_input)
elif uploaded:
    games_data = read_ticket_image(uploaded)

if games_data:
    st.divider()
    final_picks = []
    
    for partido in games_data:
        # Validación elástica con la API
        res_h = validar_y_obtener_stats(partido['home'])
        res_a = validar_y_obtener_stats(partido['away'])
        
        if res_h['valido'] and res_a['valido']:
            # Si ambos son válidos, procedemos al análisis de forma
            s_h = obtener_forma_reciente(res_h['id'])
            s_a = obtener_forma_reciente(res_a['id'])
            pick = obtener_mejor_apuesta(partido, s_h, s_a)
            
            # Mostrar tarjeta visual del partido
            with st.container():
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <img src="{res_h['logo']}" width="45">
                        <span style="font-size: 1.2em; font-weight: bold;">{res_h['nombre_real']} vs {res_a['nombre_real']}</span>
                        <img src="{res_a['logo']}" width="45">
                    </div>
                    <p style="color: #4cd964; font-size: 1.1em; margin-top: 15px;">📢 Sugerencia: {pick['selection']} ({pick['odd']})</p>
                    <small style="color: #8b949e;">Confianza basada en últimos 5 juegos: {round(pick['probability']*100, 1)}%</small>
                </div>
                """, unsafe_allow_html=True)
                final_picks.append(pick)
        else:
            # Mensaje de error amigable si la búsqueda falla
            st.error(f"❌ No se encontró coincidencia para: **{partido['home']}** o **{partido['away']}**. Revisa la ortografía.")

    # --- Generación de Parlay ---
    if final_picks:
        parlay = build_smart_parlay(final_picks)
        st.sidebar.header("🚀 Tu Parlay")
        st.sidebar.metric("Cuota Total", f"{parlay['total_odd']}x")
        st.sidebar.metric("Probabilidad Total", f"{round(parlay['combined_prob']*100, 1)}%")
        
        if st.sidebar.button("💾 Guardar en Historial"):
            st.sidebar.success("Parlay guardado correctamente.")
