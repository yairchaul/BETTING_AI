# modules/probability_engine.py
"""
Motor de probabilidades basado en Poisson
Calcula 1X2, Over/Under, BTTS usando estadísticas de equipos
"""
import numpy as np
from math import exp, factorial

MAX_GOALS = 10


def poisson_prob(k, lam):
    """Probabilidad de Poisson P(X = k)"""
    return (exp(-lam) * lam**k) / factorial(k)


class ProbabilityEngine:
    """
    Calcula probabilidades reales para mercados de fútbol
    Basado en modelo Poisson estándar
    """
    
    def __init__(self, league_avg_goals=2.6):
        """
        Args:
            league_avg_goals: Promedio de goles por partido en la liga
        """
        self.league_avg_goals = league_avg_goals
    
    def expected_goals(self, home_stats, away_stats):
        """
        Calcula goles esperados (lambda) para cada equipo
        
        Fórmula:
        λ_home = ataque_local × defensa_visitante × promedio_liga
        λ_away = ataque_visitante × defensa_local × promedio_liga
        """
        # Extraer stats (con valores por defecto)
        home_attack = home_stats.get('attack', home_stats.get('avg_goals_scored', 1.2))
        home_defense = home_stats.get('defense', home_stats.get('avg_goals_conceded', 1.2))
        away_attack = away_stats.get('attack', away_stats.get('avg_goals_scored', 1.2))
        away_defense = away_stats.get('defense', away_stats.get('avg_goals_conceded', 1.2))
        
        # Normalizar respecto al promedio de liga
        home_attack_norm = home_attack / 1.2
        home_defense_norm = home_defense / 1.2
        away_attack_norm = away_attack / 1.2
        away_defense_norm = away_defense / 1.2
        
        # Calcular goles esperados
        lambda_home = home_attack_norm * away_defense_norm * self.league_avg_goals
        lambda_away = away_attack_norm * home_defense_norm * self.league_avg_goals
        
        return lambda_home, lambda_away
    
    def goal_matrix(self, lambda_home, lambda_away):
        """
        Genera matriz de probabilidades conjuntas
        matrix[i][j] = P(local anota i, visitante anota j)
        """
        matrix = np.zeros((MAX_GOALS, MAX_GOALS))
        
        for i in range(MAX_GOALS):
            for j in range(MAX_GOALS):
                p_home = poisson_prob(i, lambda_home)
                p_away = poisson_prob(j, lambda_away)
                matrix[i][j] = p_home * p_away
        
        return matrix
    
    def calculate_1x2(self, matrix):
        """
        Calcula probabilidades de resultado final
        """
        home = 0
        draw = 0
        away = 0
        
        for i in range(MAX_GOALS):
            for j in range(MAX_GOALS):
                if i > j:
                    home += matrix[i][j]
                elif i == j:
                    draw += matrix[i][j]
                else:
                    away += matrix[i][j]
        
        # Normalizar
        total = home + draw + away
        return {
            'home': home / total,
            'draw': draw / total,
            'away': away / total
        }
    
    def calculate_over(self, matrix, line):
        """
        Calcula probabilidad de Over X.5
        line puede ser 1.5, 2.5, 3.5
        """
        prob = 0
        for i in range(MAX_GOALS):
            for j in range(MAX_GOALS):
                if (i + j) > line:
                    prob += matrix[i][j]
        return prob
    
    def calculate_btts(self, matrix):
        """
        Calcula probabilidad de que ambos equipos anoten
        """
        prob = 0
        for i in range(1, MAX_GOALS):
            for j in range(1, MAX_GOALS):
                prob += matrix[i][j]
        return prob
    
    def analyze_match(self, home_team, away_team, home_stats, away_stats):
        """
        Análisis completo de un partido
        Retorna probabilidades 1X2 y mercados adicionales
        """
        lambda_home, lambda_away = self.expected_goals(home_stats, away_stats)
        matrix = self.goal_matrix(lambda_home, lambda_away)
        
        probs_1x2 = self.calculate_1x2(matrix)
        
        additional = {
            'over_1_5': self.calculate_over(matrix, 1.5),
            'over_2_5': self.calculate_over(matrix, 2.5),
            'over_3_5': self.calculate_over(matrix, 3.5),
            'btts_yes': self.calculate_btts(matrix),
            'btts_no': 1 - self.calculate_btts(matrix)
        }
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'lambda_home': lambda_home,
            'lambda_away': lambda_away,
            'probs_1x2': probs_1x2,
            'additional_markets': additional
        }