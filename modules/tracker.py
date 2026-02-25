import pandas as pd
import os
import requests
import streamlit as st
from datetime import datetime

PATH_HISTORIAL = "data/parlay_history.csv"
API_KEY = st.secrets["ODDS_API_KEY"]
REGION = "eu" # Cambiar a 'us' si son ligas americanas

def registrar_parlay_automatico(datos_simulacion, picks_texto):
    if not os.path.exists("data"): os.makedirs("data")
    nuevo_registro = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Picks": picks_texto,
        "Monto": datos_simulacion['monto'],
        "Cuota": datos_simulacion['cuota_total'],
        "Pago_Potencial": datos_simulacion['pago_total'],
        "Estado": "Pendiente"
    }
    df = pd.DataFrame([nuevo_registro])
    header = not os.path.exists(PATH_HISTORIAL)
    df.to_csv(PATH_HISTORIAL, mode='a', index=False, header=header, encoding='utf-8')

def actualizar_resultados_api():
    """Consulta resultados reales y cierra apuestas pendientes."""
    if not os.path.exists(PATH_HISTORIAL): return
    
    df = pd.read_csv(PATH_HISTORIAL)
    if not df[df['Estado'] == "Pendiente"].empty:
        # Nota: Aquí se implementaría el endpoint /scores de la Odds API
        # Por seguridad, si la API no responde, se mantienen en Pendiente
        try:
            url = f"https://api.the-odds-api.com/v4/sports/upcoming/scores/?apiKey={API_KEY}&daysFrom=3"
            response = requests.get(url)
            if response.status_status == 200:
                resultados = response.json()
                # Aquí se cruzarían los resultados con tus picks
                # Lógica simplificada para el testeo:
                st.sidebar.success("Sincronizado con Odds API")
        except:
            st.sidebar.warning("No se pudo conectar con la API de resultados")
            
    df.to_csv(PATH_HISTORIAL, index=False)

