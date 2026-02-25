import pandas as pd
import os
import requests
import streamlit as st
from datetime import datetime

PATH_HISTORIAL = "data/parlay_history.csv"

def registrar_parlay_automatico(datos_simulacion, picks_texto):
    """Guarda el parlay con los cálculos corregidos."""
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

def actualizar_resultados_api():
    """Consulta Odds API para cerrar apuestas pendientes automáticamente."""
    if not os.path.exists(PATH_HISTORIAL): return
    
    df = pd.read_csv(PATH_HISTORIAL)
    pendientes = df[df['Estado'] == "Pendiente"]
    
    if not pendientes.empty:
        try:
            api_key = st.secrets["ODDS_API_KEY"]
            # Endpoint para obtener resultados (scores) de partidos finalizados
            url = f"https://api.the-odds-api.com/v4/sports/soccer/scores/?apiKey={api_key}&daysFrom=3"
            response = requests.get(url)
            
            if response.status_code == 200:
                scores = response.json()
                # Aquí la lógica compararía cada pick con el score['completed'] == True
                # Por ahora, notificamos la conexión exitosa
                st.sidebar.caption("✅ Sincronizado con Odds API")
        except Exception as e:
            st.sidebar.warning("⚠️ Odds API: Revisar conexión o Key")
    
    df.to_csv(PATH_HISTORIAL, index=False)
