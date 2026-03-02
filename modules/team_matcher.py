# modules/team_matcher.py
import requests
import unicodedata
import re
from difflib import SequenceMatcher

class TeamMatcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = {}
        self.stats_cache = {}
    
    def normalize(self, name):
        """Normalización avanzada para matching"""
        if not name:
            return ""
        
        # Convertir a minúsculas
        name = name.lower().strip()
        
        # Quitar acentos
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        
        # Quitar caracteres especiales
        name = re.sub(r'[^a-z0-9\s]', '', name)
        
        # Quitar palabras comunes
        common_words = [
            'fc', 'cf', 'sc', 'ac', 'us', 'as', 'cd', 'real', 
            'united', 'city', 'athletic', 'deportivo', 'club', 
            'team', 'de', 'del', 'la', 'el', 'los', 'las',
            'and', '&', 'vs', 'v', 'sociedad', 'deportiva',
            'cultural', 'sporting', 'racing', 'racing club'
        ]
        for word in common_words:
            name = re.sub(r'\b' + word + r'\b', '', name)
        
        # Quitar números
        name = re.sub(r'\d+', '', name)
        
        # Quitar espacios múltiples
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def similarity(self, a, b):
        """Calcula similitud con múltiples estrategias"""
        if not a or not b:
            return 0
        
        n1 = self.normalize(a)
        n2 = self.normalize(b)
        
        if not n1 or not n2:
            return 0
        
        # Similitud de secuencia
        ratio = SequenceMatcher(None, n1, n2).ratio()
        
        # Bonus si una cadena contiene a la otra
        if n1 in n2 or n2 in n1:
            ratio += 0.15
            
        # Bonus por palabras clave
        words1 = set(n1.split())
        words2 = set(n2.split())
        common_words = words1.intersection(words2)
        if common_words:
            ratio += 0.1 * len(common_words)
        
        return min(ratio, 1.0)
    
    def find_team(self, team_name, league_hint=None):
        """Busca equipo con estrategias múltiples"""
        if not team_name or len(team_name) < 2:
            return None
            
        cache_key = f"{team_name}_{league_hint}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.api_key:
            return None
        
        try:
            headers = {'x-apisports-key': self.api_key}
            best_match = None
            best_score = 0
            
            # Estrategia 1: Búsqueda directa
            search_name = requests.utils.quote(team_name)
            url = f"https://v3.football.api-sports.io/teams?search={search_name}"
            response = requests.get(url, headers=headers, timeout=10).json()
            
            if response.get('results', 0) > 0:
                for item in response['response']:
                    team = item['team']
                    score = self.similarity(team_name, team['name'])
                    if score > best_score:
                        best_score = score
                        best_match = team
            
            # Estrategia 2: Si hay liga, buscar en esa liga
            if league_hint and league_hint != "Detectada de imagen" and best_score < 0.7:
                league_norm = self.normalize(league_hint)
                league_url = f"https://v3.football.api-sports.io/leagues?search={league_norm}"
                league_resp = requests.get(league_url, headers=headers, timeout=10).json()
                
                if league_resp.get('results', 0) > 0:
                    league_id = league_resp['response'][0]['league']['id']
                    teams_url = f"https://v3.football.api-sports.io/teams?league={league_id}&season=2024"
                    teams_resp = requests.get(teams_url, headers=headers, timeout=10).json()
                    
                    for item in teams_resp.get('response', []):
                        team = item['team']
                        score = self.similarity(team_name, team['name'])
                        if score > best_score and score > 0.4:
                            best_score = score
                            best_match = team
            
            # Estrategia 3: Búsqueda por palabra más significativa
            if best_score < 0.6:
                words = team_name.split()
                for word in words:
                    if len(word) > 3:
                        url = f"https://v3.football.api-sports.io/teams?search={word}"
                        response = requests.get(url, headers=headers, timeout=10).json()
                        
                        if response.get('results', 0) > 0:
                            for item in response['response']:
                                team = item['team']
                                score = self.similarity(team_name, team['name'])
                                if score > best_score and score > 0.5:
                                    best_score = score
                                    best_match = team
            
            # Guardar si la similitud es aceptable (>0.6)
            if best_score >= 0.6:
                self.cache[cache_key] = best_match
                return best_match
            
        except Exception as e:
            print(f"Error buscando equipo {team_name}: {e}")
        
        self.cache[cache_key] = None
        return None
    
    def get_team_stats(self, team_id):
        """Obtiene estadísticas de un equipo"""
        if not team_id:
            return None
            
        cache_key = f"stats_{team_id}"
        if cache_key in self.stats_cache:
            return self.stats_cache[cache_key]
        
        try:
            headers = {'x-apisports-key': self.api_key}
            url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024"
            response = requests.get(url, headers=headers, timeout=10).json()
            
            if response.get('response'):
                stats = response['response']
                self.stats_cache[cache_key] = stats
                return stats
        except:
            pass
        
        return None
