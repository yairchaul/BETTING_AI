# modules/team_knowledge.py
import json
import os
import requests
import streamlit as st
from difflib import SequenceMatcher

class TeamKnowledge:
    """
    Base de conocimiento sobre equipos y ligas
    """
    def __init__(self):
        self.leagues_data = self._load_leagues_data()
        self.team_patterns = self._load_team_patterns()
        self.football_api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    
    def _load_leagues_data(self):
        """Carga información de ligas"""
        # Datos quemados de ligas comunes (se expandirá con el tiempo)
        return {
            'France Ligue 1': {
                'nivel': 'ALTO',
                'goles_promedio': 2.8,
                'local_ventaja': 55,
                'btts_pct': 52,
                'top_equipos': ['PSG', 'Marseille', 'Monaco', 'Lyon', 'Lens'],
                'descripcion': 'Liga top europea, muchos goles, PSG dominante'
            },
            'England Premier League': {
                'nivel': 'ALTO',
                'goles_promedio': 2.9,
                'local_ventaja': 48,
                'btts_pct': 55,
                'top_equipos': ['Manchester City', 'Liverpool', 'Arsenal', 'Chelsea'],
                'descripcion': 'Liga más competitiva, cualquiera le gana a cualquiera'
            },
            'Spain LaLiga': {
                'nivel': 'ALTO',
                'goles_promedio': 2.5,
                'local_ventaja': 52,
                'btts_pct': 48,
                'top_equipos': ['Real Madrid', 'Barcelona', 'Atletico Madrid'],
                'descripcion': 'Más táctica, menos goles que Premier'
            },
            'Germany Bundesliga': {
                'nivel': 'ALTO',
                'goles_promedio': 3.1,
                'local_ventaja': 54,
                'btts_pct': 58,
                'top_equipos': ['Bayern Munich', 'Dortmund', 'Leverkusen'],
                'descripcion': 'Muchos goles, partidos abiertos'
            },
            'Italy Serie A': {
                'nivel': 'ALTO',
                'goles_promedio': 2.6,
                'local_ventaja': 51,
                'btts_pct': 50,
                'top_equipos': ['Juventus', 'Inter', 'Milan', 'Napoli'],
                'descripcion': 'Táctica, algo lenta, menos goles'
            },
            'Mexico Liga MX': {
                'nivel': 'MEDIO',
                'goles_promedio': 2.7,
                'local_ventaja': 58,
                'btts_pct': 54,
                'top_equipos': ['America', 'Chivas', 'Tigres', 'Monterrey'],
                'descripcion': 'Loca, cualquiera gana, muchos goles en casa'
            },
            'Argentina Liga Profesional': {
                'nivel': 'MEDIO',
                'goles_promedio': 2.3,
                'local_ventaja': 62,
                'btts_pct': 45,
                'top_equipos': ['Boca', 'River', 'Racing'],
                'descripcion': 'Muy localista, pocos goles de visitante'
            },
            'Brazil Serie A': {
                'nivel': 'MEDIO',
                'goles_promedio': 2.4,
                'local_ventaja': 65,
                'btts_pct': 48,
                'top_equipos': ['Flamengo', 'Palmeiras', 'Corinthians'],
                'descripcion': 'Local muy fuerte, viajes largos afectan'
            },
            'default': {
                'nivel': 'DESCONOCIDO',
                'goles_promedio': 2.5,
                'local_ventaja': 55,
                'btts_pct': 50,
                'top_equipos': [],
                'descripcion': 'Liga sin datos específicos'
            }
        }
    
    def _load_team_patterns(self):
        """Patrones de equipos basados en análisis histórico"""
        return {
            'PSG': {
                'casa': {'goles': 2.8, 'recibe': 0.9, 'btts': 45, 'victorias': 85},
                'vs_top': {'btts': 70, 'victorias': 60},
                'vs_medios': {'btts': 55, 'victorias': 80},
                'patron': 'Golea en casa, a veces recibe goles de equipos buenos'
            },
            'Monaco': {
                'visitante': {'goles': 1.4, 'recibe': 1.6, 'btts': 65},
                'vs_top': {'anota': 75, 'pierde': 70},
                'patron': 'Siempre anota contra grandes, pero pierde'
            },
            'Lens': {
                'casa': {'goles': 2.2, 'recibe': 0.8, 'btts': 40, 'victorias': 80},
                'vs_debiles': {'goleadas': 70, 'clean_sheets': 60},
                'patron': 'Fortísimo en casa, aplasta a débiles'
            },
            'Marseille': {
                'visitante': {'goles': 1.5, 'victorias': 55},
                'vs_medios': {'victorias': 65},
                'patron': 'Buen visitante, aprovecha equipos sin motivación'
            }
        }
    
    def identify_league(self, team_name):
        """Intenta identificar la liga de un equipo"""
        # Buscar en ligas conocidas
        for league, data in self.leagues_data.items():
            if team_name in data.get('top_equipos', []):
                return league, data
        
        # Si no encuentra, usar API-Football
        if self.football_api_key:
            try:
                headers = {'x-apisports-key': self.football_api_key}
                url = f"https://v3.football.api-sports.io/teams?search={team_name}"
                response = requests.get(url, headers=headers, timeout=3).json()
                
                if response.get('results', 0) > 0:
                    team = response['response'][0]['team']
                    # Aquí podrías obtener la liga del equipo
                    return 'Desconocida', self.leagues_data['default']
            except:
                pass
        
        return 'Desconocida', self.leagues_data['default']
    
    def get_team_pattern(self, team_name):
        """Obtiene patrón de comportamiento de un equipo"""
        # Buscar en patrones conocidos
        for name, pattern in self.team_patterns.items():
            if name.lower() in team_name.lower() or team_name.lower() in name.lower():
                return pattern
        
        # Patrón genérico
        return {
            'casa': {'goles': 1.5, 'recibe': 1.2, 'btts': 50, 'victorias': 50},
            'visitante': {'goles': 1.1, 'recibe': 1.5, 'btts': 55, 'victorias': 30},
            'patron': 'Equipo sin datos específicos'
        }
