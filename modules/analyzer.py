from .team_matcher import TeamMatcher
from .montecarlo import run_simulation

class MatchAnalyzer:
    def __init__(self, api_key):
        self.matcher = TeamMatcher(api_key)
    
    def analyze_match(self, home_name, away_name, league_hint=None):
        """Analiza un partido y genera todos los mercados"""
        
        # Buscar equipos
        home_team = self.matcher.find_team(home_name, league_hint)
        away_team = self.matcher.find_team(away_name, league_hint)
        
        # Simular probabilidades
        probs = run_simulation()
        
        # Generar mercados
        markets = self._generate_markets(probs)
        
        return {
            'home_team': home_team['name'] if home_team else home_name,
            'away_team': away_team['name'] if away_team else away_name,
            'home_found': home_team is not None,
            'away_found': away_team is not None,
            'markets': markets,
            'probabilidades': probs
        }
    
    def _generate_markets(self, probs):
        """Genera lista de mercados con probabilidades"""
        markets = [
            {'name': 'Gana Local', 'prob': probs['local_gana']},
            {'name': 'Empate', 'prob': probs['empate']},
            {'name': 'Gana Visitante', 'prob': probs['visitante_gana']},
            {'name': 'Local o Empate (1X)', 'prob': probs['local_gana'] + probs['empate']},
            {'name': 'Visitante o Empate (X2)', 'prob': probs['visitante_gana'] + probs['empate']},
            {'name': 'Over 1.5 goles', 'prob': probs['over_1.5']},
            {'name': 'Over 2.5 goles', 'prob': probs['over_2.5']},
            {'name': 'Under 2.5 goles', 'prob': probs['under_2.5']},
            {'name': 'Ambos anotan (BTTS)', 'prob': probs['btts']}
        ]
        return sorted(markets, key=lambda x: x['prob'], reverse=True)
