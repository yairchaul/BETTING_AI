# ev_engine.py - Eficiente: Vectorizado, cache, limits
import functools
import itertools
import numpy as np
import pandas as pd
from scipy.stats import poisson
from connector import get_live_data
from stats_fetch import get_player_avg
import logging

@functools.lru_cache(maxsize=128)  # Cache stats
def cached_player_avg(player, stat):
    return get_player_avg(player, stat)

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.7
        self.ev_threshold = 1.05
        self.max_legs = 4
        self.top_n_picks = 5  # Limita combos

    def analyze_matches(self):
        live_data = get_live_data()
        if not live_data:
            return [], None
        df_props = pd.DataFrame(live_data)  # Pandas para batch
        individual_picks = self._batch_filter_layers(df_props)
        best_parlay = self._find_best_parlay(individual_picks)
        return individual_picks, best_parlay

    def _batch_filter_layers(self, df):
        picks = []
        for layer in [self._over_triples, self._over_points_player, self._over_team_points, self._moneyline]:
            layer_picks = layer(df)
            picks.extend([row.to_dict() for _, row in layer_picks.iterrows() if not layer_picks.empty])
            if picks:  # Salta si ya hay
                break
        return sorted(picks, key=lambda x: x.get('prob', 0), reverse=True)[:self.top_n_picks]  # Top-N eficiente

    def _over_triples(self, df):
        triples_df = df[df['type'] == 'triples'].copy()  # Filter batch
        if triples_df.empty:
            return pd.DataFrame()
        triples_df['avg_3pm'] = triples_df.apply(lambda row: cached_player_avg(row['player'], '3PM'), axis=1)
        triples_df['prob_over'] = triples_df.apply(lambda row: 1 - poisson.cdf(row['line'], row['avg_3pm']) if row['avg_3pm'] > 0 else 0, axis=1)
        triples_df['implied'] = np.where(triples_df['odds_over'] < 0, abs(triples_df['odds_over']) / (abs(triples_df['odds_over']) + 100), 100 / (triples_df['odds_over'] + 100))
        triples_df['ev'] = triples_df['prob_over'] / triples_df['implied']
        return triples_df[(triples_df['prob_over'] > self.high_prob_threshold) & (triples_df['ev'] > self.ev_threshold)]

    # Similar vectorizado para otras layers...

    def _find_best_parlay(self, picks):
        if len(picks) < 2:
            return None
        max_prob = 0
        best_combo = None
        for legs in range(2, min(self.max_legs + 1, len(picks) + 1)):
            for combo in itertools.combinations(picks, legs):  # Aún O(n^k), pero n=5 bajo
                probs = [p['prob_over'] for p in combo]
                chain_prob = np.prod(probs)
                if chain_prob > max_prob and chain_prob > self.high_prob_threshold / 2:
                    combined_odds = self._calculate_parlay_odds(combo)
                    combined_ev = np.mean([p['ev'] for p in combo])
                    best_combo = {'legs': list(combo), 'prob': chain_prob, 'odds': combined_odds, 'ev': combined_ev}
                    max_prob = chain_prob
        return best_combo

    # _calculate_parlay_odds mismo
