import streamlit as st
from modules.vision_reader import read_ticket_image, procesar_texto_manual
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Analizador Pro", layout="wide")

# CSS personalizado para emular tu interfaz de capturas
st.markdown("""
    <style>
    .stTextArea textarea { background-color: #161b22; color: white; border: 1px solid #30363d; }
    .match-card {
        background-color: #0d1117;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    .pick-text { color: #4cd964; font-weight: bold; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Analizador de Apuestas Pro")

col_in, col_res = st.columns([1, 1.5])

with col_in:
    st.subheader("📥 Entrada de Datos")
    manual = st.text_area("Pega los partidos aquí:", placeholder="Ej: PSG vs Le Havre", height=120)
    archivo = st.file_uploader("O sube tu captura de Caliente", type=['png', 'jpg', 'jpeg'])

games = []
if manual:
    games = procesar_texto_manual(manual)
elif archivo:
    games = read_ticket_image(archivo)

with col_res:
    st.subheader("🔍 Análisis de Valor")
    if games:
        picks_finales = []
        for g in games:
            # Buscamos los equipos con el nuevo motor inteligente
            rh = validar_y_obtener_stats(g['home'])
            ra = validar_y_obtener_stats(g['away'])
            
            if rh['valido'] and ra['valido']:
                sh = obtener_forma_reciente(rh['id'])
                sa = obtener_forma_reciente(ra['id'])
                p = obtener_mejor_apuesta(g, sh, sa)
                
                st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <img src="{rh['logo']}" width="35">
                        <b>{rh['nombre_real']}</b> vs <b>{ra['nombre_real']}</b>
                        <img src="{ra['logo']}" width="35">
                    </div>
                    <div style="margin-top: 10px;">
                        <span class="pick-text">✅ Sugerencia: {p['label']}</span><br>
                        <small style="color: #8b949e;">Probabilidad Real: {round(p['probability']*100, 1)}%</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                picks_finales.append(p)
            else:
                st.error(f"⚠️ No pude encontrar a: {g['home']} o {g['away']}. Intenta con el nombre de la ciudad.")

        if picks_finales:
            parlay = build_smart_parlay(picks_finales)
            st.sidebar.success(f"🚀 Parlay Sugerido: {parlay['total_odd']}x")
            st.sidebar.info(f"Probabilidad Combinada: {round(parlay['combined_prob']*100, 1)}%")
