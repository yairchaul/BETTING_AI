import pandas as pd
import os
from datetime import datetime

def guardar_pick_automatico(juego_data, ev, stake):
    """
    Guarda el análisis de la IA en un archivo CSV para auditoría.
    """
    path = "data/picks.csv"
    
    # 1. Asegurar que la carpeta data existe automáticamente
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # 2. Extraer datos con nombres flexibles (para evitar errores si la IA cambia una palabra)
    # Buscamos 'total' o 'handicap', y 'moneyline' o 'momio'
    linea_detectada = juego_data.get('total', juego_data.get('handicap', 'N/A'))
    momio_detectado = juego_data.get('moneyline', juego_data.get('odds_over', 'N/A'))
    
    # 3. Crear la estructura de la nueva apuesta
    nueva_apuesta = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Evento": f"{juego_data.get('away', 'Visitante')} @ {juego_data.get('home', 'Local')}",
        "Linea": linea_detectada,
        "Momio": momio_detectado,
        "EV": f"{ev*100:.2f}%",
        "Stake_Sugerido": f"${stake:,.2f}",
        "Estado": "Pendiente"
    }
    
    df_nuevo = pd.DataFrame([nueva_apuesta])
    
    # 4. Guardado seguro
    try:
        if not os.path.exists(path):
            df_nuevo.to_csv(path, index=False, encoding='utf-8')
        else:
            df_nuevo.to_csv(path, mode='a', header=False, index=False, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error al guardar CSV: {e}")
        return False

