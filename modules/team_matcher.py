# modules/team_matcher.py
import unicodedata
import re
from difflib import SequenceMatcher
import requests
import streamlit as st

class TeamMatcher:
    def __init__(self):
        self.api_key = st.secrets["football_api_key"]
        self.cache = {}  # Cache de búsquedas
        
    def normalize_name(self, name):
        """Normaliza nombres: quita acentos, caracteres especiales, estandariza"""
        # Convertir a minúsculas
        name = name.lower().strip()
        
        # Quitar acentos
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        
        # Quitar caracteres especiales y palabras comunes
        name = re.sub(r'[^a-z0-9\s]', '', name)
        name = re.sub(r'\b(fc|cf|sc|ac|us|as|cd|real|united|city|athletic|deportivo)\b', '', name)
        
        # Quitar espacios múltiples
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def similarity_score(self, name1, name2):
        """Calcula similitud entre dos nombres"""
        n1 = self.normalize_name(name1)
        n2 = self.normalize_name(name2)
        return SequenceMatcher(None, n1, n2).ratio()
    
    def search_football_api(self, team_name, league_hint=None):
        """Busca en API-Sports con estrategias múltiples"""
        headers = {'x-apisports-key': self.api_key}
        normalized = self.normalize_name(team_name)
        
        # Estrategia 1: Búsqueda directa
        url = f"https://v3.football.api-sports.io/teams?search={normalized}"
        response = requests.get(url, headers=headers).json()
        
        if response.get('results', 0) > 0:
            return response['response'][0]['team']
        
        # Estrategia 2: Si hay pista de liga, buscar equipos de esa liga
        if league_hint:
            # Buscar liga primero
            league_url = f"https://v3.football.api-sports.io/leagues?search={league_hint}"
            league_resp = requests.get(league_url, headers=headers).json()
            
            if league_resp.get('results', 0) > 0:
                league_id = league_resp['response'][0]['league']['id']
                
                # Obtener equipos de la liga
                teams_url = f"https://v3.football.api-sports.io/teams?league={league_id}&season=2024"
                teams_resp = requests.get(teams_url, headers=headers).json()
                
                best_match = None
                best_score = 0
                
                for item in teams_resp.get('response', []):
                    team = item['team']
                    score = self.similarity_score(team_name, team['name'])
                    
                    # También probar con nombre corto si existe
                    if 'short_name' in team:
                        score = max(score, self.similarity_score(team_name, team['short_name']))
                    
                    if score > best_score and score > 0.6:  # Umbral de 60%
                        best_score = score
                        best_match = team
                
                if best_match:
                    return best_match
        
        # Estrategia 3: Búsqueda por palabras clave
        # Tomar la palabra más significativa del nombre
        words = normalized.split()
        for word in words:
            if len(word) > 3:  # Palabras significativas
                url = f"https://v3.football.api-sports.io/teams?search={word}"
                response = requests.get(url, headers=headers).json()
                
                if response.get('results', 0) > 0:
                    # Verificar si algún resultado tiene alta similitud
                    for item in response['response']:
                        team = item['team']
                        score = self.similarity_score(team_name, team['name'])
                        if score > 0.7:
                            return team
        
        return None
    
    def match_team_from_image(self, team_name, league_context=None):
        """Función principal para encontrar un equipo desde imagen"""
        cache_key = f"{team_name}_{league_context}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Intentar búsqueda
        team = self.search_football_api(team_name, league_context)
        
        if team:
            self.cache[cache_key] = team
            return team
        
        # Si no encuentra, devolver None pero guardar para referencia
        self.cache[cache_key] = None
        return None