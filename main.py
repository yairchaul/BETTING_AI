import streamlit as st
from modules.vision_reader import read_ticket_image, procesar_texto_manual
from modules.cerebro import validar_y_obtener_stats, obtener_forma_reciente, obtener_mejor_apuesta

st.set_page_config(page_title="Bet Radar Pro", layout="wide")

# Estilos CSS para emular la interfaz de tu imagen
st.markdown("""
    <style>
    .match-card {
        background-color: #0d1117;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    .check-icon { color: #4cd964; margin-right: 10px; }
    .pick-title { font-weight: bold; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Analizador de Apuestas Inteligente")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("📥 Entrada de Datos")
    manual = st.text_area("✍️ Pega tus equipos:", placeholder="Ej: PSG vs Le Havre", height=120)
    archivo = st.file_uploader("📸 O sube la captura de Caliente", type=['png', 'jpg', 'jpeg'])

# Obtener partidos de cualquiera de las fuentes
partidos_detectados = []
if manual:
    partidos_detectados = procesar_texto_manual(manual)
elif archivo:
    partidos_detectados = read_ticket_image(archivo)

with col_right:
    st.subheader("📋 Selecciones Recomendadas")
    if partidos_detectados:
        picks_parlay = []
        for p in partidos_detectados:
            with st.spinner(f"Analizando {p['home']}..."):
                res_h = validar_y_obtener_stats(p['home'])
                res_a = validar_y_obtener_stats(p['away'])
                
                if res_h['valido'] and res_a['valido']:
                    sh = obtener_forma_reciente(res_h['id'])
                    sa = obtener_forma_reciente(res_a['id'])
                    pick = obtener_mejor_apuesta(p, sh, sa)
                    
                    # Mostrar tarjeta estilo la imagen que subiste
                    st.markdown(f"""
                    <div class="match-card">
                        <span class="check-icon">✅</span>
                        <span class="pick-title">{res_h['nombre_real']} vs {res_a['nombre_real']}</span>
                        <div style="margin-left: 30px; margin-top: 5px;">
                            <span>{pick['selection']} ({pick['odd']})</span><br>
                            <small style="color: #8b949e;">Confianza: {round(pick['probability']*100, 1)}%</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    picks_parlay.append(pick)
                else:
                    st.warning(f"⚠️ No se encontró: {p['home']} o {p['away']}. Intenta nombres cortos.")
        
        # Resumen del Parlay (Análisis de Valor)
        if picks_parlay:
            st.divider()
            st.markdown("### 📈 Análisis de Valor")
            prob_total = 1.0
            for pk in picks_parlay: prob_total *= pk['probability']
            
            st.metric("Cuota Final Estimada", f"{round(1.85**len(picks_parlay), 2)}x")
            st.metric("Probabilidad Combinada", f"{round(prob_total*100, 1)}%")
    else:
        st.info("Esperando datos para iniciar el análisis...")
