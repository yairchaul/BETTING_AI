import pandas as pd
import os
import datetime

FILE_PATH = "parlay_history.csv"

def registrar_parlay_automatico(parlay_obj, monto):
    picks_txt = " | ".join(parlay_obj.matches)
    ganancia_neta = (monto * parlay_obj.total_odd) - monto

    nuevo_registro = {
        "Fecha": datetime.datetime.now().strftime("%d/%m %H:%M"),
        "monto": float(monto),
        "cuota_total": float(parlay_obj.total_odd),
        "ganancia_neta": round(ganancia_neta, 2),
        "picks": picks_txt
    }
    
    df = pd.DataFrame([nuevo_registro])
    header = not os.path.exists(FILE_PATH)
    df.to_csv(FILE_PATH, mode='a', index=False, header=header)
    return True

def cargar_historial():
    if os.path.exists(FILE_PATH):
        try:
            return pd.read_csv(FILE_PATH)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def limpiar_historial_corrupto():
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
        return True
    return False
