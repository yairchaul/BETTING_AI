"""
DEBUG MONEYLINE - Muestra exactamente dónde están las cuotas
"""
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Debug Moneyline NBA", page_icon="💰", layout="wide")

st.title("💰 Debug Moneyline NBA")
st.markdown("### Ver dónde están las cuotas en la API")

fecha = datetime.now().strftime("%Y%m%d")
url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={fecha}&limit=100"

if st.button("🔍 CONSULTAR API"):
    with st.spinner("Consultando ESPN..."):
        response = requests.get(url, timeout=10)
        st.write(f"**Status code:** {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('events') and len(data['events']) > 0:
                event = data['events'][0]
                competition = event['competitions'][0]
                
                st.subheader("📋 Estructura de odds")
                if 'odds' in competition:
                    odds = competition['odds'][0]
                    
                    # Mostrar todas las keys disponibles
                    st.write("**Keys en odds:**", list(odds.keys()))
                    
                    # Mostrar homeTeamOdds
                    if 'homeTeamOdds' in odds:
                        st.write("**homeTeamOdds:**", odds['homeTeamOdds'])
                    
                    # Mostrar awayTeamOdds
                    if 'awayTeamOdds' in odds:
                        st.write("**awayTeamOdds:**", odds['awayTeamOdds'])
                    
                    # Mostrar moneyline
                    if 'moneyline' in odds:
                        st.write("**moneyline:**", odds['moneyline'])
                    
                    # Mostrar todo el objeto odds
                    st.subheader("📊 Objeto odds completo")
                    st.json(odds)
                else:
                    st.warning("No hay odds en este evento")
            else:
                st.warning("No hay eventos para hoy")
        else:
            st.error(f"Error {response.status_code}")
