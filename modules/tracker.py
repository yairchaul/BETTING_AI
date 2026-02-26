import pandas as pd
import os
import datetime

FILE_PATH = "parlay_history.csv"

def registrar_parlay_automatico(parlay_obj, monto):
    """
    Recibe el objeto ParlayResult y el monto desde el main.
    """
    picks_txt = " | ".join(parlay_obj.matches)
    ganancia_neta = (monto * parlay_obj.total_odd) - monto

    nuevo_registro = {
        "Fecha": datetime.datetime.now().strftime("%d/%m %H:%M"),
        "monto": float(monto),
        "cuota_total": float(parlay_obj.total_odd),
        "ganancia_neta": round(ganancia_neta, 2),
        "picks": picks_txt,
        "EV_Combinado": parlay_obj.total_ev
    }
    
    df_nuevo = pd.DataFrame([nuevo_registro])
    header_exist = not os.path.exists(FILE_PATH)
    df_nuevo.to_csv(FILE_PATH, mode='a', index=False, header=header_exist)
    return True

def cargar_historial():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    return pd.DataFrame()
