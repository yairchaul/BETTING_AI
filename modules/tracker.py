# tracker.py
import csv
from datetime import datetime

ARCHIVO_HISTORICO = "data/historial_picks.csv"

def registrar_pick_generado(partido, seleccion, momio, confianza, inversion):
    """
    Guarda el pick en un CSV antes de que empiece el partido.
    Cura el error de no saber qué se apostó realmente.
    """
    nuevo_registro = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        partido,
        seleccion,
        momio,
        f"{confianza}%",
        inversion,
        "PENDIENTE" # Se actualizará al finalizar el juego
    ]
    
    with open(ARCHIVO_HISTORICO, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(nuevo_registro)

def auditar_resultados_diarios():
    """
    Función para comparar los picks guardados contra los resultados finales.
    Esto alimenta al módulo learning.py para ajustar probabilidades futuras.
    """
    # Lógica para leer el CSV y marcar como GANADO o PERDIDO
    pass
