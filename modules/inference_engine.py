# modules/inference_engine.py
import numpy as np

class InferenceEngine:
    """
    Motor que aplica reglas de apostador profesional
    """
    
    def __init__(self, team_knowledge):
        self.knowledge = team_knowledge
        
        # REGLAS DEL APOSTADOR PROFESIONAL
        self.rules = [
            {
                'name': 'Favorito en casa contra débil',
                'condition': lambda l, v, ld, vd: 
                    ld.get('victorias', 50) > 70 and vd.get('victorias', 50) < 30,
                'action': 'local_gana',
                'confidence': 'ALTA',
                'reason': 'Local muy fuerte en casa contra visitante débil'
            },
            {
                'name': 'Equipo grande siempre anota',
                'condition': lambda l, v, ld, vd:
                    'top' in str(ld) and 'anota' in str(vd),
                'action': 'btts',
                'confidence': 'ALTA',
                'reason': 'Equipo grande anota, rival también suele anotar'
            },
            {
                'name': 'Visitante motivado vs local relajado',
                'condition': lambda l, v, ld, vd:
                    vd.get('necesita_puntos', False) and not ld.get('necesita_puntos', True),
                'action': 'visitante_gana_o_empata',
                'confidence': 'MEDIA',
                'reason': 'Visitante tiene más necesidad de ganar'
            },
            {
                'name': 'Partido de muchos goles históricamente',
                'condition': lambda l, v, ld, vd:
                    ld.get('goles', 1.5) + vd.get('goles', 1.2) > 3.0,
                'action': 'over_2_5',
                'confidence': 'ALTA',
                'reason': 'Historial de goles entre estos equipos'
            },
            {
                'name': 'Local goleador vs visitante que recibe muchos',
                'condition': lambda l, v, ld, vd:
                    ld.get('goles', 1.5) > 2.0 and vd.get('recibe', 1.2) > 1.8,
                'action': 'local_gana_y_over',
                'confidence': 'MEDIA',
                'reason': 'Local anota mucho y visitante recibe muchos'
            },
            {
                'name': 'Equipos que siempre se anotan mutuamente',
                'condition': lambda l, v, ld, vd:
                    ld.get('btts', 50) > 60 and vd.get('btts', 50) > 60,
                'action': 'btts',
                'confidence': 'ALTA',
                'reason': 'Ambos equipos suelen anotar en sus partidos'
            },
            {
                'name': 'Liga de pocos goles',
                'condition': lambda l, v, ld, vd, league_data:
                    league_data.get('goles_promedio', 2.5) < 2.3,
                'action': 'under_2_5',
                'confidence': 'MEDIA',
                'reason': 'Liga con pocos goles históricamente'
            },
            {
                'name': 'Liga de muchos goles',
                'condition': lambda l, v, ld, vd, league_data:
                    league_data.get('goles_promedio', 2.5) > 2.8,
                'action': 'over_2_5',
                'confidence': 'ALTA',
                'reason': 'Liga con muchos goles históricamente'
            },
            {
                'name': 'Local muy fuerte en liga localista',
                'condition': lambda l, v, ld, vd, league_data:
                    league_data.get('local_ventaja', 50) > 60 and ld.get('victorias', 50) > 60,
                'action': 'local_gana',
                'confidence': 'ALTA',
                'reason': 'Liga muy localista y local fuerte'
            }
        ]
    
    def analyze(self, home_team, away_team, home_stats, away_stats, league_data):
        """
        Aplica todas las reglas y determina la mejor apuesta
        """
        resultados = []
        
        for rule in self.rules:
            try:
                # Verificar si la regla aplica
                if rule['condition'](home_team, away_team, home_stats, away_stats, league_data):
                    resultados.append({
                        'apuesta': rule['action'],
                        'confianza': rule['confidence'],
                        'razon': rule['reason']
                    })
            except:
                # Si la regla falla, ignorar
                pass
        
        return resultados
    
    def get_best_bet(self, home_team, away_team, home_stats, away_stats, league_data):
        """
        Determina la mejor apuesta basada en reglas y estadísticas
        """
        reglas_aplicadas = self.analyze(home_team, away_team, home_stats, away_stats, league_data)
        
        # Mapeo de acciones a nombres de mercado
        market_map = {
            'local_gana': 'Gana Local',
            'visitante_gana': 'Gana Visitante',
            'visitante_gana_o_empata': 'Visitante o Empate (X2)',
            'local_gana_o_empata': 'Local o Empate (1X)',
            'btts': 'Ambos anotan (BTTS)',
            'over_2_5': 'Over 2.5 goles',
            'under_2_5': 'Under 2.5 goles',
            'local_gana_y_over': 'Gana Local + Over 2.5',
            'visitante_gana_y_over': 'Gana Visitante + Over 2.5'
        }
        
        if not reglas_aplicadas:
            return {
                'market': 'Over 1.5 goles',
                'confidence': 'BAJA',
                'reason': 'Sin reglas claras, apuesta conservadora',
                'probability': 0.70
            }
        
        # Contar frecuencias de apuestas
        from collections import Counter
        apuestas = [r['apuesta'] for r in reglas_aplicadas]
        mas_comun = Counter(apuestas).most_common(1)[0][0]
        
        # Obtener la regla de mayor confianza para esa apuesta
        mejor_regla = max(
            [r for r in reglas_aplicadas if r['apuesta'] == mas_comun],
            key=lambda x: {'ALTA': 3, 'MEDIA': 2, 'BAJA': 1}[x['confianza']]
        )
        
        # Calcular probabilidad base
        prob_base = {
            'ALTA': 0.75,
            'MEDIA': 0.60,
            'BAJA': 0.50
        }[mejor_regla['confianza']]
        
        return {
            'market': market_map.get(mas_comun, 'Over 1.5 goles'),
            'confidence': mejor_regla['confianza'],
            'reason': mejor_regla['razon'],
            'probability': prob_base
        }
