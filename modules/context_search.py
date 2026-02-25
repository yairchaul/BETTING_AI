import requests
import streamlit as st

def get_team_context(team_name):
    """Busca bajas, lesiones y noticias recientes del equipo."""
    api_key = st.secrets["GOOGLE_API_KEY"]
    cse_id = st.secrets["GOOGLE_CSE_ID"]
    query = f"{team_name} alineación lesiones noticias recientes"
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}"
    
    try:
        response = requests.get(url).json()
        snippets = [item['snippet'] for item in response.get('items', [])[:3]]
        return " ".join(snippets).lower()
    except:
        return ""

def analyze_context(context_text):
    """Extrae factores de riesgo del texto encontrado."""
    factors = {"bajas": False, "rotacion": False, "motivacion": "normal"}
    keywords_bajas = ["lesión", "fuera", "baja", "duda", "suspendido", "lesionado", "ausente"]
    
    if any(word in context_text for word in keywords_bajas):
        factors["bajas"] = True
    if "suplentes" in context_text or "rotación" in context_text:
        factors["rotacion"] = True
    return factors
