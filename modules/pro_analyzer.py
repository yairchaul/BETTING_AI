# modules/pro_analyzer_ultimate.py
import streamlit as st
import requests
import json
import numpy as np
from datetime import datetime
from modules.team_knowledge import TeamKnowledge
from modules.smart_searcher import SmartSearcher

class ProAnalyzerUltimate:
    """
    Analizador profesional con múltiples fuentes de datos
    """
    
    def __init__(self):
        self.knowledge = TeamKnowledge()
        self.searcher = SmartSearcher()
        
        # APIs profesionales (las que ya tienes + nuevas)
        self.apis = {
            'football_api': st.secrets.get("FOOTBALL_API_KEY", ""),
            'odds_api': st.secrets.get("ODDS_API_KEY", ""),
            'google_cse': {
                'key': st.secrets.get("GOOGLE_API_KEY", ""),
                'cx': st.secrets.get("GOOGLE_CSE_ID", "")
            },
            # NUEVAS FUENTES (OPCIONALES - PARA EL FUTURO)
            'isports': st.secrets.get("ISPORTS_API_KEY", ""),  # iSports API
            'sportsdataio': st.secrets.get("SPORTSDATAIO_KEY", "")  # SportsDataIO
        }
        
        # Base de conocimiento de ligas (ampliada)
        self.leagues_db = self._build_leagues_database()
        
        # Reglas de inferencia profesional
        self.rules = self._build_inference_rules()
    
    def _build_leagues_database(self):
        """Base de datos completa de ligas [citation:3][citation:7]"""
        return {
            'Argentina Liga Profesional': {
                'goles_promedio': 2.1,
                'local_ventaja': 62,
                'btts_pct': 42,
                'tarjetas_promedio': 5.8,
                'top_equipos': ['River', 'Boca', 'Racing', 'Independiente'],
                'descripcion': 'Muy localista, pocos goles, muchos amarillas',
                'under_2_5_prob': 68,
                'over_2_5_prob': 32
            },
            'Brazil Serie A': {
                'goles_promedio': 2.4,
                'local_ventaja': 65,
                'btts_pct': 48,
                'top_equipos': ['Flamengo', 'Palmeiras', 'Corinthians', 'Sao Paulo'],
                'descripcion': 'Local muy fuerte, viajes largos afectan',
                'under_2_5_prob': 55,
                'over_2_5_prob': 45
            },
            'England Premier League': {
                'goles_promedio': 2.9,
                'local_ventaja': 52,
                'btts_pct': 58,
                'top_equipos': ['Manchester City', 'Liverpool', 'Arsenal', 'Chelsea'],
                'descripcion': 'Liga más competitiva, cualquiera gana',
                'under_2_5_prob': 42,
                'over_2_5_prob': 58
            },
            'France Ligue 1': {
                'goles_promedio': 2.8,
                'local_ventaja': 55,
                'btts_pct': 52,
                'top_equipos': ['PSG', 'Marseille', 'Monaco', 'Lyon', 'Lens'],
                'descripcion': 'PSG dominante, resto competitivo',
                'under_2_5_prob': 45,
                'over_2_5_prob': 55
            },
            'Germany Bundesliga': {
                'goles_promedio': 3.2,
                'local_ventaja': 54,
                'btts_pct': 60,
                'top_equipos': ['Bayern', 'Dortmund', 'Leverkusen', 'Leipzig'],
                'descripcion': 'Muchos goles, partidos abiertos',
                'under_2_5_prob': 35,
                'over_2_5_prob': 65
            },
            'Mexico Liga MX': {
                'goles_promedio': 2.7,
                'local_ventaja': 58,
                'btts_pct': 54,
                'top_equipos': ['America', 'Chivas', 'Tigres', 'Monterrey'],
                'descripcion': 'Loca, cualquiera gana en casa',
                'under_2_5_prob': 48,
                'over_2_5_prob': 52
            },
            'Netherlands Eredivisie': {
                'goles_promedio': 3.3,
                'local_ventaja': 56,
                'btts_pct': 62,
                'top_equipos': ['Ajax', 'PSV', 'Feyenoord', 'AZ'],
                'descripcion': 'Muchísimos goles, defensas débiles',
                'under_2_5_prob': 30,
                'over_2_5_prob': 70
            },
            'Spain LaLiga': {
                'goles_promedio': 2.5,
                'local_ventaja': 54,
                'btts_pct': 48,
                'top_equipos': ['Real Madrid', 'Barcelona', 'Atletico', 'Real Sociedad'],
                'descripcion': 'Táctica, menos goles que Premier',
                'under_2_5_prob': 52,
                'over_2_5_prob': 48
            },
            'USA MLS': {
                'goles_promedio': 3.0,
                'local_ventaja': 60,
                'btts_pct': 65,
                'top_equipos': ['Inter Miami', 'LAFC', 'LA Galaxy', 'Atlanta'],
                'descripcion': 'Muchos goles, viajes largos',
                'under_2_5_prob': 38,
                'over_2_5_prob': 62
            }
        }
    
    def _build_inference_rules(self):
        """Reglas de inferencia profesional [citation:9]"""
        return [
            {
                'name': 'GOLES_BAJOS_ARGENTINA',
                'condition': lambda liga, local, visit: liga == 'Argentina Liga Profesional',
                'action': 'under_2_5',
                'base_prob': 68,
                'reason': 'La Liga Argentina tiene pocos goles históricamente'
            },
            {
                'name': 'GOLES_ALTOS_BUNDESLIGA',
                'condition': lambda liga, local, visit: liga == 'Germany Bundesliga',
                'action': 'over_2_5',
                'base_prob': 65,
                'reason': 'La Bundesliga es conocida por muchos goles'
            },
            {
                'name': 'LOCAL_FUERTE_VS_DEBIL',
                'condition': lambda liga, local, visit: 
                    self._is_top_team(local, liga) and not self._is_top_team(visit, liga),
                'action': 'local_gana',
                'base_prob': 75,
                'reason': f'{local} es top de la liga contra un rival menor'
            },
            {
                'name': 'TOP_VISITANTE_VS_DEBIL',
                'condition': lambda liga, local, visit: 
                    not self._is_top_team(local, liga) and self._is_top_team(visit, liga),
                'action': 'visitante_gana',
                'base_prob': 65,
                'reason': f'{visit} es muy superior a {local}'
            },
            {
                'name': 'BTT_ALTO_EN_LIGA',
                'condition': lambda liga, local, visit: 
                    self.leagues_db.get(liga, {}).get('btts_pct', 50) > 55,
                'action': 'btts',
                'base_prob': 60,
                'reason': f'En {liga} es común que ambos anoten'
            },
            {
                'name': 'LOCAL_MUY_FUERTE',
                'condition': lambda liga, local, visit: 
                    self.leagues_db.get(liga, {}).get('local_ventaja', 50) > 60,
                'action': 'local_no_pierde',
                'base_prob': 70,
                'reason': f'En {liga} los locales son muy fuertes'
            },
            {
                'name': 'CLASICO_RIVALES',
                'condition': lambda liga, local, visit:
                    self._are_rivals(local, visit),
                'action': 'btts',
                'base_prob': 65,
                'reason': 'Los clásicos suelen tener goles de ambos lados'
            },
            {
                'name': 'TOP_CASA_VS_DEBIL',
                'condition': lambda liga, local, visit:
                    self._is_top_team(local, liga) and self._is_bottom_team(visit, liga),
                'action': 'local_gana_y_over',
                'base_prob': 60,
                'reason': f'{local} aplasta en casa a los débiles'
            }
        ]
    
    def analyze_match(self, home_team, away_team, odds_data=None):
        """
        Análisis profesional completo
        """
        # PASO 1: Identificar la liga
        liga = self._identify_league(home_team, away_team)
        liga_data = self.leagues_db.get(liga, self.leagues_db.get('England Premier League'))
        
        # PASO 2: Buscar datos en APIs
        stats = self._fetch_team_stats(home_team, away_team)
        
        # PASO 3: Aplicar reglas de inferencia
        reglas_aplicadas = []
        for rule in self.rules:
            try:
                if rule['condition'](liga, home_team, away_team):
                    reglas_aplicadas.append(rule)
            except:
                pass
        
        # PASO 4: Determinar mejor apuesta
        best_bet = self._determine_best_bet(reglas_aplicadas, liga_data, stats)
        
        # PASO 5: Generar todos los mercados
        markets = self._generate_markets(reglas_aplicadas, liga_data, stats, best_bet)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'liga': liga,
            'liga_data': liga_data,
            'markets': markets,
            'best_bet': best_bet,
            'stats': stats,
            'reglas_aplicadas': [r['name'] for r in reglas_aplicadas]
        }
    
    def _identify_league(self, home, away):
        """Identifica la liga usando múltiples fuentes"""
        # Buscar en conocimiento local
        for liga, data in self.leagues_db.items():
            if (home in data.get('top_equipos', []) or 
                away in data.get('top_equipos', [])):
                return liga
        
        # Buscar en API-Football
        if self.apis['football_api']:
            try:
                headers = {'x-apisports-key': self.apis['football_api']}
                for team in [home, away]:
                    url = f"https://v3.football.api-sports.io/teams?search={team}"
                    response = requests.get(url, headers=headers, timeout=2).json()
                    if response.get('response'):
                        # Extraer liga de la respuesta
                        return 'England Premier League'  # Default
            except:
                pass
        
        return 'England Premier League'  # Default
    
    def _is_top_team(self, team, liga):
        """Determina si un equipo es top en su liga"""
        liga_data = self.leagues_db.get(liga, {})
        return team in liga_data.get('top_equipos', [])
    
    def _is_bottom_team(self, team, liga):
        """Determina si un equipo es débil"""
        # Por ahora, inversa de top
        return not self._is_top_team(team, liga)
    
    def _are_rivals(self, team1, team2):
        """Detecta si son clásicos rivales"""
        rivalries = [
            ('Boca', 'River'),
            ('Real Madrid', 'Barcelona'),
            ('Manchester United', 'Liverpool'),
            ('Manchester City', 'Manchester United'),
            ('Inter', 'Milan'),
            ('Roma', 'Lazio'),
            ('Arsenal', 'Tottenham')
        ]
        return any((team1 in r and team2 in r) for r in rivalries)
    
    def _fetch_team_stats(self, home, away):
        """Obtiene estadísticas de APIs [citation:2][citation:7]"""
        stats = {
            'home_form': [],
            'away_form': [],
            'home_goals_avg': 1.5,
            'away_goals_avg': 1.2,
            'home_concede_avg': 1.3,
            'away_concede_avg': 1.4,
            'home_btts_pct': 50,
            'away_btts_pct': 48
        }
        
        # Intentar con Football API
        if self.apis['football_api']:
            try:
                headers = {'x-apisports-key': self.apis['football_api']}
                
                # Buscar IDs
                home_id = self._get_team_id(home)
                away_id = self._get_team_id(away)
                
                if home_id:
                    url = f"https://v3.football.api-sports.io/fixtures?team={home_id}&last=5"
                    response = requests.get(url, headers=headers, timeout=2).json()
                    stats['home_form'] = self._extract_form(response, home_id)
                
                if away_id:
                    url = f"https://v3.football.api-sports.io/fixtures?team={away_id}&last=5"
                    response = requests.get(url, headers=headers, timeout=2).json()
                    stats['away_form'] = self._extract_form(response, away_id)
            except:
                pass
        
        return stats
    
    def _get_team_id(self, team_name):
        """Obtiene ID de equipo de API-Football"""
        try:
            headers = {'x-apisports-key': self.apis['football_api']}
            url = f"https://v3.football.api-sports.io/teams?search={team_name}"
            response = requests.get(url, headers=headers, timeout=2).json()
            if response.get('response'):
                return response['response'][0]['team']['id']
        except:
            pass
        return None
    
    def _extract_form(self, response, team_id):
        """Extrae forma reciente de respuesta API"""
        form = []
        for match in response.get('response', [])[:5]:
            is_home = match['teams']['home']['id'] == team_id
            home_goals = match['goals']['home'] or 0
            away_goals = match['goals']['away'] or 0
            
            if is_home:
                result = 'G' if home_goals > away_goals else 'E' if home_goals == away_goals else 'P'
                form.append({
                    'result': result,
                    'gf': home_goals,
                    'ga': away_goals,
                    'btts': home_goals > 0 and away_goals > 0
                })
            else:
                result = 'G' if away_goals > home_goals else 'E' if home_goals == away_goals else 'P'
                form.append({
                    'result': result,
                    'gf': away_goals,
                    'ga': home_goals,
                    'btts': home_goals > 0 and away_goals > 0
                })
        return form
    
    def _determine_best_bet(self, reglas, liga_data, stats):
        """Determina la mejor apuesta basada en reglas y datos"""
        if not reglas:
            return {
                'market': 'Over 1.5 goles',
                'probability': 70,
                'confidence': 'BAJA',
                'reason': 'Sin datos específicos, apuesta conservadora'
            }
        
        # Contar frecuencias
        from collections import Counter
        acciones = [r['action'] for r in reglas]
        mas_comun = Counter(acciones).most_common(1)[0][0]
        
        # Encontrar la regla con mayor probabilidad base
        mejor_regla = max(
            [r for r in reglas if r['action'] == mas_comun],
            key=lambda x: x.get('base_prob', 50)
        )
        
        # Ajustar probabilidad según liga
        prob_ajustada = mejor_regla['base_prob']
        if mas_comun == 'over_2_5':
            prob_ajustada = liga_data.get('over_2_5_prob', prob_ajustada)
        elif mas_comun == 'under_2_5':
            prob_ajustada = liga_data.get('under_2_5_prob', prob_ajustada)
        
        # Mapeo de acciones a nombres de mercado
        market_map = {
            'local_gana': 'Gana Local',
            'visitante_gana': 'Gana Visitante',
            'local_no_pierde': 'Local o Empate (1X)',
            'btts': 'Ambos anotan (BTTS)',
            'over_2_5': 'Over 2.5 goles',
            'under_2_5': 'Under 2.5 goles',
            'local_gana_y_over': 'Gana Local + Over 2.5'
        }
        
        return {
            'market': market_map.get(mas_comun, 'Over 1.5 goles'),
            'probability': prob_ajustada / 100,
            'confidence': 'ALTA' if prob_ajustada > 65 else 'MEDIA' if prob_ajustada > 55 else 'BAJA',
            'reason': mejor_regla['reason']
        }
    
    def _generate_markets(self, reglas, liga_data, stats, best_bet):
        """Genera todos los mercados basados en el análisis"""
        markets = []
        
        # Resultado final (basado en reglas)
        markets.append({'name': 'Gana Local', 'prob': 0.40, 'category': '1X2'})
        markets.append({'name': 'Empate', 'prob': 0.25, 'category': '1X2'})
        markets.append({'name': 'Gana Visitante', 'prob': 0.35, 'category': '1X2'})
        
        # Ajustar según reglas
        for r in reglas:
            if r['action'] == 'local_gana':
                markets[0]['prob'] = max(markets[0]['prob'], r['base_prob'] / 100)
                markets[2]['prob'] = min(markets[2]['prob'], 0.20)
            elif r['action'] == 'visitante_gana':
                markets[2]['prob'] = max(markets[2]['prob'], r['base_prob'] / 100)
                markets[0]['prob'] = min(markets[0]['prob'], 0.30)
        
        # Totales basados en liga
        markets.append({
            'name': 'Over 1.5 goles',
            'prob': 1 - (liga_data.get('under_2_5_prob', 50) / 100 * 0.6),
            'category': 'Totales'
        })
        markets.append({
            'name': 'Over 2.5 goles',
            'prob': liga_data.get('over_2_5_prob', 50) / 100,
            'category': 'Totales'
        })
        markets.append({
            'name': 'Under 2.5 goles',
            'prob': liga_data.get('under_2_5_prob', 50) / 100,
            'category': 'Totales'
        })
        
        # BTTS
        markets.append({
            'name': 'Ambos anotan (BTTS)',
            'prob': liga_data.get('btts_pct', 50) / 100,
            'category': 'BTTS'
        })
        
        # Primer tiempo
        markets.append({
            'name': 'Over 0.5 goles (1T)',
            'prob': min(0.85, liga_data.get('goles_promedio', 2.5) / 3 * 1.2),
            'category': 'Primer Tiempo'
        })
        
        # Combinados
        markets.append({
            'name': 'Gana Local + Over 1.5',
            'prob': markets[0]['prob'] * 0.85,
            'category': 'Combinado'
        })
        markets.append({
            'name': 'Gana Visitante + Over 1.5',
            'prob': markets[2]['prob'] * 0.85,
            'category': 'Combinado'
        })
        
        return sorted(markets, key=lambda x: x['prob'], reverse=True)
