# ev_engine.py - Eficiente: Vectorizado, cache, limits
import functools
import itertools
import numpy as np
import pandas as pd
from scipy.stats import poisson
import math

# --- CORRECCIÓN DE IMPORTACIÓN ---
# Usamos try/except para que funcione tanto en local como en Streamlit Cloud
try:
    from .connector import get_live_data, get_real_time_odds
except (ImportError, ValueError):
    from connector import get_live_data, get_real_time_odds

# --- FUNCIONES GLOBALES ---

def calcular_ev(probabilidad_over, momio_americano=-110):
    """
    Calcula el Valor Esperado (EV) de forma individual.
    """
    momio_americano = float(momio_americano)
    if momio_americano > 0:
        momio_decimal = (momio_americano / 100) + 1
    else:
        momio_decimal = (100 / abs(momio_americano)) + 1
    
    # EV = (P * G) - (1-P)
    ev = (probabilidad_over * (momio_decimal - 1)) - (1 - probabilidad_over)
    return round(ev, 4)

def american_to_probability(odds):
    """Convierte momio americano a probabilidad implícita."""
    odds = float(odds)
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

@functools.lru_cache(maxsize=128)
def cached_player_avg(player, stat):
    """Caché para optimizar el rendimiento de estadísticas."""
    try:
        from .stats_fetch import get_player_avg
        return get_player_avg(player, stat)
    except:
        return 0.0

# --- CLASE CORE: EVEngine ---

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.70 # Filtro de confianza del 70%
        self.ev_threshold = 0.05        # 5% de EV mínimo
        self.top_n_picks = 5  

    def analyze_matches(self, datos_ia=None):
        """
        Analiza mercados buscando oportunidades +EV. 
        Acepta datos de la IA o de la API en vivo.
        """
        if datos_ia:
            df = pd.DataFrame(datos_ia if isinstance(datos_ia, list) else datos_ia.get('juegos', []))
        else:
            live_data = get_live_data()
            if not live_data: return [], None
            df = pd.DataFrame(live_data)
        
        if df.empty: return [], None

        picks = self._scan_ev_opportunities(df)
        return picks

    def _scan_ev_opportunities(self, df):
        """Lógica de escaneo con capas de valor."""
        picks = []
        
        for _, row in df.iterrows():
            # Extraer momio y línea (con limpieza de datos básicos)
            try:
                momio = float(str(row.get('moneyline', row.get('odds_over', -110))).replace('+', ''))
                linea = float(str(row.get('total', row.get('line', 220))).split()[-1])
            except:
                continue

            # 1. Probabilidad del Mercado
            market_implied = american_to_probability(momio)
            
            # 2. Probabilidad del Modelo (Ajuste según tipo de apuesta)
            if 'triples' in str(row.get('type', '')).lower():
                avg = cached_player_avg(row.get('player'), '3PM')
                model_prob = 1 - poisson.cdf(linea, avg) if avg > 0 else 0.50
            else:
                # Modelo Base: Ventaja sobre líneas de cierre (Sharp model)
                model_prob = 0.50 + ((linea - 220) * 0.001)
                model_prob = max(min(model_prob, 0.65), 0.40)

            # 3. Cálculo de Valor
            ev = calcular_ev(model_prob, momio)
            
            if ev > 0:
                picks.append({
                    "juego": f"{row.get('away')} @ {row.get('home')}",
                    "ev": round(ev, 3),
                    "prob": round(model_prob, 2),
                    "momio": momio,
                    "status": "🔥 TOP VALUE" if model_prob >= self.high_prob_threshold else "VALUE"
                })
        
        return sorted(picks, key=lambda x: x["ev"], reverse=True)[:self.top_n_picks]

