# modules/ev_engine.py
import functools
import itertools
import numpy as np
import pandas as pd
from scipy.stats import poisson
import math

# Importe relativo para evitar el ImportError en Streamlit Cloud
try:
    from .connector import get_live_data, get_real_time_odds
except ImportError:
    # Fallback para ejecución local o pruebas
    from connector import get_live_data, get_real_time_odds

# =========================================================
# 📊 CÁLCULOS MATEMÁTICOS BASE
# =========================================================

def calcular_ev(probabilidad_modelo, momio_americano):
    """
    Calcula el Valor Esperado (EV). 
    Fórmula: (Probabilidad * Ganancia) - (Probabilidad de Perder * Apuesta)
    """
    momio_americano = float(momio_americano)
    if momio_americano > 0:
        payout = momio_americano / 100
    else:
        payout = 100 / abs(momio_americano)
    
    ev = (probabilidad_modelo * payout) - (1 - probabilidad_modelo)
    return round(ev, 4)

def american_to_probability(odds):
    """Convierte momio americano a probabilidad implícita de la casa."""
    odds = float(odds)
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

@functools.lru_cache(maxsize=128)
def cached_player_avg(player, stat):
    """Obtiene promedios históricos (Simulado o desde stats_fetch)."""
    try:
        from .stats_fetch import get_player_avg
        return get_player_avg(player, stat)
    except:
        return 0.0

# =========================================================
# 🧠 MOTOR DE ANÁLISIS (EVEngine)
# =========================================================

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.70  # 70% solicitado para picks de alta confianza
        self.ev_threshold = 0.05        # 5% de ventaja mínima sobre la casa
        self.top_n_picks = 5  

    def analyze_matches(self, datos_ia=None):
        """
        Analiza juegos. Puede recibir datos de la Visión IA o del Scraper.
        """
        if datos_ia:
            df = pd.DataFrame(datos_ia)
        else:
            live_data = get_live_data()
            if not live_data: return [], None
            df = pd.DataFrame(live_data)
        
        individual_picks = self._scan_ev_opportunities(df)
        return individual_picks

    def _scan_ev_opportunities(self, df):
        """Aplica el modelo de Poisson y probabilidad de mercado."""
        picks = []
        
        for _, row in df.iterrows():
            # 1. Obtener Probabilidad del Mercado (Sharp)
            market_prob = american_to_probability(row.get('odds_over', -110))
            
            # 2. Calcular Probabilidad del Modelo (Poisson/Stats)
            # Si es por triples, usamos Poisson. Si es por puntos, modelo base.
            if row.get('type') == 'triples':
                avg = cached_player_avg(row.get('player'), '3PM')
                model_prob = 1 - poisson.cdf(row.get('line', 0.5), avg) if avg > 0 else 0.50
            else:
                # Modelo base estilo Sharp para totales/hándicaps
                line = float(row.get('line', 220))
                model_prob = 0.50 + ((line - 220) * 0.001)
                model_prob = max(min(model_prob, 0.65), 0.40)

            # 3. Calcular EV Final
            ev = calcular_ev(model_prob, row.get('odds_over', -110))
            
            if ev > 0:
                picks.append({
                    "juego": f"{row.get('away')} @ {row.get('home')}",
                    "ev": round(ev, 3),
                    "confianza": round(model_prob, 2),
                    "momio": row.get('odds_over'),
                    "ventaja": "ALTA" if model_prob >= self.high_prob_threshold else "NORMAL"
                })
        
        return sorted(picks, key=lambda x: x["ev"], reverse=True)[:self.top_n_picks]

