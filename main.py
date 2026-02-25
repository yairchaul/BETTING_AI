import streamlit as st
from modules.vision_reader import analizar_ticket
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Auditor de Valor", layout="wide")

st.markdown("""
<style>
.card { background:#1a2c3d; padding:20px; border-left:5px solid #1E88E5; border-radius:10px; margin-bottom:15px; }
</style>
""", unsafe_allow_html=True)

st.title("🔥 Auditor de Valor IA - Fútbol")

engine = EVEngine()

# Opción 1: Imagen o texto pegado
st.subheader("Analizar ticket (imagen o texto)")
col1, col2 = st.columns(2)
with col1:
    archivo = st.file_uploader("Sube captura del ticket", type=["png", "jpg", "jpeg"])
with col2:
    texto_manual = st.text_area("O pega el texto del ticket aquí", height=200)

texto_a_analizar = ""
if archivo is not None:
    # En Cloud real usaríamos OCR, por ahora simulamos con nombre del archivo o texto manual
    texto_a_analizar = texto_manual or "Texto de imagen subida"
elif texto_manual:
    texto_a_analizar = texto_manual

if texto_a_analizar:
    partidos = analizar_ticket(texto_a_analizar)
    if partidos:
        st.success(f"Detectados {len(partidos)} partidos")
        for p in partidos:
            resultado = engine.analizar_partido(p)
            if resultado:
                st.markdown(f"""
                <div class="card">
                    <h3>{resultado['home']} vs {resultado['away']}</h3>
                    <p><strong>Mejor opción:</strong> {resultado['mejor_pick']}</p>
                    <p>Probabilidad: {resultado['prob']}% | EV: {resultado['ev']}</p>
                    <small>λ Home: {resultado['λ_home']} | λ Away: {resultado['λ_away']} | Edge: {resultado['edge']}%</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No se detectaron partidos en el texto. Intenta copiar más texto del ticket.")

# Botón para live scraping (mantener tu conector actual)
if st.button("Analizar Caliente.mx en vivo"):
    from modules.connector import get_live_data
    from modules.autopicks import generar_picks_auto
    st.write(generar_picks_auto())

st.caption("Sistema global • Cascada con combos • Poisson real • Sin equipos hardcodeados")
