import numpy as np
import json
import os
from datetime import datetime

class ELOSystem:
    def __init__(self, k_factor=32, home_advantage=100):
        self.ratings = {}
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.history = []
        
        # Ratings iniciales para equipos conocidos (basados en rendimiento histórico)
        self._init_ratings()
    
    def _init_ratings(self):
        """Inicializa ratings para equipos comunes"""
        initial_ratings = {
            # Serie A (Italia)
            'Napoles': 1650,
            'Napoli': 1650,
            'Torino': 1520,
            'Cagliari': 1480,
            'Como': 1440,
            'Atalanta': 1620,
            'Udinese': 1510,
            'Juventus': 1700,
            'Pisa': 1460,
            'Lecce': 1470,
            'Cremonese': 1450,
            'Fiorentina': 1580,
            'Parma': 1490,
            'Inter': 1680,
            'Milan': 1660,
            'Roma': 1600,
            'Lazio': 1590,
            'Bologna': 1530,
            'Genoa': 1490,
            'Empoli': 1470,
            'Monza': 1460,
            'Verona': 1480,
            'Salernitana': 1440,
            'Sassuolo': 1500,
            
            # Liga MX (México)
            'Puebla': 1480,
            'Tigres UANL': 1620,
            'Tigres': 1620,
            'Monterrey': 1610,
            'Querétaro FC': 1460,
            'Querétaro': 1460,
            'Atlas': 1490,
            'Tijuana': 1500,
            'Xolos': 1500,
            'Club Tijuana': 1500,
            'América': 1630,
            'Club America': 1630,
            'FC Juárez': 1440,
            'Juárez': 1440,
            'Chivas': 1570,
            'Guadalajara': 1570,
            'Cruz Azul': 1580,
            'Pumas': 1540,
            'UNAM': 1540,
            'Santos Laguna': 1510,
            'Santos': 1510,
            'Pachuca': 1560,
            'Leon': 1520,
            'León': 1520,
            'Necaxa': 1470,
            'Mazatlán': 1450,
            'San Luis': 1460,
            'Atletico San Luis': 1460,
            'Toluca': 1530,
            
            # Premier League
            'Manchester City': 1750,
            'Man City': 1750,
            'Liverpool': 1720,
            'Arsenal': 1700,
            'Chelsea': 1650,
            'Manchester United': 1640,
            'Man United': 1640,
            'Tottenham': 1620,
            'Newcastle': 1600,
            'Aston Villa': 1580,
            
            # La Liga
            'Real Madrid': 1760,
            'Barcelona': 1740,
            'Atletico Madrid': 1680,
            'Atlético Madrid': 1680,
            'Real Sociedad': 1590,
            'Athletic Bilbao': 1570,
            'Valencia': 1540,
            'Sevilla': 1550,
            'Villarreal': 1560,
            'Betis': 1530,
            
            # Bundesliga
            'Bayern Munich': 1740,
            'Bayern': 1740,
            'Borussia Dortmund': 1670,
            'Dortmund': 1670,
            'RB Leipzig': 1640,
            'Leipzig': 1640,
            'Bayer Leverkusen': 1660,
            'Leverkusen': 1660,
            
            # Ligue 1
            'PSG': 1720,
            'Paris Saint-Germain': 1720,
            'Marseille': 1580,
            'Lyon': 1570,
            'Monaco': 1590,
            'Lille': 1560,
        }
        
        for team, rating in initial_ratings.items():
            self.ratings[team] = rating
    
    def get_rating(self, team):
        """Obtiene el rating de un equipo"""
        if team not in self.ratings:
            # Si el equipo no existe, asignar rating promedio
            self.ratings[team] = 1500
        return self.ratings[team]
    
    def expected_score(self, rating_a, rating_b, home=False):
        """Probabilidad esperada de que A gane a B"""
        if home:
            rating_a += self.home_advantage
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def get_win_probability(self, home_team, away_team):
        """Calcula probabilidades de resultado"""
        rating_home = self.get_rating(home_team)
        rating_away = self.get_rating(away_team)
        
        # Probabilidad base
        exp_home = self.expected_score(rating_home, rating_away, home=True)
        exp_away = 1 - exp_home
        
        # Ajuste realista para fútbol (los empates son comunes)
        # Basado en distribución histórica de resultados
        rating_diff = abs(rating_home - rating_away)
        draw_prob = max(0.20, 0.32 - (rating_diff / 2000))
        
        # Ajustar probabilidades
        home_prob = exp_home * (1 - draw_prob)
        away_prob = exp_away * (1 - draw_prob)
        
        # Normalizar
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        return {
            'home': home_prob,
            'draw': draw_prob,
            'away': away_prob
        }
    
    def update_ratings(self, home_team, away_team, home_goals, away_goals):
        """Actualiza ratings después de un partido"""
        rating_home = self.get_rating(home_team)
        rating_away = self.get_rating(away_team)
        
        # Resultado real (1 para local, 0.5 empate, 0 visitante)
        if home_goals > away_goals:
            actual_home = 1
            actual_away = 0
        elif home_goals == away_goals:
            actual_home = 0.5
            actual_away = 0.5
        else:
            actual_home = 0
            actual_away = 1
        
        # Resultado esperado
        expected_home = self.expected_score(rating_home, rating_away, home=True)
        expected_away = 1 - expected_home
        
        # Ajustar K-factor por diferencia de goles
        goal_diff = abs(home_goals - away_goals)
        k_adj = self.k_factor * (1 + 0.2 * goal_diff)
        
        # Nuevos ratings
        new_rating_home = rating_home + k_adj * (actual_home - expected_home)
        new_rating_away = rating_away + k_adj * (actual_away - expected_away)
        
        self.ratings[home_team] = new_rating_home
        self.ratings[away_team] = new_rating_away
        
        # Guardar en historial
        self.history.append({
            'date': datetime.now().isoformat(),
            'home': home_team,
            'away': away_team,
            'score': f"{home_goals}-{away_goals}",
            'rating_home_before': rating_home,
            'rating_away_before': rating_away,
            'rating_home_after': new_rating_home,
            'rating_away_after': new_rating_away,
        })
        
        return {
            'home_new': new_rating_home,
            'away_new': new_rating_away
        }
    
    def save_ratings(self, filepath='data/elo_ratings.json'):
        """Guarda los ratings en un archivo"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump({
                'ratings': self.ratings,
                'history': self.history[-100:]  # Solo últimos 100
            }, f, indent=2)
    
    def load_ratings(self, filepath='data/elo_ratings.json'):
        """Carga ratings desde un archivo"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.ratings.update(data.get('ratings', {}))
                self.history = data.get('history', [])
# modules/elo_system.py (función mejorada)
    def get_win_probability(self, home_team, away_team, home_stats=None, away_stats=None):
        """
        Calcula probabilidades combinando ELO + estadísticas actuales
        """
        rating_home = self.get_rating(home_team)
        rating_away = self.get_rating(away_team)

        # Probabilidad base ELO
        exp_home = self.expected_score(rating_home, rating_away, home=True)
        exp_away = 1 - exp_home

        # Ajuste por forma reciente (si tenemos datos)
        if home_stats and away_stats:
            form_factor = 0.2  # Peso de la forma reciente
            # Calcular factor basado en goles promedio
            home_factor = home_stats['avg_goals_scored'] / (home_stats['avg_goals_scored'] + away_stats['avg_goals_conceded'])
            away_factor = 1 - home_factor

            # Combinar ELO + forma
            exp_home = exp_home * (1 - form_factor) + home_factor * form_factor
            exp_away = exp_away * (1 - form_factor) + away_factor * form_factor

        # Probabilidad de empate (basada en estadísticas históricas)
        draw_prob = 0.26  # Promedio histórico

        # Ajustar
        home_prob = exp_home * (1 - draw_prob)
        away_prob = exp_away * (1 - draw_prob)

        # Normalizar
        total = home_prob + draw_prob + away_prob
        return {
            'home': home_prob / total,
            'draw': draw_prob / total,
            'away': away_prob / total
        }