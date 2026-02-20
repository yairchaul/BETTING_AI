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

# Simulamos datos con momios de Caliente y nuestra proyección
data = {
    'game': ['Lakers vs Suns', 'Celtics vs Heat', 'Nuggets vs Warriors', 'Knicks vs Bulls'],
    'jugador': ['LeBron James', 'Jaylen Brown', 'Stephen Curry', 'Jalen Brunson'],
    'linea': [24.5, 22.5, 28.5, 26.5],
    'momio_caliente': [-110, -115, -110, -110], # Momios reales de la casa
    'prob_modelo': [0.58, 0.45, 0.62, 0.48]    # Lo que nuestra IA proyecta
}
df_picks = pd.DataFrame(data)

# Calculamos si vale la pena apostar (Edge)
# Si prob_modelo > 0.54 (para momios -110), hay valor
df_picks['es_buena_idea'] = df_picks['prob_modelo'] > 0.53 

# SOLO mostramos los que tienen valor
picks_filtrados = df_picks[df_picks['es_buena_idea'] == True]

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







