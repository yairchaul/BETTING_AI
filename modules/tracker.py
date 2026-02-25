import pandas as pd
import os
import datetime

FILE_PATH = "parlay_history.csv"

def registrar_parlay_automatico(sim, picks_txt):
    """Guarda el parlay con las columnas exactas que requiere el Sidebar."""
    nuevo_registro = {
        "Fecha": datetime.datetime.now().strftime("%d/%m %H:%M"),
        "monto": float(sim.get('monto', 0)),
        "cuota_total": float(sim.get('cuota_total', 0)),
        "ganancia_neta": float(sim.get('ganancia_neta', 0)),
        "picks": picks_txt
    }
    
    df = pd.DataFrame([nuevo_registro])
    header = not os.path.exists(FILE_PATH)
    df.to_csv(FILE_PATH, mode='a', index=False, header=header)

def obtener_metricas_sidebar():
    """Calcula los totales para el Main."""
    if not os.path.exists(FILE_PATH):
        return None
    try:
        df = pd.read_csv(FILE_PATH)
        if df.empty: return None
        return {
            "apostado": df['monto'].sum(),
            "ganancia": df['ganancia_neta'].sum(),
            "roi": (df['ganancia_neta'].sum() / df['monto'].sum() * 100) if df['monto'].sum() > 0 else 0,
            "ultimos": df.tail(5).to_dict('records')
        }
    except:
        return None
