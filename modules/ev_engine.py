# Dentro de modules/ev_engine.py

import sys
import os
import functools
import pandas as pd  # <--- ESTA LÍNEA ES VITAL PARA EVITAR EL NAMEERROR
import numpy as np
from scipy.stats import poisson

# Configuración de rutas para evitar el ImportError en Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importamos el conector de forma segura
try:
    import connector
except ImportError:
    from . import connector

def calcular_ev(probabilidad_over, momio_americano=-110):
    """Calcula el Valor Esperado."""
    try:
        momio_americano = float(momio_americano)
        momio_decimal = (momio_americano / 100) + 1 if momio_americano > 0 else (100 / abs(momio_americano)) + 1
        return round((probabilidad_over * (momio_decimal - 1)) - (1 - probabilidad_over), 4)
    except:
        return 0.0

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.52 # Probabilidad base para detectar valor
        self.top_n_picks = 5  

    def analyze_matches(self, datos_ia):
        """Metodo de clase para procesar datos de la IA."""
        # Aseguramos que 'juegos' exista para evitar fallos de DataFrame
        juegos = datos_ia.get("juegos", []) if isinstance(datos_ia, dict) else []
        
        # Aquí se producía el NameError si 'pd' no estaba bien definido
        df = pd.DataFrame(juegos)
        
        if df.empty: 
            return []

        picks = []
        for _, row in df.iterrows():
            try:
                # Limpieza de momios para evitar ValueError
                raw_momio = str(row.get('moneyline', '100')).replace('+', '').strip()
                if not raw_momio or not raw_momio.lstrip('-').isdigit():
                    continue
                
                momio = int(raw_momio)
                ev = calcular_ev(self.high_prob_threshold, momio)
                
                if ev > 0:
                    picks.append({
                        "juego": f"{row.get('away', 'Visitante')} @ {row.get('home', 'Local')}",
                        "ev": ev,
                        "momio": momio,
                        "status": "🔥 VALOR" if ev > 0.05 else "LIGERO VALOR"
                    })
            except:
                continue 
                
        return sorted(picks, key=lambda x: x["ev"], reverse=True)
