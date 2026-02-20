import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN DE IA (GEMINI) ---
# Sustituye con tu clave de Google AI Studio
genai.configure(api_key="TU_API_KEY_AQUÍ")
model = genai.GenerativeModel('gemini-1.5-flash')

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

# Datos de ejemplo (Esto debe venir de tu base de datos o CSV)
data = {
    'date': ['2026-02-20', '2026-02-20', '2026-02-20'],
    'game': ['Lakers vs Suns', 'Celtics vs Heat', 'Nuggets vs Warriors'],
    'stake': [50, 50, 40],
    'result': ['win', 'loss', 'win'], # 'win' o 'loss'
    'jugador': ['LeBron James', 'Jaylen Brown', 'Stephen Curry'],
    'linea': [24.5, 26.5, 28.5]
}
df = pd.DataFrame(data)

# --- CÁLCULO DE ROI (SOLUCIÓN AL ERROR TYPEERROR) ---
# Convertimos el resultado en ganancia real: si gana suma el 90%, si pierde resta el 100%
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
        
        # Formato para copiar a Telegram
        ticket_text = f"✅ *NBA ELITE PICK*\n🏀 {row['game']}\n🎯 {row['jugador']} Over {row['linea']}\n💰 Stake: {row['stake']} MXN"
        st.code(ticket_text, language="text")

st.subheader("📊 Historial Detallado")
st.dataframe(df, use_container_width=True)