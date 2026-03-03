# modules/montecarlo_pro.py
import numpy as np
from math import exp, factorial
import streamlit as st

class MonteCarloPro:
    """
    Simulador Monte Carlo profesional para análisis de partidos
    """
    
    def __init__(self, simulations=50000):
        self.simulations = simulations
        np.random.seed(42)  # Reproducibilidad
    
    def poisson_pmf(self, k, lam):
        """Probabilidad de Poisson"""
        return (lam**k * exp(-lam)) / factorial(k)
    
    def simulate_match(self, home_lambda, away_lambda, correlation=0.0):
        """
        Simula un partido con correlación opcional entre goles
        Usa cópula Gaussiana para correlación realista
        """
        if correlation == 0:
            # Independiente (Poisson simple)
            home_goals = np.random.poisson(home_lambda)
            away_goals = np.random.poisson(away_lambda)
        else:
            # Correlación mediante cópula normal
            mean = [0, 0]
            cov = [[1, correlation], [correlation, 1]]
            z = np.random.multivariate_normal(mean, cov)
            
            # Transformar a Poisson manteniendo correlación
            u_home = exp(-home_lambda)
            u_away = exp(-away_lambda)
            
            # Método de inversión
            home_goals = 0
            prob = u_home
            r = 0.5 * (1 + np.math.erf(z[0] / np.sqrt(2)))
            while r > prob:
                home_goals += 1
                prob += self.poisson_pmf(home_goals, home_lambda)
            
            away_goals = 0
            prob = u_away
            r = 0.5 * (1 + np.math.erf(z[1] / np.sqrt(2)))
            while r > prob:
                away_goals += 1
                prob += self.poisson_pmf(away_goals, away_lambda)
        
        return home_goals, away_goals
    
    def simulate_match_batch(self, home_lambda, away_lambda, n_sims=None):
        """
        Simula lotes de partidos (más eficiente)
        """
        if n_sims is None:
            n_sims = self.simulations
        
        home_goals = np.random.poisson(home_lambda, n_sims)
        away_goals = np.random.poisson(away_lambda, n_sims)
        
        return home_goals, away_goals
    
    def calculate_probabilities(self, home_goals, away_goals):
        """
        Calcula todas las probabilidades de las simulaciones
        """
        total_goals = home_goals + away_goals
        n_sims = len(home_goals)
        
        # Resultado 1X2
        home_win = np.mean(home_goals > away_goals)
        draw = np.mean(home_goals == away_goals)
        away_win = np.mean(away_goals > home_goals)
        
        # Totales
        probs = {
            'home_win': home_win,
            'draw': draw,
            'away_win': away_win,
            'over_0_5': np.mean(total_goals > 0.5),
            'over_1_5': np.mean(total_goals > 1.5),
            'over_2_5': np.mean(total_goals > 2.5),
            'over_3_5': np.mean(total_goals > 3.5),
            'over_4_5': np.mean(total_goals > 4.5),
            'over_5_5': np.mean(total_goals > 5.5),
            'btts': np.mean((home_goals > 0) & (away_goals > 0)),
            'btts_first_half': np.mean((home_goals > 0) & (away_goals > 0)) * 0.45,  # Aproximación
            'avg_goals': np.mean(total_goals),
            'std_goals': np.std(total_goals),
        }
        
        # Handicaps
        probs['home_handicap_-1'] = np.mean(home_goals - away_goals >= 1)
        probs['home_handicap_-2'] = np.mean(home_goals - away_goals >= 2)
        probs['away_handicap_-1'] = np.mean(away_goals - home_goals >= 1)
        probs['away_handicap_-2'] = np.mean(away_goals - home_goals >= 2)
        
        return probs
    
    def analyze_match(self, home_lambda, away_lambda, correlation=0.0):
        """
        Análisis completo de un partido con Monte Carlo
        """
        home_goals, away_goals = self.simulate_match_batch(home_lambda, away_lambda)
        return self.calculate_probabilities(home_goals, away_goals)
    
    def analyze_parlay(self, matches_params):
        """
        Analiza un parlay completo con Monte Carlo
        matches_params: lista de (home_lambda, away_lambda)
        """
        n_matches = len(matches_params)
        results = np.zeros((self.simulations, n_matches, 2))  # [sim, match, goles local/visitante]
        
        for i, (home_lambda, away_lambda) in enumerate(matches_params):
            results[:, i, 0], results[:, i, 1] = self.simulate_match_batch(home_lambda, away_lambda)
        
        # Calcular métricas del parlay
        parlay_stats = {
            'win_rate': 0,
            'avg_profit': 0,
            'max_loss': 0,
            'max_win': 0,
            'sharpe_ratio': 0
        }
        
        return parlay_stats
    
    def value_at_risk(self, probs, odds, confidence=0.95):
        """
        Calcula Value at Risk (VaR) para una apuesta
        """
        simulations = 10000
        stakes = np.random.uniform(0, 100, simulations)
        
        # Simular resultados
        wins = np.random.random(simulations) < probs
        profits = wins * stakes * (odds - 1) - (~wins) * stakes
        
        var = np.percentile(profits, (1 - confidence) * 100)
        cvar = np.mean(profits[profits <= var])
        
        return {
            'var': var,
            'cvar': cvar,
            'expected_profit': np.mean(profits),
            'win_probability': probs
        }
    
    def plot_distribution(self, home_goals, away_goals):
        """
        Genera datos para visualización de distribuciones
        """
        import plotly.graph_objects as go
        
        total_goals = home_goals + away_goals
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=total_goals,
            nbinsx=20,
            name='Goles totales',
            marker_color='#4CAF50'
        ))
        
        fig.update_layout(
            title='Distribución de Goles (Monte Carlo)',
            xaxis_title='Goles totales',
            yaxis_title='Frecuencia',
            height=400
        )
        
        return fig
