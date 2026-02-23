import streamlit as st
import os
import requests

# =========================================================
# 🔐 OBTENER API KEYS SEGURAS
# =========================================================
def get_gemini_key():
    """Obtiene la llave de Gemini de secrets o entorno"""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        return os.getenv("GEMINI_API_KEY")

def get_odds_api_key():
    """Obtiene la llave de The Odds API"""
    try:
        return st.secrets["ODDS_API_KEY"]
    except:
        return os.getenv("ODDS_API_KEY")

# =========================================================
# 📡 THE ODDS API (DATOS REALES EN TIEMPO REAL)
# =========================================================
def get_real_time_odds(sport="basketball_nba"):
    """
    Consulta momios reales para validar lo detectado por la IA.
    """
    api_key = get_odds_api_key()
    if not api_key:
        return None

    # URL para momios de NBA (puedes cambiar la región a 'us' o 'eu' para Caliente)
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    
    params = {
        'apiKey': api_key,
        'regions': 'us', # Las casas mexicanas suelen seguir líneas de Las Vegas
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error en The Odds API: {e}")
        return []

# =========================================================
# 🧪 TEST DE CONEXIÓN GLOBAL
# =========================================================
def test_connection():
    results = []
    
    # Test Gemini
    if get_gemini_key():
        results.append("✅ Gemini API: Conectado")
    else:
        results.append("❌ Gemini API: Error")
        
    # Test Odds API
    if get_odds_api_key():
        results.append("✅ Odds API: Conectado")
    else:
        results.append("❌ Odds API: Error")
        
    return " | ".join(results)

