import pandas as pd
import os
import datetime

FILE_PATH = "parlay_history.csv"

def registrar_parlay_automatico(sim, picks_txt):
    """Guarda el parlay en el archivo CSV."""
    nuevo_registro = {
        "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "monto": sim['monto'],
        "cuota_total": sim['cuota_total'],
        "pago_total": sim['pago_total'],
        "ganancia_neta": sim['ganancia_neta'],
        "picks": picks_txt,
        "Estado": "Pendiente"
    }
    
    df = pd.DataFrame([nuevo_registro])
    
    # Si el archivo no existe, lo crea con cabeceras
    header = not os.path.exists(FILE_PATH)
    df.to_csv(FILE_PATH, mode='a', index=False, header=header)

def obtener_resumen_historial():
    """Lee el historial y devuelve métricas limpias."""
    if not os.path.exists(FILE_PATH):
        return None
        
    df = pd.read_csv(FILE_PATH)
    if df.empty:
        return None
        
    resumen = {
        "apostado": df['monto'].sum(),
        "ganancia": df['ganancia_neta'].sum(),
        "total_picks": len(df),
        "ultimos": df.tail(5).to_dict('records')
    }
    return resumen
