# -*- coding: utf-8 -*-
"""
Advanced Market Reasoning - Detecta perfiles de partido
"""

class AdvancedMarketReasoning:
    """
    Clasifica partidos en perfiles (over_game, under_game, btts_game, etc.)
    """
    
    def __init__(self):
        self.profiles = {}
    
    def detect_profile(self, markets, stats_home, stats_away):
        """
        Detecta el perfil del partido basado en estadísticas
        """
        profile = {
            'type': 'balanced',
            'confidence': 0.5,
            'key_markets': []
        }
        
        home_power = stats_home.get('power', 70)
        away_power = stats_away.get('power', 70)
        expected_total = markets['expected_goals']['total']
        
        # Detectar over_game
        if expected_total > 3.0:
            profile['type'] = 'over_game'
            profile['confidence'] = min(0.9, (expected_total - 2.5) / 2)
            profile['key_markets'] = ['over2_5', 'over3_5', 'btts_yes']
        
        # Detectar under_game
        elif expected_total < 2.2:
            profile['type'] = 'under_game'
            profile['confidence'] = min(0.9, (2.5 - expected_total) / 1.5)
            profile['key_markets'] = ['under2_5', 'btts_no']
        
        # Detectar btts_game
        elif markets['btts'] > 0.65:
            profile['type'] = 'btts_game'
            profile['confidence'] = markets['btts']
            profile['key_markets'] = ['btts_yes', 'gg']
        
        # Detectar one_side_game (favorito claro)
        elif abs(home_power - away_power) > 20:
            favorite = 'home' if home_power > away_power else 'away'
            profile['type'] = f'{favorite}_dominant'
            profile['confidence'] = abs(home_power - away_power) / 40
            profile['key_markets'] = [f'win_{favorite}', 'handicap']
        
        return profile
    
    def get_recommended_markets(self, profile, markets):
        """
        Recomienda mercados según el perfil del partido
        """
        recommendations = []
        
        if profile['type'] == 'over_game':
            recommendations.extend([
                ('Over 2.5', markets['overs']['over2_5']),
                ('Over 3.5', markets['overs']['over3_5']),
                ('BTTS Sí', markets['btts'])
            ])
        
        elif profile['type'] == 'under_game':
            recommendations.extend([
                ('Under 2.5', 1 - markets['overs']['over2_5']),
                ('BTTS No', 1 - markets['btts'])
            ])
        
        elif profile['type'] == 'btts_game':
            recommendations.append(('BTTS Sí', markets['btts']))
        
        elif 'dominant' in profile['type']:
            favorite = profile['type'].split('_')[0]
            prob = markets['1x2'][favorite]
            recommendations.append((f'Gana {favorite.capitalize()}', prob))
        
        # Ordenar por probabilidad
        return sorted(recommendations, key=lambda x: x[1], reverse=True)
