import sys
import os
import functools
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuración de PATH para evitar errores de importación en la nube
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import connector 

def calcular_ev(probabilidad_over, momio_americano=-110):
    """Calcula el valor esperado convirtiendo momios americanos."""
    try:
        momio_americano = float(momio_americano)
        if momio_americano > 0:
            momio_decimal = (momio_americano / 100) + 1
        else:
            momio_decimal = (100 / abs(momio_americano)) + 1
        return round((probabilidad_over * (momio_decimal - 1)) - (1 - probabilidad_over), 4)
    except:
        return 0.0

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.70
        self.top_n_picks = 5  

    # NOTA: Esta función DEBE estar indentada dentro de la clase
    def analyze_matches(self, datos_ia):
        """Analiza los datos de la IA buscando oportunidades de valor."""
        juegos = datos_ia.get("juegos", []) if isinstance(datos_ia, dict) else []
        df = pd.DataFrame(juegos)
        
        if df.empty: 
            return []

        picks = []
        for _, row in df.iterrows():
            try:
                # Limpieza robusta del momio para evitar ValueError
                raw_momio = str(row.get('moneyline', '100')).replace('+', '').strip()
                
                # Validación: si no es un número válido, saltamos la fila
                if not raw_momio or not raw_momio.lstrip('-').isdigit():
                    continue
                    
                momio = int(raw_momio)
                prob_modelo = 0.52 # Probabilidad base para el cálculo de EV
                ev = calcular_ev(prob_modelo, momio)
                
                picks.append({
                    "juego": f"{row.get('away', 'TBD')} @ {row.get('home', 'TBD')}",
                    "ev": ev,
                    "momio": momio,
                    "status": "🔥 VALOR" if ev > 0 else "RIESGO"
                })
            except Exception:
                continue 
                
        return sorted(picks, key=lambda x: x["ev"], reverse=True)
