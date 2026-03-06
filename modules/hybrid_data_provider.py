import requests
import streamlit as st
import time
from modules.team_database import TeamDatabase

class HybridDataProvider:
    def __init__(self):
        self.football_api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.football_headers = {'x-apisports-key': self.football_api_key}
        self.football_base = "https://v3.football.api-sports.io"
        self.odds_api_key = st.secrets.get("ODDS_API_KEY", "")
        self.last_request_time = 0
        self.request_interval = 0.5
        
        # Cargar base de datos de equipos
        self.team_db = TeamDatabase()
        
        # Estadísticas locales (fallback cuando no hay datos de API)
        self.local_stats = {
            # Valores por defecto para equipos conocidos
            'default': {'gf': 1.35, 'ga': 1.35},
            
            # Basado en promedios de liga
            'Cienciano': {'gf': 1.3, 'ga': 1.3},
            'Melgar': {'gf': 1.4, 'ga': 1.2},
            'America de Cali': {'gf': 1.4, 'ga': 1.2},
            'Atletico Bucaramanga': {'gf': 1.2, 'ga': 1.3},
            'Orense SC': {'gf': 1.2, 'ga': 1.3},
            'Macara': {'gf': 1.1, 'ga': 1.3},
        }
        
        self.cache = {}
    
    def _rate_limit(self):
        now = time.time()
        if now - self.last_request_time < self.request_interval:
            time.sleep(self.request_interval - (now - self.last_request_time))
        self.last_request_time = now
    
    def get_team_id(self, team_name):
        """Obtiene el ID de un equipo desde la base de datos local"""
        return self.team_db.get_team_id(team_name) if self.team_db else None
    
    def _try_football_api(self, team_name):
        """Intenta obtener estadísticas de Football-API usando el ID del equipo"""
        team_id = self.get_team_id(team_name)
        if not team_id or not self.football_api_key:
            return None
        
        self._rate_limit()
        
        try:
            # Intentar con diferentes ligas
            leagues_to_try = [262, 135, 140, 78, 39]  # Liga MX, Serie A, La Liga, Bundesliga, Premier
            
            for league_id in leagues_to_try:
                url = f"{self.football_base}/teams/statistics"
                params = {"team": team_id, "season": 2025, "league": league_id}
                response = requests.get(url, headers=self.football_headers, params=params, timeout=3)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('response'):
                        stats = data['response']
                        gf = stats.get('goals', {}).get('for', {}).get('average', {}).get('total', 1.35)
                        ga = stats.get('goals', {}).get('against', {}).get('average', {}).get('total', 1.35)
                        return {
                            'gf': float(gf),
                            'ga': float(ga),
                            'source': f'football-api'
                        }
                time.sleep(0.2)
        except:
            pass
        
        return None
    
    def get_team_stats(self, team_name):
        cache_key = f"stats_{team_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 1. Intentar obtener de API
        api_stats = self._try_football_api(team_name)
        if api_stats:
            result = {
                'avg_goals_scored': api_stats['gf'],
                'avg_goals_conceded': api_stats['ga'],
                'source': 'api'
            }
            self.cache[cache_key] = result
            return result
        
        # 2. Usar estadísticas locales específicas
        local = self.local_stats.get(team_name, self.local_stats['default'])
        result = {
            'avg_goals_scored': local['gf'],
            'avg_goals_conceded': local['ga'],
            'source': 'local'
        }
        self.cache[cache_key] = result
        return result
    
    def get_live_odds(self, home_team, away_team):
        """Obtiene odds en vivo de Odds-API"""
        if not self.odds_api_key:
            return None
        
        try:
            url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
            params = {
                "apiKey": self.odds_api_key,
                "regions": "uk",
                "markets": "h2h",
                "oddsFormat": "decimal"
            }
            response = requests.get(url, params=params, timeout=3)
            
            if response.status_code == 200:
                matches = response.json()
                for match in matches:
                    if (home_team.lower() in match['home_team'].lower() and 
                        away_team.lower() in match['away_team'].lower()):
                        bookmakers = match.get('bookmakers', [])
                        if bookmakers:
                            outcomes = bookmakers[0].get('markets', [])[0].get('outcomes', [])
                            if len(outcomes) >= 3:
                                return {
                                    'cuota_local': outcomes[0]['price'],
                                    'cuota_empate': outcomes[1]['price'],
                                    'cuota_visitante': outcomes[2]['price']
                                }
        except:
            pass
        
        return None
