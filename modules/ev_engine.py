import sys
import os
import functools
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Forzamos a Python a ver la carpeta actual para encontrar 'connector'
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importación directa ahora que el path está corregido
import connector 

def calcular_ev(probabilidad_over, momio_americano=-110):
    momio_americano = float(momio_americano)
    momio_decimal = (momio_americano / 100) + 1 if momio_americano > 0 else (100 / abs(momio_americano)) + 1
    return round((probabilidad_over * (momio_decimal - 1)) - (1 - probabilidad_over), 4)

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.70
        self.top_n_picks = 5  

    def analyze_matches(self, datos_ia):
        # Convertimos los datos de la IA a DataFrame para procesar
        juegos = datos_ia.get("juegos", []) if isinstance(datos_ia, dict) else []
        df = pd.DataFrame(juegos)
        
        if df.empty: return []

        picks = []
        for _, row in df.iterrows():
            # Lógica simple de probabilidad para probar que el motor funciona
            prob_modelo = 0.52 # Base
            momio = int(str(row.get('moneyline', 100)).replace('+', ''))
            ev = calcular_ev(prob_modelo, momio)
            
            picks.append({
                "juego": f"{row.get('away')} @ {row.get('home')}",
                "ev": ev,
                "momio": momio,
                "status": "🔥 VALOR" if ev > 0 else "RIESGO"
            })
        return sorted(picks, key=lambda x: x["ev"], reverse=True)
