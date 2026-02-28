import streamlit as st
from modules.vision_reader import read_ticket_image, procesar_texto_manual
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta

st.set_page_config(page_title="Analizador de Apuestas Pro", layout="wide")

st.markdown("""
    <style>
    .card { background-color: #0d1117; padding: 15px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 10px; }
    .status-ok { color: #4cd964; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Analizador de Apuestas Inteligente")

tab_manual, tab_img = st.tabs(["📝 Entrada Manual", "📸 Cargar Imagen"])

with tab_manual:
    input_text = st.text_area("Pega tus partidos aquí:", placeholder="Ej: PSG vs Le Havre", height=120)

with tab_img:
    file = st.file_uploader("Sube tu captura de pantalla", type=['png', 'jpg', 'jpeg'])

raw_games = []
if input_text:
    raw_games = procesar_texto_manual(input_text)
elif file:
    raw_games = read_ticket_image(file)

if raw_games:
    st.subheader("📋 Resultados del Análisis")
    for g in raw_games:
        with st.spinner(f"Analizando {g['home']} vs {g['away']}..."):
            res_h = validar_y_obtener_stats(g['home'])
            res_a = validar_y_obtener_stats(g['away'])
            
            if res_h['valido'] and res_a['valido']:
                sh = obtener_forma_reciente(res_h['id'])
                sa = obtener_forma_reciente(res_a['id'])
                pick = obtener_mejor_apuesta(g, sh, sa)
                
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <img src="{res_h['logo']}" width="35">
                        <span class="status-ok">✔</span>
                        <b>{res_h['nombre_real']}</b> vs <b>{res_a['nombre_real']}</b>
                        <img src="{res_a['logo']}" width="35">
                    </div>
                    <div style="margin-left: 55px; margin-top: 10px;">
                        <span>📢 <b>Sugerencia:</b> {pick['selection']}</span><br>
                        <small style="color: #8b949e;">Confianza: {round(pick['probability']*100, 1)}%</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ No se encontró coincidencia para: **{g['home']}** o **{g['away']}**.")
