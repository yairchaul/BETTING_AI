import pandas as pd
import os
from datetime import datetime

def registrar_apuesta(partido, jugador, linea, prob, stake, status):
    archivo = 'historial_apuestas.csv'
    nueva_fila = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "partido": partido,
        "jugador": jugador,
        "linea": linea,
        "probabilidad": f"{prob*100:.1f}%",
        "stake_mxn": stake,
        "status_ia": status,
        "resultado": "PENDIENTE" # Se actualizará manualmente o por API después
    }
    
    df = pd.DataFrame([nueva_fila])
    
    # Si ya existe el archivo, lo cargamos y añadimos la fila
    if os.path.exists(archivo):
        df_historico = pd.read_csv(archivo)
        df_final = pd.concat([df_historico, df], ignore_index=True)
    else:
        df_final = df
        
    df_final.to_csv(archivo, index=False)
