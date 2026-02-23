# ev_engine.py - Eficiente: Vectorizado, cache, limits
import functools
import itertools
import numpy as np
import pandas as pd
from scipy.stats import poisson
# Importante: Asegúrate de que estos módulos existan en tu carpeta /modules
from connector import get_live_data 
# from stats_fetch import get_player_avg # Descomenta si usas este módulo externo

# --- CORRECCIÓN PARA MAIN.PY: Función global requerida ---
def calcular_ev(probabilidad_over, momio_americano=-110):
    """
    Calcula el Valor Esperado (EV) de forma individual para el dashboard.
    """
    if momio_americano > 0:
        momio_decimal = (momio_americano / 100) + 1
    else:
        momio_decimal = (100 / abs(momio_americano)) + 1
    
    # Probabilidad * Ganancia - Probabilidad de perder * Apuesta (1)
    ev = (probabilidad_over * (momio_decimal - 1)) - (1 - probabilidad_over)
    return round(ev, 4)

@functools.lru_cache(maxsize=128)  # Cache stats para optimizar rendimiento
def cached_player_avg(player, stat):
    # Simulación si get_player_avg no está disponible, o integración real
    try:
        from stats_fetch import get_player_avg
        return get_player_avg(player, stat)
    except ImportError:
        return 0.0

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.7 # Filtro del 70% solicitado
        self.ev_threshold = 1.05
        self.max_legs = 4
        self.top_n_picks = 5  

    def analyze_matches(self):
        live_data = get_live_data()
        if not live_data:
            return [], None
        df_props = pd.DataFrame(live_data)  
        individual_picks = self._batch_filter_layers(df_props)
        best_parlay = self._find_best_parlay(individual_picks)
        return individual_picks, best_parlay

    def _batch_filter_layers(self, df):
        picks = []
        # Jerarquía de 4 capas: Triples, Puntos, Equipo, ML
        layers = [self._over_triples, self._over_points_player, self._over_team_points, self._moneyline]
        for layer in layers:
            layer_picks = layer(df)
            if not layer_picks.empty:
                picks.extend(layer_picks.to_dict('records'))
                break # Detenerse al encontrar la capa con mayor valor
        return sorted(picks, key=lambda x: x.get('ev', 0), reverse=True)[:self.top_n_picks]

    def _over_triples(self, df):
        triples_df = df[df['type'] == 'triples'].copy()
        if triples_df.empty:
            return pd.DataFrame()
        
        triples_df['avg_3pm'] = triples_df.apply(lambda row: cached_player_avg(row['player'], '3PM'), axis=1)
        # Poisson para calcular probabilidad real
        triples_df['prob_over'] = triples_df.apply(lambda row: 1 - poisson.cdf(row['line'], row['avg_3pm']) if row['avg_3pm'] > 0 else 0, axis=1)
        
        # Cálculo de cuota implícita
        triples_df['implied'] = np.where(triples_df['odds_over'] < 0, 
                                         abs(triples_df['odds_over']) / (abs(triples_df['odds_over']) + 100), 
                                         100 / (triples_df['odds_over'] + 100))
        
        triples_df['ev'] = triples_df['prob_over'] / triples_df['implied']
        return triples_df[(triples_df['prob_over'] > self.high_prob_threshold) & (triples_df['ev'] > self.ev_threshold)]

    # Capas adicionales (Mantenlas con tu lógica original)
    def _over_points_player(self, df): return pd.DataFrame() 
    def _over_team_points(self, df): return pd.DataFrame()
    def _moneyline(self, df): return pd.DataFrame()

    def _find_best_parlay(self, picks):
        if len(picks) < 2: return None
        # Lógica de combinaciones itertools...
        return None

    # _calculate_parlay_odds mismo

