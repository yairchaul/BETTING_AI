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
    import os
    sys.path.append(os.path.dirname(__file__))
    from connector import get_live_data, get_real_time_odds
