# modules/tracker.py
import csv
from datetime import datetime
import os

def guardar_pick(juego, stake, ev):
    """
    Registra el pick generado en un archivo CSV para aprendizaje y auditoría.
    """
    archivo = 'modules/historial_picks.csv'
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Crear encabezados si el archivo no existe
    if not os.path.exists(archivo):
        with open(archivo, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Fecha', 'Juego', 'Stake', 'EV', 'Resultado'])

    try:
        with open(archivo, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ahora, juego, stake, f"{ev*100:.2f}%", "PENDIENTE"])
    except Exception as e:
        print(f"Error guardando en tracker: {e}")
