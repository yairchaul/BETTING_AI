import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# Usamos la etiqueta "GEMINI_API_KEY" que configuraste en los Secrets de Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error al configurar la API Key de Gemini. Verifica tus Secrets.")

def obtener_analisis_ia(partido, jugador, linea):
    prompt = f"Analiza brevemente por qué el Over de {linea} para {jugador} en {partido} es buena idea. Sé muy breve."
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "IA analizando tendencias..."

# --- INTERFAZ ---
st.set_page_config(page_title="NBA Dashboard Pro", layout="wide")
st.title("🏀 NBA +EV Dashboard v12")

# Datos de ejemplo
data = {
    'date': ['2026-02-20', '2026-02-20', '2026-02-20'],
    'game': ['Lakers vs Suns', 'Celtics vs Heat', 'Nuggets vs Warriors'],
    'stake': [50, 50, 40],
    'result': ['win', 'loss', 'win'], 
    'jugador': ['LeBron James', 'Jaylen Brown', 'Stephen Curry'],
    'linea': [24.5, 26.5, 28.5]
}
df = pd.DataFrame(data)

# --- CÁLCULO DE ROI (CORRECCIÓN TYPEERROR) ---
# Evitamos el error de la imagen 17db93 convirtiendo resultados a números
df['ganancia_mxn'] = df.apply(lambda r: r['stake'] * 0.9 if r['result'] == 'win' else -r['stake'], axis=1)

total_ganado = df['ganancia_mxn'].sum()
total_apostado = df['stake'].sum()
roi_calculado = (total_ganado / total_apostado) * 100 if total_apostado > 0 else 0

# --- MÉTRICAS ---
col1, col2, col3 = st.columns(3)
col1.metric("Balance Total", f"{total_ganado:.2f} MXN", delta=f"{total_ganado}")
col2.metric("ROI del Sistema", f"{roi_calculado:.2f}%")
col3.metric("Apuestas Totales", len(df))

st.divider()

# --- GENERADOR DE TICKETS E IA ---
st.subheader("🔥 Picks del Día y Análisis de IA")
for i, row in df.iterrows():
    with st.expander(f"📌 Ticket: {row['game']}"):
        st.write(f"**Análisis IA:** {obtener_analisis_ia(row['game'], row['jugador'], row['linea'])}")
        
        ticket_text = f"✅ *NBA ELITE PICK*\n🏀 {row['game']}\n🎯 {row['jugador']} Over {row['linea']}\n💰 Stake: {row['stake']} MXN"
        st.code(ticket_text, language="text")

st.subheader("📊 Historial Detallado")
st.dataframe(df, use_container_width=True)






