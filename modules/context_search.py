import requests
import streamlit as st

def get_team_context(team_name):
    api_key = st.secrets["GOOGLE_API_KEY"]
    cse_id = st.secrets["GOOGLE_CSE_ID"]
    # Agregamos operadores de búsqueda para mayor efectividad en sitios deportivos
    query = f"{team_name} (lesiones OR bajas OR alineación) site:espn.com OR site:soccerway.com"
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}"
    
    try:
        response = requests.get(url).json()
        items = response.get('items', [])
        if not items: return "No se encontraron noticias recientes críticas."
        return " ".join([item['snippet'] for item in items[:2]])
    except:
        return "Error de conexión con el motor de búsqueda."

def analyze_context(context_text):
    context_text = context_text.lower()
    factors = {"bajas": False}
    # Diccionario de palabras clave para detectar riesgos
    keywords = ["baja", "lesion", "duda", "suspendido", "roja", "ausente", "fuera"]
    if any(word in context_text for word in keywords):
        factors["bajas"] = True
    return factors
