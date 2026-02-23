# En autopicks.py

# Opción 1: Import correcto (recomendada)
from modules.connector import get_live_data

def generar_picks_auto():
    data = get_live_data()  # Llama a la función real que scrapea Caliente.mx
    # Aquí puedes procesar data para generar picks
    # Por ejemplo:
    # picks = procesar_eventos(data)  # tu lógica futura
    return data if data else []  # Devuelve lista vacía si no hay datos
