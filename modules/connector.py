import streamlit as st
import requests

def obtener_datos_caliente_limpios():
    # Usamos try/except para capturar el error exacto
    try:
        API_KEY = st.secrets["ODDS_API_KEY"]
        # Simplificamos a mercados básicos para asegurar que traiga ALGO
        url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={API_KEY}&regions=us&markets=h2h,totals&oddsFormat=american"
        
        response = requests.get(url)
        
        if response.status_code == 401:
            st.error("🔑 Error: Tu API Key de Odds API es inválida.")
            return []
            
        data = response.json()
        
        if not data:
            st.warning("⚠️ La API respondió pero no hay partidos disponibles ahora.")
            return []
            
        return data # Retorna la lista de partidos
        
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return []
