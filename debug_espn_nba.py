"""
DEBUG ESPN NBA - Muestra la respuesta cruda de la API
"""
import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Debug ESPN NBA", page_icon="🔍", layout="wide")

st.title("🔍 Debug ESPN NBA")
st.markdown("### Ver la respuesta cruda de la API")

fecha = datetime.now().strftime("%Y%m%d")
url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={fecha}&limit=100"

st.write(f"**URL consultada:** `{url}`")

if st.button("🔍 CONSULTAR API"):
    with st.spinner("Consultando ESPN..."):
        try:
            response = requests.get(url, timeout=10)
            st.write(f"**Status code:** {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                st.subheader("📊 Estructura de la respuesta")
                st.write(f"Keys principales: {list(data.keys())}")
                
                eventos = data.get('events', [])
                st.write(f"**Eventos encontrados:** {len(eventos)}")
                
                if eventos:
                    # Mostrar el primer evento completo
                    st.subheader("📋 Primer evento (completo)")
                    st.json(eventos[0])
                    
                    # Extraer odds del primer evento
                    if 'competitions' in eventos[0] and len(eventos[0]['competitions']) > 0:
                        competition = eventos[0]['competitions'][0]
                        if 'odds' in competition:
                            st.subheader("💰 Odds encontrados")
                            st.json(competition['odds'])
                        else:
                            st.warning("⚠️ No se encontraron odds en este evento")
                            
                            # Buscar en otra ubicación
                            if 'competitors' in competition:
                                for comp in competition['competitors']:
                                    if 'statistics' in comp:
                                        st.write(f"Estadísticas de {comp['team']['displayName']}:")
                                        st.json(comp['statistics'])
                else:
                    st.warning("No hay eventos para hoy")
            else:
                st.error(f"Error {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.markdown("### 📋 Si la API no devuelve odds, el programa usará datos de ejemplo")
