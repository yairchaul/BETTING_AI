import streamlit as st
from modules.vision_reader import read_ticket_image, procesar_texto_manual
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Detector Pro", layout="wide")

st.title("🎯 Detector de Apuestas")

# --- NUEVA SECCIÓN: ENTRADA MANUAL ---
st.subheader("📝 Entrada de Partidos")
col_input, col_img = st.columns(2)

with col_input:
    texto_manual = st.text_area("Pega aquí los partidos (Ej: Kasimpasa vs Caykur Rizespor)", placeholder="Kasimpasa vs Caykur Rizespor\nEquipo C vs Equipo D")

with col_img:
    uploaded = st.file_uploader("O sube tu captura", type=['png', 'jpg', 'jpeg'])

# Lógica de detección: Manual tiene prioridad si existe texto
games_data = []
if texto_manual:
    games_data = procesar_texto_manual(texto_manual)
elif uploaded:
    games_data = read_ticket_image(uploaded)

if games_data:
    final_picks = []
    st.divider()
    
    for partido in games_data:
        # Validación con API (logos y IDs)
        with st.status(f"Analizando: {partido['home']} vs {partido['away']}...", expanded=False):
            res_h = validar_y_obtener_stats(partido['home'])
            res_a = validar_y_obtener_stats(partido['away'])
            
            if res_h['valido'] and res_a['valido']:
                # Extraer goles reales últimos 5 partidos de la API
                s_h = obtener_forma_reciente(res_h['id'])
                s_a = obtener_forma_reciente(res_a['id'])
                
                pick = obtener_mejor_apuesta(partido, s_h, s_a)
                
                if pick:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(res_h['logo'], width=40)
                        st.write(f"**{res_h['nombre_real']}**")
                        st.image(res_a['logo'], width=40)
                        st.write(f"**{res_a['nombre_real']}**")
                    with col2:
                        st.success(f"Pick: {pick['selection']}")
                        st.info(f"Probabilidad (Últimos 5 juegos): {round(pick['probability']*100, 1)}%")
                    final_picks.append(pick)
            else:
                st.error(f"❌ La API no encontró a: {partido['home']} o {partido['away']}. Revisa la ortografía.")

    if final_picks:
        parlay = build_smart_parlay(final_picks)
        st.sidebar.header("🚀 Parlay Sugerido")
        st.sidebar.metric("Cuota Total", f"{parlay['total_odd']}x")
        st.sidebar.metric("Probabilidad", f"{round(parlay['combined_prob']*100, 1)}%")
