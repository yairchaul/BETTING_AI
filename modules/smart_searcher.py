# modules/smart_searcher.py
import requests
import unicodedata
import re
from difflib import SequenceMatcher
import streamlit as st

class SmartSearcher:
    def __init__(self):
        """Inicializa con todas las APIs disponibles en secrets"""
        self.football_api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
        self.google_cse_id = st.secrets.get("GOOGLE_CSE_ID", "")
        self.odds_api_key = st.secrets.get("ODDS_API_KEY", "")
        
    def normalize_name(self, name):
        """Normalización ultra-agresiva para matching"""
        if not name:
            return ""
        
        # Minúsculas y sin acentos
        name = name.lower().strip()
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        
        # Eliminar caracteres especiales y números
        name = re.sub(r'[^a-z\s]', '', name)
        
        # Diccionario de reemplazos comunes
        replacements = {
            'real madrid': 'realmadrid',
            'r madrid': 'realmadrid',
            'real m': 'realmadrid',
            'atletico madrid': 'atleticodemadrid',
            'at madrid': 'atleticodemadrid',
            'atleti': 'atleticodemadrid',
            'barcelona': 'barcelona',
            'barça': 'barcelona',
            'fc barcelona': 'barcelona',
            'ra yo': 'rayo',
            'ra y o': 'rayo',
            'celta': 'celta',
            'vigo': 'celta',
            'osasuna': 'osasuna',
            'ossa': 'osasuna',
            'levante': 'levante',
            'getafe': 'getafe',
            'girona': 'girona',
            'mallorca': 'rcdmallorca',
            'rcd mallorca': 'rcdmallorca',
            'oviedo': 'realoviedo',
            'real oviedo': 'realoviedo'
        }
        
        # Aplicar reemplazos
        for key, value in replacements.items():
            if key in name:
                return value
        
        # Eliminar palabras comunes
        common_words = ['fc', 'cf', 'sc', 'ac', 'cd', 'ud', 'sd', 'club', 'deportivo', 
                       'real', 'united', 'city', 'athletic', 'sporting', 'racing']
        for word in common_words:
            name = name.replace(word, '')
        
        # Eliminar espacios y devolver
        return re.sub(r'\s+', '', name)
    
    def similarity_score(self, a, b):
        """Calcula similitud entre dos nombres"""
        n1 = self.normalize_name(a)
        n2 = self.normalize_name(b)
        
        if not n1 or not n2:
            return 0
        
        # Similitud de secuencia
        ratio = SequenceMatcher(None, n1, n2).ratio()
        
        # Bonus si uno contiene al otro
        if n1 in n2 or n2 in n1:
            ratio += 0.2
        
        return min(ratio, 1.0)
    
    def search_football_api(self, team_name):
        """Búsqueda en API-Football"""
        if not self.football_api_key:
            return None
        
        try:
            headers = {'x-apisports-key': self.football_api_key}
            url = f"https://v3.football.api-sports.io/teams?search={team_name}"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('results', 0) > 0:
                best_match = None
                best_score = 0
                
                for item in response['response']:
                    team = item['team']
                    score = self.similarity_score(team_name, team['name'])
                    if score > best_score and score > 0.6:
                        best_score = score
                        best_match = team
                
                return best_match
        except:
            pass
        return None
    
    def search_google_cse(self, team_name):
        """Búsqueda en Google Custom Search para encontrar IDs"""
        if not self.google_api_key or not self.google_cse_id:
            return None
        
        try:
            query = f"{team_name} football team api-sports id"
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={self.google_cse_id}&key={self.google_api_key}"
            response = requests.get(url, timeout=5).json()
            
            # Buscar IDs en los resultados
            import re
            for item in response.get('items', []):
                snippet = item.get('snippet', '')
                # Buscar patrones de ID (números)
                ids = re.findall(r'\b\d{4,6}\b', snippet)
                if ids:
                    return {'id': ids[0], 'name': team_name, 'source': 'google_cse'}
        except:
            pass
        return None
    
    def search_odds_api(self, team_name):
        """Búsqueda en Odds API para obtener referencias"""
        if not self.odds_api_key:
            return None
        
        try:
            url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={self.odds_api_key}&regions=us&markets=h2h"
            response = requests.get(url, timeout=5).json()
            
            for event in response:
                home = event.get('home_team', '')
                away = event.get('away_team', '')
                
                if self.similarity_score(team_name, home) > 0.7:
                    return {'id': f"odds_{event['id']}", 'name': home, 'source': 'odds_api'}
                if self.similarity_score(team_name, away) > 0.7:
                    return {'id': f"odds_{event['id']}", 'name': away, 'source': 'odds_api'}
        except:
            pass
        return None
    
    def find_team(self, team_name):
        """Busca equipo usando TODAS las APIs disponibles"""
        
        # Intentar con Football API primero
        team = self.search_football_api(team_name)
        if team:
            return team
        
        # Intentar con Google CSE
        team = self.search_google_cse(team_name)
        if team:
            return team
        
        # Intentar con Odds API
        team = self.search_odds_api(team_name)
        if team:
            return team
        
        return None
    
    def get_last_5_matches(self, team_id):
        """Obtiene los últimos 5 partidos de un equipo"""
        if not self.football_api_key or not team_id:
            return None
        
        try:
            headers = {'x-apisports-key': self.football_api_key}
            url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            matches = []
            for game in response.get('response', []):
                is_home = game['teams']['home']['id'] == team_id
                
                match = {
                    'date': game['fixture']['date'][:10],
                    'home': game['teams']['home']['name'],
                    'away': game['teams']['away']['name'],
                    'goals_home': game['goals']['home'] or 0,
                    'goals_away': game['goals']['away'] or 0,
                    'result': 'G' if (is_home and game['goals']['home'] > game['goals']['away']) or 
                                    (not is_home and game['goals']['away'] > game['goals']['home']) else
                             'E' if game['goals']['home'] == game['goals']['away'] else 'P'
                }
                matches.append(match)
            
            return matches
        except:
            return None
