# modules/tracker.py
import pandas as pd
import os
from datetime import datetime

def guardar_pick_automatico(juego_data, ev, stake):
    """
    Guarda el análisis de la IA en un archivo CSV para auditoría.
    """
    path = "data/picks.csv"
    
    # Asegurar que la carpeta data existe
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Crear la estructura de la nueva apuesta
    nueva_apuesta = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Evento": f"{juego_data['away']} @ {juego_data['home']}",
        "Linea": juego_data.get('total_line'),
        "Momio": juego_data.get('odds_over'),
        "EV": f"{ev*100:.2f}%",
        "Stake_Sugerido": f"${stake:,.2f}",
        "Estado": "Pendiente"
    }
    
    df_nuevo = pd.DataFrame([nueva_apuesta])
    
    # Si el archivo no existe, lo creamos con cabeceras
    if not os.path.exists(path):
        df_nuevo.to_csv(path, index=False)
    else:
        # Si ya existe, añadimos la fila al final
        df_nuevo.to_csv(path, mode='a', header=False, index=False)
