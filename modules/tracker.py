import pandas as pd
import os
import datetime

FILE_PATH = "parlay_history.csv"

def registrar_parlay_automatico(sim, picks_txt):
    """
    Guarda el parlay asegurando que los nombres de las columnas 
    coincidan con lo que el Sidebar del Main busca.
    """
    # Creamos el diccionario con los nombres de columna exactos
    nuevo_registro = {
        "Fecha": datetime.datetime.now().strftime("%d/%m %H:%M"),
        "monto": float(sim.get('monto', 0)),
        "cuota_total": float(sim.get('cuota_total', 0)),
        "ganancia_neta": float(sim.get('ganancia_neta', 0)),
        "picks": picks_txt
    }
    
    df_nuevo = pd.DataFrame([nuevo_registro])
    
    # Si el archivo no existe, lo creamos con encabezados. 
    # Si existe, añadimos la fila sin repetir encabezados.
    header_exist = not os.path.exists(FILE_PATH)
    df_nuevo.to_csv(FILE_PATH, mode='a', index=False, header=header_exist)

def limpiar_historial_corrupto():
    """
    Función de emergencia por si el CSV tiene errores de formato.
    Borra el archivo para empezar de cero.
    """
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
        return True
    return False
