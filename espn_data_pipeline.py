"""
ESPN DATA PIPELINE - Extracción de datos de ESPN con TODAS las cuotas
"""
import requests
import streamlit as st
from datetime import datetime

class ESPNDataPipeline:
    def __init__(self):
        self.base_url = "https://site.web.api.espn.com/apis/site/v2/sports"
        self.ligas_codigos = {
            "México - Liga MX": "mex.1",
            "UEFA - Champions League": "uefa.champions",
            "UEFA - Europa League": "uefa.europa",
            "UEFA - Europa Conference League": "uefa.europa.conf",
            "La Liga": "esp.1",
            "Inglaterra - Premier League": "eng.1",
            "Bundesliga 1": "ger.1",
            "Serie A": "ita.1",
            "Ligue 1": "fra.1",
            "Holanda - Eredivisie": "ned.1",
            "Portugal - Primeira Liga": "por.1",
            "México - Liga de Expansión MX": "mex.2",
            "Eliminatorias UEFA": "fifa.worldq.uefa",
            "México - Liga MX Femenil": "mex.women",
            "CONCACAF Champions Cup": "concacaf.champions",
            "Copa Libertadores": "conmebol.libertadores",
            "Copa Sudamericana": "conmebol.sudamericana",
            "Brasil - Serie A": "bra.1",
            "Argentina - Liga Profesional": "arg.1",
            "MLS - Major League Soccer": "usa.1",
        }
    
    # 🔥 MÉTODO QUE FALTABA - NBA con odds
    def get_nba_games_with_odds(self):
        """
        Obtiene partidos NBA con TODAS las cuotas
        """
        try:
            fecha = datetime.now().strftime("%Y%m%d")
            url = f"{self.base_url}/basketball/nba/scoreboard?dates={fecha}&limit=100"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                partidos = []
                
                for event in data.get('events', []):
                    competition = event['competitions'][0]
                    competitors = competition['competitors']
                    
                    if len(competitors) >= 2:
                        home = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                        away = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
                        
                        # Extraer odds
                        odds_data = self._extract_nba_odds(competition)
                        
                        # Extraer líderes estadísticos
                        lideres_local, lideres_visit = self._extract_nba_leaders(competitors)
                        
                        partidos.append({
                            'id': event.get('id'),
                            'local': home['team']['displayName'],
                            'visitante': away['team']['displayName'],
                            'fecha': event.get('date', '')[:10],
                            'hora': competition.get('date', '')[-8:] if competition.get('date') else '',
                            'estado': competition.get('status', {}).get('type', 'scheduled'),
                            'records': {
                                'local': home.get('records', [{}])[0].get('summary', '0-0') if home.get('records') else '0-0',
                                'visitante': away.get('records', [{}])[0].get('summary', '0-0') if away.get('records') else '0-0'
                            },
                            'odds': odds_data,
                            'lideres': {
                                'local': lideres_local,
                                'visitante': lideres_visit
                            }
                        })
                return partidos
            else:
                st.warning(f"⚠️ Error {response.status_code} en API NBA. Usando datos de ejemplo.")
                return self._get_mock_nba_data()
        except Exception as e:
            st.error(f"Error obteniendo NBA: {e}")
            return self._get_mock_nba_data()
    
    def _extract_nba_odds(self, competition):
        """Extrae odds de un partido NBA"""
        odds_data = {
            'moneyline': {'local': 'N/A', 'visitante': 'N/A'},
            'spread': {'valor': 0, 'local_odds': 'N/A', 'visitante_odds': 'N/A'},
            'totales': {'linea': 0, 'over_odds': 'N/A', 'under_odds': 'N/A'}
        }
        
        if 'odds' in competition and competition['odds']:
            odds = competition['odds'][0]
            
            # Moneyline
            if 'homeTeamOdds' in odds and odds['homeTeamOdds']:
                if 'american' in odds['homeTeamOdds']:
                    odds_data['moneyline']['local'] = odds['homeTeamOdds']['american']
            if 'awayTeamOdds' in odds and odds['awayTeamOdds']:
                if 'american' in odds['awayTeamOdds']:
                    odds_data['moneyline']['visitante'] = odds['awayTeamOdds']['american']
            
            # Si no encuentra en homeTeamOdds, buscar en moneyline
            if odds_data['moneyline']['local'] == 'N/A' and 'moneyline' in odds:
                ml_data = odds['moneyline']
                if 'home' in ml_data and 'close' in ml_data['home']:
                    odds_data['moneyline']['local'] = ml_data['home']['close'].get('odds', 'N/A')
                if 'away' in ml_data and 'close' in ml_data['away']:
                    odds_data['moneyline']['visitante'] = ml_data['away']['close'].get('odds', 'N/A')
            
            # Spread - valor
            if 'spread' in odds:
                odds_data['spread']['valor'] = odds.get('spread', 0)
            
            # Spread - odds
            if 'pointSpread' in odds:
                spread_details = odds['pointSpread']
                if 'home' in spread_details and 'close' in spread_details['home']:
                    odds_data['spread']['local_odds'] = spread_details['home']['close'].get('odds', 'N/A')
                if 'away' in spread_details and 'close' in spread_details['away']:
                    odds_data['spread']['visitante_odds'] = spread_details['away']['close'].get('odds', 'N/A')
            
            # Totales - línea
            if 'overUnder' in odds:
                odds_data['totales']['linea'] = odds.get('overUnder', 0)
            
            # Totales - odds
            if 'total' in odds:
                total_details = odds['total']
                if 'over' in total_details and 'close' in total_details['over']:
                    odds_data['totales']['over_odds'] = total_details['over']['close'].get('odds', 'N/A')
                if 'under' in total_details and 'close' in total_details['under']:
                    odds_data['totales']['under_odds'] = total_details['under']['close'].get('odds', 'N/A')
        
        return odds_data
    
    def _extract_nba_leaders(self, competitors):
        """Extrae líderes estadísticos de los equipos"""
        lideres_local = []
        lideres_visit = []
        
        for i, comp in enumerate(competitors):
            if 'leaders' in comp:
                for lider in comp['leaders']:
                    if lider.get('name') in ['pointsPerGame', 'assistsPerGame', 'reboundsPerGame']:
                        for jugador in lider.get('leaders', []):
                            stats = {
                                'nombre': jugador['athlete']['displayName'],
                                'categoria': lider['name'],
                                'valor': jugador['displayValue'],
                                'equipo': comp['team']['displayName']
                            }
                            if i == 0:  # local
                                lideres_local.append(stats)
                            else:  # visitante
                                lideres_visit.append(stats)
        
        return lideres_local, lideres_visit
    
    def _get_mock_nba_data(self):
        """Datos de ejemplo para NBA"""
        return [
            {
                'id': 'mock1',
                'local': 'Charlotte Hornets',
                'visitante': 'Orlando Magic',
                'fecha': datetime.now().strftime('%Y-%m-%d'),
                'hora': '19:00',
                'estado': 'scheduled',
                'records': {'local': '35-34', 'visitante': '38-30'},
                'odds': {
                    'moneyline': {'local': '-218', 'visitante': '+180'},
                    'spread': {'valor': -5.5, 'local_odds': '-110', 'visitante_odds': '-110'},
                    'totales': {'linea': 225.5, 'over_odds': '-108', 'under_odds': '-112'}
                },
                'lideres': {
                    'local': [
                        {'nombre': 'Brandon Miller', 'categoria': 'pointsPerGame', 'valor': '20.3', 'equipo': 'Charlotte Hornets'},
                        {'nombre': 'LaMelo Ball', 'categoria': 'assistsPerGame', 'valor': '7.2', 'equipo': 'Charlotte Hornets'}
                    ],
                    'visitante': [
                        {'nombre': 'Paolo Banchero', 'categoria': 'pointsPerGame', 'valor': '22.4', 'equipo': 'Orlando Magic'},
                        {'nombre': 'Jalen Suggs', 'categoria': 'assistsPerGame', 'valor': '5.3', 'equipo': 'Orlando Magic'}
                    ]
                }
            }
        ]

    def get_soccer_games_today(self, liga_nombre):
        """Obtiene partidos de fútbol para una liga"""
        codigo = self.ligas_codigos.get(liga_nombre)
        if not codigo:
            return []
        
        try:
            url = f"{self.base_url}/soccer/{codigo}/scoreboard"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                partidos = []
                
                for event in data.get('events', []):
                    competition = event['competitions'][0]
                    competitors = competition['competitors']
                    
                    if len(competitors) >= 2:
                        home = next((c for c in competitors if c.get('homeAway') == 'home'), competitors[0])
                        away = next((c for c in competitors if c.get('homeAway') == 'away'), competitors[1])
                        
                        partidos.append({
                            'id': event.get('id'),
                            'liga': liga_nombre,
                            'local': home['team']['displayName'],
                            'visitante': away['team']['displayName'],
                            'fecha': event.get('date', '')[:10]
                        })
                return partidos
        except:
            return []

    def get_ufc_events(self):
        """Obtiene eventos UFC"""
        try:
            url = f"{self.base_url}/mma/ufc/scoreboard"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                combates = []
                
                for event in data.get('events', []):
                    event_name = event.get('name', 'UFC Event')
                    event_date = event.get('date', '')[:10]
                    
                    for competition in event.get('competitions', []):
                        competitors = competition.get('competitors', [])
                        
                        if len(competitors) >= 2:
                            p1 = competitors[0]
                            p2 = competitors[1]
                            
                            pais1 = 'Desconocido'
                            pais2 = 'Desconocido'
                            
                            if 'athlete' in p1 and 'flag' in p1['athlete']:
                                pais1 = p1['athlete']['flag'].get('alt', 'Desconocido')
                            if 'athlete' in p2 and 'flag' in p2['athlete']:
                                pais2 = p2['athlete']['flag'].get('alt', 'Desconocido')
                            
                            combates.append({
                                'id': event.get('id'),
                                'evento': event_name,
                                'fecha': event_date,
                                'peleador1': {
                                    'nombre': p1['athlete']['displayName'],
                                    'record': p1.get('record', '0-0-0'),
                                    'pais': pais1
                                },
                                'peleador2': {
                                    'nombre': p2['athlete']['displayName'],
                                    'record': p2.get('record', '0-0-0'),
                                    'pais': pais2
                                }
                            })
                return combates
        except Exception as e:
            st.error(f"Error obteniendo UFC: {e}")
            return []
