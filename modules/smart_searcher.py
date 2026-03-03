# modules/smart_searcher.py
import requests
import unicodedata
import re
from difflib import SequenceMatcher
import streamlit as st
from groq import Groq

class SmartSearcher:
    def __init__(self):
        self.football_api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
        self.google_cse_id = st.secrets.get("GOOGLE_CSE_ID", "")
        self.odds_api_key = st.secrets.get("ODDS_API_KEY", "")
        self.groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "")) if st.secrets.get("GROQ_API_KEY") else None
        self.cache = {}
    
    def normalize(self, name):
        """Normalización para matching"""
        if not name:
            return ""
        
        name = name.lower().strip()
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        name = re.sub(r'[^a-z0-9\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def similarity(self, a, b):
        """Calcula similitud entre dos nombres"""
        n1 = self.normalize(a)
        n2 = self.normalize(b)
        if not n1 or not n2:
            return 0
        return SequenceMatcher(None, n1, n2).ratio()
    
    def find_team(self, team_name, context=None):
        """Busca equipo con múltiples estrategias"""
        cache_key = f"{team_name}_{context}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        team = self._search_football_api(team_name)
        if team:
            self.cache[cache_key] = team
            return team
        
        if self.groq_client:
            team = self._find_team_with_groq(team_name, context)
            if team:
                self.cache[cache_key] = team
                return team
        
        self.cache[cache_key] = None
        return None
    
    def _search_football_api(self, team_name):
        """Busca en API-Football"""
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
                    score = self.similarity(team_name, team['name'])
                    if score > best_score and score > 0.6:
                        best_score = score
                        best_match = team
                
                return best_match
        except:
            pass
        return None
    
    def _find_team_with_groq(self, team_name, context):
        """Usa Groq para interpretar nombres corruptos"""
        try:
            prompt = f"""
            El texto OCR extrajo este posible nombre de equipo: "{team_name}"
            Contexto adicional: {context if context else 'Sin contexto'}
            
            ¿Cuál es el nombre REAL de este equipo de fútbol?
            Responde SOLO con el nombre correcto, nada más.
            Si no estás seguro, responde "DESCONOCIDO".
            """
            
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            corrected_name = response.choices[0].message.content.strip()
            
            if corrected_name != "DESCONOCIDO":
                return self._search_football_api(corrected_name)
            
        except Exception as e:
            pass
        
        return None
    
    def get_team_stats(self, team_id):
        """Obtiene estadísticas de un equipo"""
        if not team_id:
            return None
        
        cache_key = f"stats_{team_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            headers = {'x-apisports-key': self.football_api_key}
            url = f"https://v3.football.api-sports.io/teams/statistics?team={team_id}&season=2024"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('response'):
                stats = response['response']
                self.cache[cache_key] = stats
                return stats
        except:
            pass
        
        return None
