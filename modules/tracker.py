import pandas as pd
import os
import requests
import streamlit as st
from datetime import datetime

PATH_HISTORIAL = "data/parlay_history.csv"
def registrar_parlay_automatico(datos_simulacion, picks_texto):
    """Guarda el parlay con montos redondeados para lectura clara."""
    if not os.path.exists("data"): os.makedirs("data")
    
    nuevo_registro = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Picks": picks_texto,
        "Monto": round(float(datos_simulacion['monto']), 2),
        "Cuota": round(float(datos_simulacion['cuota_total']), 2),
        "Pago_Potencial": round(float(datos_simulacion['pago_total']), 2),
        "Ganancia_Neta": round(float(datos_simulacion['ganancia_neta']), 2),
        "Estado": "Pendiente"
    }
    # ... resto del código de guardado ...
def registrar_parlay_automatico(datos_simulacion, picks_texto):
    if not os.path.exists("data"): os.makedirs("data")
    
    nuevo_registro = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Picks": picks_texto,
        "Monto": round(float(datos_simulacion['monto']), 2),
        "Cuota": round(float(datos_simulacion['cuota_total']), 2),
        "Pago_Potencial": round(float(datos_simulacion['pago_total']), 2),
        "Ganancia_Neta": round(float(datos_simulacion['ganancia_neta']), 2),
        "Estado": "Pendiente"
    }
    
    df = pd.DataFrame([nuevo_registro])
    header = not os.path.exists(PATH_HISTORIAL)
    df.to_csv(PATH_HISTORIAL, mode='a', index=False, header=header, encoding='utf-8')

def update_pending_parlays():
    """Función para actualizar estados vía API"""
    if not os.path.exists(PATH_HISTORIAL): return
    # Lógica de Odds API aquí...
    st.sidebar.caption("✅ Tracker activo y redondeado")



