"""
INVESTIGAR LIGAS - Busca códigos ESPN para ligas pendientes
"""
import streamlit as st
import requests

st.set_page_config(page_title="Investigar Ligas ESPN", page_icon="🔍", layout="wide")

st.title("🔍 Investigador de Códigos ESPN")
st.markdown("### Encuentra códigos para ligas pendientes")

def buscar_en_api(nombre_busqueda):
    """
    Intenta encontrar la liga en la API de ESPN
    """
    try:
        # Primero intentar con la API de búsqueda general
        url = f"https://site.web.api.espn.com/apis/search/v3?region=US&lang=en&q={nombre_busqueda}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def obtener_leagues_disponibles():
    """
    Obtiene lista de ligas disponibles de la API de RapidAPI
    """
    # Nota: Esto requiere API key de RapidAPI
    st.info("Para obtener la lista completa, necesitas una API key de RapidAPI")
    st.markdown("""
    1. Regístrate en https://rapidapi.com/
    2. Busca "ESPN Football Soccer" 
    3. Usa el endpoint /leagues
    """)

st.subheader("📋 Ligas Pendientes de Investigar")
ligas_pendientes = [
    "Mexico - Segunda Division",
    "Mexico - Liga MX U21",
    "Panama - Liga Prom",
    "Panama - Liga Panamena",
    "Copa Libertadores U20",
    "Costa Rica - Liga de Ascenso",
    "El Salvador - Reserve League",
    "Jamaica - Premier League",
    "Nicaragua - Nicaragua Cup",
    "Paraguay - Primera Division Reserves",
    "Argentina - Primera Division Reserves",
    "Argentina - Primera B Metropolitana",
    "Brasil - Copa do Nordeste",
    "Chile - Primera B",
    "Escocia - Championship",
    "Serie C",
    "Nacional",
    "Regionalliga",
]

for liga in ligas_pendientes:
    st.write(f"• {liga}")

st.markdown("---")
st.subheader("🔎 Buscador Manual")
busqueda = st.text_input("Nombre de la liga a buscar:")

if st.button("🔍 BUSCAR"):
    with st.spinner(f"Buscando {busqueda}..."):
        resultado = buscar_en_api(busqueda)
        if resultado:
            st.json(resultado)
        else:
            st.warning("No se encontraron resultados en la API de búsqueda")
            st.info("Prueba con estos patrones comunes:")
            st.code("""
            # Formatos típicos:
            - mexico.2
            - mex.2
            - mexico.u21
            - mex.u21
            - panama.1
            - pan.1
            - libertadores.u20
            - conmebol.libertadores.u20
            """)
