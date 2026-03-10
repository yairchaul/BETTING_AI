import math
import numpy as np
import requests
from scipy.stats import poisson, norm

class StatsEngine:
    """
    Motor estadístico que consulta APIs reales y calcula probabilidades.
    """
    
    def __init__(self):
        # Configuración de APIs (simulada por ahora)
        self.api_keys = {
            'FOOTBALL': 'tu_api_key',
            'NBA': 'tu_api_key',
            'UFC': 'tu_api_key'
        }
    
    def enriquecer(self, evento):
        """
        Dispatcher principal - llama al método correcto según el deporte.
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
        # Aquí iría la llamada a API real
        # Por ahora usamos datos simulados
        stats_local = {'gf': 1.5, 'ga': 1.2}
        stats_visit = {'gf': 1.3, 'ga': 1.4}
        
        lambda_local = stats_local['gf']
        lambda_visit = stats_visit['gf']
        
        evento.stats = {
            'local_gf': lambda_local,
            'local_ga': stats_local['ga'],
            'visitante_gf': lambda_visit,
            'visitante_ga': stats_visit['ga']
        }
        
        # Calcular probabilidades de goles
        prob_local = [poisson.pmf(i, lambda_local) for i in range(6)]
        prob_visit = [poisson.pmf(i, lambda_visit) for i in range(6)]
        
        # BTTS
        prob_l_marcar = 1 - prob_local[0]
        prob_v_marcar = 1 - prob_visit[0]
        btts_yes = prob_l_marcar * prob_v_marcar
        
        # Overs
        over_1_5 = self._calcular_over(prob_local, prob_visit, 1.5)
        over_2_5 = self._calcular_over(prob_local, prob_visit, 2.5)
        over_3_5 = self._calcular_over(prob_local, prob_visit, 3.5)
        
        # Over 1.5 Primer Tiempo
        lambda_1t = (lambda_local + lambda_visit) * 0.35
        over_1_5_1t = 1 - poisson.pmf(0, lambda_1t) - poisson.pmf(1, lambda_1t)
        over_1_5_1t = min(0.60, over_1_5_1t)
        
        # Probabilidades 1X2 (simplificado)
        total = lambda_local + lambda_visit
        prob_home = lambda_local / total * 0.55
        prob_away = lambda_visit / total * 0.45
        prob_draw = 1 - prob_home - prob_away
        
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
    
    def _calcular_nba(self, evento):
        """Calcula probabilidades para NBA (Spread, Totals, Moneyline)"""
        # Extraer odds de los datos crudos
        datos = evento.datos_crudos
        
        # Calcular probabilidades implícitas de las cuotas
        prob_home_ml = self._american_to_prob(datos.get('home_ml', '-110'))
        prob_away_ml = self._american_to_prob(datos.get('away_ml', '-110'))
        total_prob = prob_home_ml + prob_away_ml
        prob_home_ml_norm = prob_home_ml / total_prob
        prob_away_ml_norm = prob_away_ml / total_prob
        
        # Probabilidad de spread (simulada - idealmente de API)
        spread_valor = datos.get('home_spread', '0')
        prob_spread = 0.55 if float(spread_valor) > 0 else 0.45
        
        # Probabilidad de over/under
        prob_over = 0.52  # Simulado
        
        evento.mercados = {
            'prob_spread': prob_spread,
            'prob_over': prob_over,
            'prob_under': 1 - prob_over,
            'prob_home_ml': prob_home_ml_norm,
            'prob_away_ml': prob_away_ml_norm,
            'spread_valor': datos.get('home_spread', '0'),
            'total_valor': datos.get('home_total', '0'),
            'ou': datos.get('home_ou', 'O')
        }
        return evento
    
    def _calcular_ufc(self, evento):
        """Calcula probabilidades para UFC"""
        # Implementar para UFC
        evento.mercados = {
            'prob_local': 0.65,
            'prob_visitante': 0.35,
            'ko_tko': 0.45,
            'submission': 0.25,
            'decision': 0.30
        }
        return evento
    
    def _calcular_over(self, p_local, p_visit, limite):
        """Calcula probabilidad de que la suma de goles supere un límite"""
        total = 0
        for i in range(len(p_local)):
            for j in range(len(p_visit)):
                if i + j > limite:
                    total += p_local[i] * p_visit[j]
        return min(total, 0.99)
    
    def _american_to_prob(self, odds):
        """Convierte odds americanos a probabilidad"""
        try:
            odds = str(odds).replace('+', '')
            odds = int(odds)
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return -odds / (-odds + 100)
        except:
            return 0.5
