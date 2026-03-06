# -*- coding: utf-8 -*-
"""
Proveedor híbrido de datos - Combina API + datos locales
"""
import json
import os
import random
from modules.team_database import TeamDatabase

class HybridDataProvider:
    """
    Provee estadísticas de equipos usando datos reales + lógica de fuerza relativa
    """
    
    def __init__(self):
        self.db = TeamDatabase()
        self.stats_cache = {}
        
        # Estadísticas base por liga (goles por partido)
        self.league_strength = {
            'Spain': {'avg_goals': 2.8, 'factor': 1.1},
            'England': {'avg_goals': 3.0, 'factor': 1.15},
            'Italy': {'avg_goals': 2.7, 'factor': 1.05},
            'Germany': {'avg_goals': 3.2, 'factor': 1.2},
            'France': {'avg_goals': 2.8, 'factor': 1.1},
            'Netherlands': {'avg_goals': 3.1, 'factor': 1.18},
            'Portugal': {'avg_goals': 2.6, 'factor': 1.0},
            'Belgium': {'avg_goals': 2.7, 'factor': 1.05},
            'Turkey': {'avg_goals': 2.6, 'factor': 1.0},
            'Scotland': {'avg_goals': 2.5, 'factor': 0.95},
            'Denmark': {'avg_goals': 2.4, 'factor': 0.9},
            'Sweden': {'avg_goals': 2.3, 'factor': 0.88},
            'Norway': {'avg_goals': 2.5, 'factor': 0.95},
            'Mexico': {'avg_goals': 2.6, 'factor': 1.0},
            'USA': {'avg_goals': 2.7, 'factor': 1.05},
        }
        
        # Poderío de equipos específicos (escala 0-100)
        self.team_power = {
            # Premier League
            'Manchester City': 95, 'Liverpool': 92, 'Arsenal': 90, 'Chelsea': 88,
            'Tottenham': 87, 'Manchester United': 86, 'Newcastle': 85,
            
            # LaLiga
            'Real Madrid': 96, 'Barcelona': 94, 'Atletico Madrid': 89,
            'Real Sociedad': 84, 'Athletic Bilbao': 82, 'Sevilla': 81,
            
            # Bundesliga
            'Bayern Munich': 94, 'Borussia Dortmund': 88, 'RB Leipzig': 86,
            'Bayer Leverkusen': 87,
            
            # Serie A
            'Inter': 90, 'Milan': 88, 'Juventus': 87, 'Napoli': 86,
            
            # Ligue 1
            'Paris Saint Germain': 92, 'Marseille': 83, 'Lyon': 82,
            
            # Eredivisie
            'Ajax Amsterdam': 88, 'PSV Eindhoven': 86, 'Feyenoord': 85,
            'AZ Alkmaar': 82,
            
            # Primeira Liga
            'Benfica': 86, 'Porto': 85, 'Sporting CP': 84,
            
            # Liga MX
            'América': 82, 'Tigres UANL': 81, 'Monterrey': 81, 'Guadalajara': 79,
        }
    
    def get_team_stats(self, team_name):
        """
        Obtiene estadísticas realistas para un equipo
        """
        if team_name in self.stats_cache:
            return self.stats_cache[team_name]
        
        # Obtener país del equipo
        team_id = self.db.get_team_id(team_name)
        country = 'Unknown'
        if team_id:
            # Buscar en la base de datos
            for tid, tdata in self.db.data.get('teams', {}).items():
                if str(tid) == str(team_id):
                    country = tdata.get('country', 'Unknown')
                    break
        
        # Determinar poder del equipo
        power = self.team_power.get(team_name, 70)  # 70 es base para equipos medios
        
        # Factor de liga
        league_factor = self.league_strength.get(country, {'factor': 1.0})['factor']
        
        # Calcular goles a favor (escala: 0.8 a 2.5)
        gf_base = 0.8 + (power / 100) * 1.7
        gf = round(gf_base * league_factor, 2)
        
        # Goles en contra (inversamente proporcional al poder)
        ga_base = 2.2 - (power / 100) * 1.4
        ga = round(ga_base / league_factor, 2)
        
        # Ajustes por nombre de equipo
        if 'Real' in team_name and 'Madrid' not in team_name:
            gf = round(gf * 1.1, 2)
        elif 'Athletic' in team_name or 'Sociedad' in team_name:
            gf = round(gf * 1.05, 2)
        
        stats = {
            'avg_goals_scored': min(2.8, max(0.7, gf)),
            'avg_goals_conceded': min(2.2, max(0.6, ga)),
            'power': power,
            'country': country
        }
        
        self.stats_cache[team_name] = stats
        return stats
    
    def get_match_stats(self, home, away):
        """
        Obtiene estadísticas combinadas para un partido
        """
        home_stats = self.get_team_stats(home)
        away_stats = self.get_team_stats(away)
        
        # Calcular expectativas de goles
        expected_home = home_stats['avg_goals_scored'] * 1.2  # Factor localía
        expected_away = away_stats['avg_goals_scored'] * 0.9  # Factor visitante
        
        return {
            'home': home_stats,
            'away': away_stats,
            'expected_home': round(expected_home, 2),
            'expected_away': round(expected_away, 2),
            'expected_total': round(expected_home + expected_away, 2)
        }
