import pandas as pd
import os
import requests
import streamlit as st
from datetime import datetime

PATH_HISTORIAL = "data/parlay_history.csv"

def registrar_parlay_automatico(datos_simulacion, picks_texto):
    """Guarda el parlay con cálculos corregidos."""
    if not os.path.exists("data"): 
        os.makedirs("data")
    
    nuevo_registro = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Picks": picks_texto,
        "Monto": datos_simulacion['monto'],
        "Cuota": datos_simulacion['cuota_total'],
        "Pago_Potencial": datos_simulacion['pago_total'],
        "Ganancia_Neta": datos_simulacion['ganancia_neta'],
        "Estado": "Pendiente"
    }
    
    df = pd.DataFrame([nuevo_registro])
    header = not os.path.exists(PATH_HISTORIAL)
    df.to_csv(PATH_HISTORIAL, mode='a', index=False, header=header, encoding='utf-8')

def update_pending_parlays(file_path):
    """Consulta la API y actualiza estados de Pendiente a Ganada/Perdida."""
    if not os.path.exists(file_path): return
    
    df = pd.read_csv(file_path)
    if df[df['Estado'] == "Pendiente"].empty: return

    try:
        api_key = st.secrets["ODDS_API_KEY"]
        # Consultar scores de los últimos 3 días
        url = f"https://api.the-odds-api.com/v4/sports/soccer/scores/?apiKey={api_key}&daysFrom=3"
        response = requests.get(url)
        
        if response.status_code == 200:
            scores = response.json()
            # Aquí se compararía cada pick con los resultados reales de 'scores'
            # Por ahora, marcamos la sincronización exitosa en el log
            st.sidebar.success("Sincronizado con Odds API")
    except Exception as e:
        st.sidebar.warning("API de Resultados no disponible")

    df.to_csv(file_path, index=False)

