# -*- coding: utf-8 -*-
"""
Sistema ELO para cálculo de probabilidades 1X2
"""
import math

class ELOSystem:
    """
    Calcula probabilidades de resultados usando sistema ELO
    """
    
    def __init__(self, k_factor=32):
        self.k_factor = k_factor
        self.default_elo = 1500
        
        # Elo inicial por equipos (basado en poderío)
        self.team_elo = {
            'Manchester City': 1950, 'Liverpool': 1920, 'Arsenal': 1880,
            'Real Madrid': 1980, 'Barcelona': 1940, 'Atletico Madrid': 1850,
            'Bayern Munich': 1960, 'Borussia Dortmund': 1860,
            'Paris Saint Germain': 1900, 'Ajax Amsterdam': 1840,
            'PSV Eindhoven': 1800, 'Benfica': 1820, 'Porto': 1800,
            'América': 1750, 'Tigres UANL': 1740,
        }
    
    def get_team_elo(self, team_name):
        """Obtiene el rating ELO de un equipo"""
        return self.team_elo.get(team_name, self.default_elo)
    
    def expected_score(self, elo_a, elo_b):
        """Probabilidad esperada de que A gane a B"""
        return 1 / (1 + math.pow(10, (elo_b - elo_a) / 400))
    
    def get_win_probability(self, home, away, home_stats=None, away_stats=None):
        """
        Calcula probabilidades 1X2 para un partido
        """
        home_elo = self.get_team_elo(home)
        away_elo = self.get_team_elo(away)
        
        # Factor localía (+70 ELO)
        home_elo_adj = home_elo + 70
        
        # Probabilidades base
        p_home = self.expected_score(home_elo_adj, away_elo)
        p_away = self.expected_score(away_elo, home_elo_adj)
        
        # Ajustar por estadísticas si están disponibles
        if home_stats and away_stats:
            home_power = home_stats.get('power', 70)
            away_power = away_stats.get('power', 70)
            
            # Factor de poder (escala 0.8-1.2)
            power_factor = 1 + ((home_power - away_power) / 500)
            p_home *= power_factor
        
        # Calcular empate (mayor cuando los equipos son parejos)
        elo_diff = abs(home_elo_adj - away_elo)
        p_draw = 0.26 * math.exp(-elo_diff / 400)
        
        # Normalizar
        total = p_home + p_away + p_draw
        p_home_norm = p_home / total
        p_away_norm = p_away / total
        p_draw_norm = p_draw / total
        
        return {
            'home': round(p_home_norm, 3),
            'draw': round(p_draw_norm, 3),
            'away': round(p_away_norm, 3)
        }
