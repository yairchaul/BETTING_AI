# modules/odds_integrator.py
import requests
import streamlit as st
from datetime import datetime

class OddsIntegrator:
    """
    Integrador de odds en vivo desde API-Football
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.base_url = "https://v3.football.api-sports.io"
        self.cache = {}
    
    def get_live_odds(self, fixture_id=None):
        """
        Obtiene odds en vivo de la API-Football
        Endpoint beta que no consume cuota durante pruebas
        """
        if not self.api_key:
            st.warning("⚠️ No hay API Key de Football configurada")
            return None
        
        headers = {
            'x-apisports-key': self.api_key,
            'x-apisports-beta': 'true'  # Para acceder al endpoint beta
        }
        
        try:
            if fixture_id:
                url = f"{self.base_url}/odds/live?fixture={fixture_id}"
            else:
                url = f"{self.base_url}/odds/live"
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.warning(f"Error en API: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error obteniendo odds en vivo: {e}")
            return None
    
    def get_fixture_id(self, home_team, away_team, league=None):
        """
        Busca el ID de un fixture por nombres de equipos
        """
        cache_key = f"{home_team}_{away_team}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        headers = {'x-apisports-key': self.api_key}
        
        try:
            # Buscar próximos fixtures
            url = f"{self.base_url}/fixtures?search={home_team} {away_team}&season=2024"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('results', 0) > 0:
                for fixture in response['response']:
                    teams = fixture['teams']
                    if (home_team.lower() in teams['home']['name'].lower() and 
                        away_team.lower() in teams['away']['name'].lower()):
                        fixture_id = fixture['fixture']['id']
                        self.cache[cache_key] = fixture_id
                        return fixture_id
            
            return None
            
        except Exception as e:
            st.error(f"Error buscando fixture: {e}")
            return None
    
    def compare_with_market(self, our_probability, market_odds):
        """
        Compara nuestra probabilidad con las odds del mercado
        Detecta si hay valor (value bet)
        """
        if not market_odds:
            return None
        
        results = []
        for bookmaker, odds in market_odds.items():
            for market, odd in odds.items():
                # Probabilidad implícita de la cuota (1 / odd)
                implied_prob = 1 / odd
                
                # Diferencia entre nuestra probabilidad y la del mercado
                value = our_probability - implied_prob
                
                if value > 0.05:  # 5% de valor
                    results.append({
                        'bookmaker': bookmaker,
                        'market': market,
                        'odd': odd,
                        'our_prob': our_probability,
                        'implied_prob': implied_prob,
                        'value': value,
                        'recommendation': 'VALUE BET'
                    })
                elif value < -0.05:
                    results.append({
                        'bookmaker': bookmaker,
                        'market': market,
                        'odd': odd,
                        'our_prob': our_probability,
                        'implied_prob': implied_prob,
                        'value': value,
                        'recommendation': 'EVITAR'
                    })
        
        return results
    
    def get_best_odds(self, fixture_id, market='h2h'):
        """
        Obtiene las mejores odds para un fixture
        """
        headers = {'x-apisports-key': self.api_key}
        
        try:
            url = f"{self.base_url}/odds?fixture={fixture_id}&bookmaker=all"
            response = requests.get(url, headers=headers, timeout=5).json()
            
            if response.get('results', 0) > 0:
                odds_data = response['response'][0]
                
                best_odds = {
                    'home': {'value': 0, 'bookmaker': ''},
                    'draw': {'value': 0, 'bookmaker': ''},
                    'away': {'value': 0, 'bookmaker': ''}
                }
                
                for bookmaker in odds_data['bookmakers']:
                    for bet in bookmaker['bets']:
                        if bet['name'] == 'Match Winner':
                            for value in bet['values']:
                                if value['value'] == 'Home':
                                    if float(value['odd']) > best_odds['home']['value']:
                                        best_odds['home'] = {
                                            'value': float(value['odd']),
                                            'bookmaker': bookmaker['name']
                                        }
                                elif value['value'] == 'Draw':
                                    if float(value['odd']) > best_odds['draw']['value']:
                                        best_odds['draw'] = {
                                            'value': float(value['odd']),
                                            'bookmaker': bookmaker['name']
                                        }
                                elif value['value'] == 'Away':
                                    if float(value['odd']) > best_odds['away']['value']:
                                        best_odds['away'] = {
                                            'value': float(value['odd']),
                                            'bookmaker': bookmaker['name']
                                        }
                
                return best_odds
            
            return None
            
        except Exception as e:
            st.error(f"Error obteniendo mejores odds: {e}")
            return None
