"""
NBA HISTORICAL DATA - Clase para obtener datos históricos (sin Streamlit)
"""
import requests

class NBAHistoricalData:
    """
    Obtiene partidos históricos de la API de ESPN
    SIN dependencias de Streamlit
    """
    
    def __init__(self):
        self.base_url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    def get_games_by_date(self, date):
        """
        Obtiene partidos de una fecha específica
        date: string en formato YYYYMMDD
        """
        try:
            url = f"{self.base_url}/scoreboard?dates={date}&limit=100"
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
                        
                        if competition.get('status', {}).get('type', {}).get('completed'):
                            home_score = int(home.get('score', 0))
                            away_score = int(away.get('score', 0))
                            
                            if home_score > away_score:
                                ganador = home['team']['displayName']
                            else:
                                ganador = away['team']['displayName']
                            
                            diferencia = home_score - away_score
                        else:
                            ganador = "Pendiente"
                            diferencia = 0
                            home_score = 0
                            away_score = 0
                        
                        odds_data = {
                            'spread': 0,
                            'over_under': 0,
                            'moneyline_local': 'N/A',
                            'moneyline_visit': 'N/A'
                        }
                        
                        if 'odds' in competition and competition['odds']:
                            odds = competition['odds'][0]
                            odds_data = {
                                'moneyline_local': odds.get('homeTeamOdds', {}).get('american', 'N/A'),
                                'moneyline_visit': odds.get('awayTeamOdds', {}).get('american', 'N/A'),
                                'spread': odds.get('spread', 0),
                                'over_under': odds.get('overUnder', 0)
                            }
                        
                        partidos.append({
                            'id': event.get('id'),
                            'fecha': event.get('date', '')[:10],
                            'local': home['team']['displayName'],
                            'visitante': away['team']['displayName'],
                            'puntos_local': home_score,
                            'puntos_visit': away_score,
                            'diferencia': diferencia,
                            'ganador': ganador,
                            'completado': competition.get('status', {}).get('type', {}).get('completed', False),
                            'records': {
                                'local': home.get('records', [{}])[0].get('summary', '0-0') if home.get('records') else '0-0',
                                'visitante': away.get('records', [{}])[0].get('summary', '0-0') if away.get('records') else '0-0'
                            },
                            'odds': odds_data
                        })
                return partidos
        except Exception as e:
            print(f"Error: {e}")
            return []
