# modules/data_collector.py
import requests
import streamlit as st
from datetime import datetime, timedelta

class DataCollector:
    """
    Recolecta datos históricos de partidos para entrenar el modelo ML
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    
    def get_historical_matches(self, league_id, season='2024', limit=500):
        """
        Obtiene partidos históricos de una liga
        """
        if not self.api_key:
            st.warning("No hay API key configurada")
            return []
        
        headers = {'x-apisports-key': self.api_key}
        matches = []
        
        try:
            # Obtener fixtures de la temporada
            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"
            response = requests.get(url, headers=headers, timeout=10).json()
            
            for fixture in response.get('response', [])[:limit]:
                match = {
                    'fixture_id': fixture['fixture']['id'],
                    'date': fixture['fixture']['date'],
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'home_goals': fixture['goals']['home'] or 0,
                    'away_goals': fixture['goals']['away'] or 0,
                    'resultado': self._get_resultado(
                        fixture['goals']['home'] or 0,
                        fixture['goals']['away'] or 0
                    )
                }
                
                # Obtener estadísticas del partido (si están disponibles)
                stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={match['fixture_id']}"
                stats_response = requests.get(stats_url, headers=headers, timeout=10).json()
                
                match['stats'] = self._extract_stats(stats_response)
                matches.append(match)
            
            return matches
            
        except Exception as e:
            st.error(f"Error recolectando datos: {e}")
            return []
    
    def _get_resultado(self, home_goals, away_goals):
        """Determina el resultado del partido (0: local, 1: empate, 2: visitante)"""
        if home_goals > away_goals:
            return 0
        elif home_goals == away_goals:
            return 1
        else:
            return 2
    
    def _extract_stats(self, stats_response):
        """Extrae estadísticas relevantes del partido"""
        stats = {
            'home_possession': 50,
            'away_possession': 50,
            'home_shots': 0,
            'away_shots': 0,
            'home_shots_on_target': 0,
            'away_shots_on_target': 0
        }
        
        try:
            for team_stats in stats_response.get('response', []):
                is_home = team_stats['team']['name'] == 'home'
                for stat in team_stats['statistics']:
                    if stat['type'] == 'Ball Possession':
                        value = int(stat['value'].replace('%', '')) if stat['value'] else 50
                        if is_home:
                            stats['home_possession'] = value
                        else:
                            stats['away_possession'] = value
                    elif stat['type'] == 'Total Shots':
                        value = int(stat['value']) if stat['value'] else 0
                        if is_home:
                            stats['home_shots'] = value
                        else:
                            stats['away_shots'] = value
                    elif stat['type'] == 'Shots on Goal':
                        value = int(stat['value']) if stat['value'] else 0
                        if is_home:
                            stats['home_shots_on_target'] = value
                        else:
                            stats['away_shots_on_target'] = value
        except:
            pass
        
        return stats