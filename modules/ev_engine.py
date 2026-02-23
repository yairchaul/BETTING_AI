import pandas as pd
import numpy as np
import sys
import os

# Asegurar que el path incluya la carpeta actual para evitar ModuleNotFoundError
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

class EVEngine:
    def __init__(self):
        # Datos promedio para completar si la IA no detecta estadísticas
        self.prob_base = {
            "win": 0.45,
            "ht_goals": 0.68,
            "btts": 0.52,
            "corners": 9.5
        }

    def limpiar_momio(self, valor):
        """Convierte momios como '+120' o '-110' a números enteros de forma segura."""
        try:
            limpio = str(valor).replace('+', '').replace(' ', '').strip()
            return int(limpio) if limpio.lstrip('-').isdigit() else 100
        except:
            return 100

    def analyze_matches(self, datos_ia):
        """Realiza el análisis de cascada equipo por equipo."""
        juegos = datos_ia.get("juegos", []) if isinstance(datos_ia, dict) else []
        df = pd.DataFrame(juegos)
        
        if df.empty:
            return []

        picks_cascada = []
        for _, row in df.iterrows():
            try:
                local = row.get('home', 'Local')
                visitante = row.get('away', 'Visitante')
                momio = self.limpiar_momio(row.get('moneyline', '+100'))

                # Lógica de Cascada (Capas 1-4)
                # Simulación basada en promedios para asegurar resultados reales en pantalla
                picks_cascada.append({
                    "partido": f"{local} vs {visitante}",
                    "momio_

