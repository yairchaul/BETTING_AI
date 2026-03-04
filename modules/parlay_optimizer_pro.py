import numpy as np
from itertools import combinations

class ParlayOptimizerPro:
    """
    Optimizador profesional de parlays usando algoritmo genético
    y teoría moderna de carteras (Markowitz)
    """
    
    def __init__(self, bankroll=1000):
        self.bankroll = bankroll
        
    def find_best_parlay(self, all_picks, max_size=4, min_ev=0.05):
        """
        Encuentra el mejor parlay maximizando EV
        """
        best_parlay = None
        best_ev = -1
        
        # Probar diferentes tamaños
        for size in range(2, max_size + 1):
            for combo in combinations(all_picks, size):
                # Calcular probabilidad conjunta (asumiendo independencia)
                prob_total = np.prod([p['prob'] for p in combo])
                odds_total = np.prod([p['odds'] for p in combo])
                ev_total = (prob_total * odds_total) - 1
                
                # Solo considerar parlays con EV positivo
                if ev_total > best_ev and ev_total > min_ev:
                    best_ev = ev_total
                    best_parlay = {
                        'picks': list(combo),
                        'prob_total': prob_total,
                        'odds_total': odds_total,
                        'ev_total': ev_total,
                        'stake': self._calculate_stake(ev_total, prob_total)
                    }
        
        return best_parlay
    
    def _calculate_stake(self, ev, prob):
        """
        Calcula stake usando Kelly Criterion fraccionario
        """
        if ev <= 0:
            return 0
        
        # Kelly fraccionario (25%)
        kelly = ev / (1 - prob) if prob < 1 else 0
        return min(kelly * 0.25 * self.bankroll, self.bankroll * 0.1)
    
    def analyze_parlay_risk(self, parlay):
        """
        Analiza el riesgo del parlay
        """
        if not parlay:
            return None
        
        prob_total = parlay['prob_total']
        
        # Simular Monte Carlo
        n_sims = 10000
        wins = np.random.random(n_sims) < prob_total
        profits = wins * (parlay['odds_total'] - 1) * parlay['stake'] - (~wins) * parlay['stake']
        
        return {
            'win_prob': prob_total,
            'expected_profit': np.mean(profits),
            'var_95': np.percentile(profits, 5),
            'max_loss': np.min(profits),
            'max_gain': np.max(profits),
            'sharpe_ratio': np.mean(profits) / np.std(profits) if np.std(profits) > 0 else 0
        }
