from .team_matcher import TeamMatcher
from .montecarlo import run_simulation

class MatchAnalyzer:
    def __init__(self, api_key):
        self.matcher = TeamMatcher(api_key)
    
    def analyze_match(self, home_name, away_name, league_hint=None):
        """Analiza un partido y genera TODOS los mercados posibles"""
        
        # Buscar equipos
        home_team = self.matcher.find_team(home_name, league_hint)
        away_team = self.matcher.find_team(away_name, league_hint)
        
        # Obtener estadísticas reales si es posible
        if home_team and away_team:
            # Aquí podrías obtener stats reales de la API
            # Por ahora usamos valores por defecto
            probs = run_simulation()
        else:
            probs = run_simulation()
        
        # Generar TODOS los mercados
        markets = self._generate_all_markets(probs)
        
        return {
            'home_team': home_team['name'] if home_team else home_name,
            'away_team': away_team['name'] if away_team else away_name,
            'home_found': home_team is not None,
            'away_found': away_team is not None,
            'markets': markets,
            'probabilidades': probs,
            'stats': {
                'goles_promedio': probs['goles_promedio'],
                'prob_over_5.5': probs['over_5.5']
            }
        }
    
    def _generate_all_markets(self, probs):
        """Genera lista completa de mercados con probabilidades"""
        markets = [
            # Resultado final
            {'name': 'Gana Local', 'prob': probs['local_gana'], 'category': '1X2'},
            {'name': 'Empate', 'prob': probs['empate'], 'category': '1X2'},
            {'name': 'Gana Visitante', 'prob': probs['visitante_gana'], 'category': '1X2'},
            
            # Doble oportunidad
            {'name': 'Local o Empate (1X)', 'prob': probs['local_gana'] + probs['empate'], 'category': 'Doble Oportunidad'},
            {'name': 'Visitante o Empate (X2)', 'prob': probs['visitante_gana'] + probs['empate'], 'category': 'Doble Oportunidad'},
            
            # Totales de goles
            {'name': 'Over 0.5 goles', 'prob': probs['over_0.5'], 'category': 'Totales'},
            {'name': 'Over 1.5 goles', 'prob': probs['over_1.5'], 'category': 'Totales'},
            {'name': 'Over 2.5 goles', 'prob': probs['over_2.5'], 'category': 'Totales'},
            {'name': 'Over 3.5 goles', 'prob': probs['over_3.5'], 'category': 'Totales'},
            {'name': 'Over 4.5 goles', 'prob': probs['over_4.5'], 'category': 'Totales'},
            {'name': 'Over 5.5 goles', 'prob': probs['over_5.5'], 'category': 'Totales (Especial)'},
            
            # Primer tiempo
            {'name': 'Over 0.5 goles (1T)', 'prob': probs['over_0.5_1t'], 'category': 'Primer Tiempo'},
            {'name': 'Over 1.5 goles (1T)', 'prob': probs['over_1.5_1t'], 'category': 'Primer Tiempo'},
            {'name': 'Ambos anotan (1T)', 'prob': probs['btts_1t'], 'category': 'Primer Tiempo'},
            
            # BTTS
            {'name': 'Ambos anotan (BTTS)', 'prob': probs['btts'], 'category': 'BTTS'},
            {'name': 'No anotan ambos', 'prob': 1 - probs['btts'], 'category': 'BTTS'},
            
            # Handicaps / Goleadas
            {'name': 'Local gana por 2+ goles', 'prob': probs['local_gana_por_2+'], 'category': 'Handicap'},
            {'name': 'Visitante gana por 2+ goles', 'prob': probs['visitante_gana_por_2+'], 'category': 'Handicap'},
            {'name': 'Local marca 3+ goles', 'prob': probs['local_marca_3+'], 'category': 'Goleador'},
            {'name': 'Visitante marca 3+ goles', 'prob': probs['visitante_marca_3+'], 'category': 'Goleador'},
            
            # Combinados populares
            {'name': 'Gana Local + Over 2.5', 
             'prob': probs['local_gana'] * probs['over_2.5'] * 1.1, 
             'category': 'Combinado'},
            {'name': 'Gana Visitante + Over 2.5', 
             'prob': probs['visitante_gana'] * probs['over_2.5'] * 1.1, 
             'category': 'Combinado'},
            {'name': 'BTTS + Over 2.5', 
             'prob': probs['btts'] * probs['over_2.5'] * 1.1, 
             'category': 'Combinado'},
        ]
        return sorted(markets, key=lambda x: x['prob'], reverse=True)
