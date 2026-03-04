import numpy as np
from math import exp, factorial
from modules.elo_system import ELOSystem
from modules.montecarlo_pro import MonteCarloPro
from modules.odds_api_integrator import OddsAPIIntegrator
from modules.data_fetcher import DataFetcher
from modules.parlay_optimizer import ParlayOptimizer

class ProAnalyzerSimple:
    def __init__(self):
        self.elo = ELOSystem()
        self.montecarlo = MonteCarloPro(simulations=10000)
        self.odds_api = OddsAPIIntegrator()
        self.data_fetcher = DataFetcher()
        self.optimizer = ParlayOptimizer()
        
        try:
            self.elo.load_ratings()
        except:
            pass
    
    def analyze_match(self, home_team, away_team, odds_captura):
        odds_reales = self.odds_api.get_live_odds(home_team, away_team)
        
        if not odds_reales:
            odds_reales = {
                'cuota_local': odds_captura.get('local', 2.0),
                'cuota_empate': odds_captura.get('draw', 3.0),
                'cuota_visitante': odds_captura.get('away', 3.0)
            }
        
        home_stats = self.data_fetcher.get_team_stats(home_team)
        away_stats = self.data_fetcher.get_team_stats(away_team)
        elo_probs = self.elo.get_win_probability(home_team, away_team)
        
        lambda_home = home_stats['avg_goals_scored'] * 1.1
        lambda_away = away_stats['avg_goals_scored']
        
        home_goals, away_goals = self.montecarlo.simulate_match_batch(lambda_home, lambda_away)
        mc_probs = self.montecarlo.calculate_probabilities(home_goals, away_goals)
        
        home_prob = elo_probs['home'] * 0.6 + mc_probs['home_win'] * 0.4
        draw_prob = elo_probs['draw'] * 0.6 + mc_probs['draw'] * 0.4
        away_prob = elo_probs['away'] * 0.6 + mc_probs['away_win'] * 0.4
        
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        mercados = [
            {
                'name': f'Gana {home_team}',
                'prob': home_prob,
                'odds': odds_reales['cuota_local'],
                'ev': (home_prob * odds_reales['cuota_local']) - 1,
                'category': '1X2'
            },
            {
                'name': 'Empate',
                'prob': draw_prob,
                'odds': odds_reales['cuota_empate'],
                'ev': (draw_prob * odds_reales['cuota_empate']) - 1,
                'category': '1X2'
            },
            {
                'name': f'Gana {away_team}',
                'prob': away_prob,
                'odds': odds_reales['cuota_visitante'],
                'ev': (away_prob * odds_reales['cuota_visitante']) - 1,
                'category': '1X2'
            },
            {
                'name': 'BTTS - Sí',
                'prob': mc_probs['btts'],
                'odds': 1 / mc_probs['btts'] * 0.95,
                'ev': (mc_probs['btts'] * (1 / mc_probs['btts'] * 0.95)) - 1,
                'category': 'BTTS'
            },
            {
                'name': 'Over 1.5',
                'prob': mc_probs['over_1_5'],
                'odds': 1 / mc_probs['over_1_5'] * 0.95,
                'ev': (mc_probs['over_1_5'] * (1 / mc_probs['over_1_5'] * 0.95)) - 1,
                'category': 'Totales'
            },
            {
                'name': 'Over 2.5',
                'prob': mc_probs['over_2_5'],
                'odds': 1 / mc_probs['over_2_5'] * 0.95,
                'ev': (mc_probs['over_2_5'] * (1 / mc_probs['over_2_5'] * 0.95)) - 1,
                'category': 'Totales'
            }
        ]
        
        value_bets = [m for m in mercados if m['ev'] > 0.05]
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'mercados': mercados,
            'value_bets': value_bets,
            'mc_stats': mc_probs,
            'elo_probs': elo_probs,
            'odds_reales': odds_reales,
            'stats': {'home': home_stats, 'away': away_stats}
        }
    
    def find_best_parlay(self, partidos_analizados, max_size=3):
        all_picks = []
        for analisis in partidos_analizados:
            for vb in analisis['value_bets']:
                all_picks.append({
                    'match': f"{analisis['home_team']} vs {analisis['away_team']}",
                    'selection': vb['name'],
                    'prob': vb['prob'],
                    'odds': vb['odds'],
                    'ev': vb['ev'],
                    'category': vb['category']
                })
        return self.optimizer.find_optimal_parlays(all_picks, max_size=max_size)
