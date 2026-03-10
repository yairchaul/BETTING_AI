import math
import numpy as np
from scipy.stats import poisson, norm

class StatsEngine:
    """
    Motor estadístico que calcula probabilidades reales basadas en datos.
    Convierte nombres de equipos en probabilidades matemáticas.
    """
    
    def __init__(self):
        # Base de datos simulada (esto se reemplazará con scraping real)
        self.base_datos = {
            'FUTBOL': {
                'Galatasaray': {'gf': 1.9, 'ga': 1.1},
                'Liverpool': {'gf': 2.2, 'ga': 0.8},
                'Barcelona': {'gf': 2.1, 'ga': 0.9},
                'Real Madrid': {'gf': 2.3, 'ga': 0.7},
                'Arsenal': {'gf': 2.0, 'ga': 1.0},
                'Chelsea': {'gf': 1.8, 'ga': 1.1},
            },
            'NBA': {
                'Lakers': {'pts': 115.2, 'pts_allowed': 112.8},
                'Celtics': {'pts': 118.5, 'pts_allowed': 110.2},
                'Warriors': {'pts': 116.8, 'pts_allowed': 114.5},
            },
            'UFC': {
                'Piera Rodriguez': {'win_rate': 0.75, 'ko_rate': 0.30},
                'Sam Hughes': {'win_rate': 0.65, 'ko_rate': 0.20},
            }
        }
    
    def enriquecer(self, evento):
        """
        Toma un evento vacío y lo llena con probabilidades calculadas.
        """
        if evento.deporte == 'FUTBOL':
            return self._calcular_futbol(evento)
        elif evento.deporte == 'NBA':
            return self._calcular_nba(evento)
        elif evento.deporte == 'UFC':
            return self._calcular_ufc(evento)
        else:
            return evento
    
    def _calcular_futbol(self, evento):
        """Calcula probabilidades para fútbol usando Poisson"""
        # Obtener estadísticas de los equipos
        stats_local = self.base_datos['FUTBOL'].get(evento.local, {'gf': 1.5, 'ga': 1.3})
        stats_visit = self.base_datos['FUTBOL'].get(evento.visitante, {'gf': 1.4, 'ga': 1.4})
        
        # Calcular tasas de goles esperados
        lambda_local = stats_local['gf']
        lambda_visit = stats_visit['gf']
        
        # Guardar stats base
        evento.stats = {
            'local': stats_local,
            'visitante': stats_visit
        }
        
        # Calcular probabilidades de goles exactos
        prob_local = [poisson.pmf(i, lambda_local) for i in range(6)]
        prob_visit = [poisson.pmf(i, lambda_visit) for i in range(6)]
        
        # Calcular BTTS (Ambos marcan)
        prob_l_marcar = 1 - prob_local[0]
        prob_v_marcar = 1 - prob_visit[0]
        btts_yes = prob_l_marcar * prob_v_marcar
        
        # Calcular Overs
        over_1_5 = self._calcular_over(prob_local, prob_visit, 1.5)
        over_2_5 = self._calcular_over(prob_local, prob_visit, 2.5)
        over_3_5 = self._calcular_over(prob_local, prob_visit, 3.5)
        
        # Over 1.5 Primer Tiempo (35% de los goles)
        lambda_1t = (lambda_local + lambda_visit) * 0.35
        over_1_5_1t = 1 - poisson.pmf(0, lambda_1t) - poisson.pmf(1, lambda_1t)
        over_1_5_1t = min(0.60, over_1_5_1t)
        
        # Calcular probabilidades 1X2 (simplificado)
        total = lambda_local + lambda_visit
        prob_home = lambda_local / total * 0.55
        prob_away = lambda_visit / total * 0.45
        prob_draw = 1 - prob_home - prob_away
        
        # Guardar todos los mercados calculados
        evento.mercados = {
            'over_1_5': over_1_5,
            'over_2_5': over_2_5,
            'over_3_5': over_3_5,
            'btts_yes': btts_yes,
            'btts_no': 1 - btts_yes,
            'over_1_5_1t': over_1_5_1t,
            'prob_local': prob_home,
            'prob_draw': prob_draw,
            'prob_visitante': prob_away
        }
        
        return evento
    
    def _calcular_over(self, p_local, p_visit, limite):
        """Calcula probabilidad de que la suma de goles supere un límite"""
        total = 0
        for i in range(len(p_local)):
            for j in range(len(p_visit)):
                if i + j > limite:
                    total += p_local[i] * p_visit[j]
        return min(total, 0.99)  # Cap at 0.99
    
    def _calcular_nba(self, evento):
        """Calcula probabilidades para NBA"""
        # Implementación para NBA
        evento.mercados = {
            'spread_cover': 0.55,
            'total_points_over': 0.52,
            'prob_local': 0.60,
            'prob_visitante': 0.40
        }
        return evento
    
    def _calcular_ufc(self, evento):
        """Calcula probabilidades para UFC"""
        # Implementación para UFC
        evento.mercados = {
            'prob_local': 0.65,
            'prob_visitante': 0.35,
            'ko_tko': 0.45,
            'submission': 0.25,
            'decision': 0.30
        }
        return evento
