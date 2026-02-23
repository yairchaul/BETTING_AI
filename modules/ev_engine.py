# modules/ev_engine.py
import functools
import pandas as pd
import numpy as np
from scipy.stats import poisson

# SOLUCIÓN DEFINITIVA AL IMPORT ERROR
try:
    # Intenta importación relativa (Streamlit Cloud)
    from .connector import get_live_data, get_real_time_odds
except (ImportError, ValueError):
    # Fallback para ejecución local
    import sys
  import sys
import os

# Agregamos la carpeta actual al path de Python para que encuentre 'connector'
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    # Intentamos la importación ahora que el path está configurado
    from connector import get_live_data, get_real_time_odds
except ImportError:
    # Si falla, intentamos la ruta relativa
    from .connector import get_live_data, get_real_time_odds
