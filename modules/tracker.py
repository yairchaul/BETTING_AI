# modules/tracker.py
import csv
from datetime import datetime

def guardar_apuesta_real(partido, seleccion, momio, confianza):
    """
    Registra el pick con nombres reales de Selenium para auditoría
    """
    datos_apuesta = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        partido,
        seleccion,
        momio,
        confianza,
        "Pendiente"
    ]
    
    # Guarda en la carpeta de módulos para fácil acceso
    with open('modules/historial_resultados.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(datos_apuesta)
