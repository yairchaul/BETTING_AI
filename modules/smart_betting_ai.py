# -*- coding: utf-8 -*-
"""
Smart Betting AI - Simulación Monte Carlo y generación de mercados
"""
import math
import numpy as np

class SmartBettingAI:
    """
    Simula partidos usando Monte Carlo y genera probabilidades de mercados
    """
    
    def __init__(self, league_avg_goals=2.6, n_simulations=10000):
        self.league_avg_goals = league_avg_goals
        self.n_simulations = n_simulations
    
    def poisson_prob(self, k, lam):
        """Probabilidad de Poisson"""
        return (math.exp(-lam) * lam**k) / math.factorial(k)
    
    def simulate_match(self, home_expected, away_expected):
        """
        Simula un partido usando distribución de Poisson
        """
        home_goals = np.random.poisson(home_expected)
        away_goals = np.random.poisson(away_expected)
        return home_goals, away_goals
    
    def get_market_probabilities(self, home_expected, away_expected):
        """
        Calcula probabilidades para todos los mercados vía Monte Carlo
        """
        total_goals = []
        home_wins = 0
        away_wins = 0
        draws = 0
        btts = 0
        over1_5 = 0
        over2_5 = 0
        over3_5 = 0
        over1_5_1t = 0
        
        # Simular n partidos
        for _ in range(self.n_simulations):
            h, a = self.simulate_match(home_expected, away_expected)
            total = h + a
            total_goals.append(total)
            
            # Resultado
            if h > a:
                home_wins += 1
            elif a > h:
                away_wins += 1
            else:
                draws += 1
            
            # BTTS
            if h > 0 and a > 0:
                btts += 1
            
            # Overs
            if total > 1.5:
                over1_5 += 1
            if total > 2.5:
                over2_5 += 1
            if total > 3.5:
                over3_5 += 1
            
            # Primer tiempo (aproximado 35% de los goles)
            h_1t = np.random.poisson(home_expected * 0.35)
            a_1t = np.random.poisson(away_expected * 0.35)
            if h_1t + a_1t > 1.5:
                over1_5_1t += 1
        
        return {
            '1x2': {
                'home': home_wins / self.n_simulations,
                'draw': draws / self.n_simulations,
                'away': away_wins / self.n_simulations
            },
            'btts': btts / self.n_simulations,
            'overs': {
                'over1_5': over1_5 / self.n_simulations,
                'over2_5': over2_5 / self.n_simulations,
                'over3_5': over3_5 / self.n_simulations,
                'over1_5_1t': over1_5_1t / self.n_simulations
            },
            'expected_goals': {
                'home': home_expected,
                'away': away_expected,
                'total': home_expected + away_expected
            }
        }
    
    def get_additional_markets(self, home_stats, away_stats):
        """
        Calcula mercados adicionales combinando estadísticas
        """
        home_expected = home_stats['avg_goals_scored']
        away_expected = away_stats['avg_goals_scored']
        
        return self.get_market_probabilities(home_expected, away_expected)
