"""
CALCULADOR PROBABILIDADES FÚTBOL - Basado en últimos 5 partidos
CORREGIDO: Las probabilidades de victoria ahora suman 100%
"""
import streamlit as st

class CalculadorProbabilidadesFutbol:
    """
    Calcula probabilidades reales basadas en los últimos 5 partidos
    """
    
    @staticmethod
    def calcular(stats_local, stats_visitante):
        """
        Calcula las probabilidades reales basadas en los últimos 5 encuentros.
        
        Args:
            stats_local: Estadísticas del equipo local
            stats_visitante: Estadísticas del equipo visitante
            
        Returns:
            Diccionario con todas las probabilidades calculadas
        """
        # Extraer listas de goles
        ultimos_local = stats_local.get('ultimos_5', [])
        ultimos_visit = stats_visitante.get('ultimos_5', [])
        
        # Verificar que hay datos
        if len(ultimos_local) == 0 or len(ultimos_visit) == 0:
            return {
                'prob_ht': 0,
                'prob_btts': 0,
                'prob_over15': 0,
                'prob_over25': 0,
                'prob_over35': 0,
                'prob_local': 50,
                'prob_visitante': 50,
                'lesionados_local': [],
                'lesionados_visit': [],
                'victorias_local': 0,
                'victorias_visit': 0
            }
        
        goles_f_l = [p.get('goles_favor', 0) for p in ultimos_local]
        goles_c_l = [p.get('goles_contra', 0) for p in ultimos_local]
        goles_ht_l = [p.get('goles_ht', 0) for p in ultimos_local]
        
        goles_f_v = [p.get('goles_favor', 0) for p in ultimos_visit]
        goles_c_v = [p.get('goles_contra', 0) for p in ultimos_visit]
        goles_ht_v = [p.get('goles_ht', 0) for p in ultimos_visit]

        # --- CÁLCULOS DE PROBABILIDAD ---
        total_partidos = 10  # 5 local + 5 visitante
        
        # Probabilidad Over 1.5 HT (Primer Tiempo)
        hits_ht = sum(1 for g in (goles_ht_l + goles_ht_v) if g >= 2)
        prob_ht = (hits_ht / total_partidos * 100) if total_partidos > 0 else 0

        # Probabilidad BTTS (Ambos Anotan)
        hits_btts_l = sum(1 for f, c in zip(goles_f_l, goles_c_l) if f > 0 and c > 0)
        hits_btts_v = sum(1 for f, c in zip(goles_f_v, goles_c_v) if f > 0 and c > 0)
        prob_btts = ((hits_btts_l + hits_btts_v) / total_partidos * 100) if total_partidos > 0 else 0

        # Probabilidades Over 1.5, 2.5, 3.5 FT
        totales_l = [f + c for f, c in zip(goles_f_l, goles_c_l)]
        totales_v = [f + c for f, c in zip(goles_f_v, goles_c_v)]
        todos_los_totales = totales_l + totales_v
        
        prob_over15 = (sum(1 for t in todos_los_totales if t > 1.5) / total_partidos * 100) if total_partidos > 0 else 0
        prob_over25 = (sum(1 for t in todos_los_totales if t > 2.5) / total_partidos * 100) if total_partidos > 0 else 0
        prob_over35 = (sum(1 for t in todos_los_totales if t > 3.5) / total_partidos * 100) if total_partidos > 0 else 0

        # 🔥 CORRECCIÓN: Probabilidad de Victoria (NORMALIZADA)
        victorias_local = stats_local.get('victorias_recientes', 0)
        victorias_visit = stats_visitante.get('victorias_recientes', 0)
        
        # Calcular probabilidades base
        prob_local_base = (victorias_local / 5 * 100) if victorias_local > 0 else 0
        prob_visit_base = (victorias_visit / 5 * 100) if victorias_visit > 0 else 0
        
        # Añadir factor localía (3%)
        prob_local_con_localia = prob_local_base + 3
        
        # Calcular empate (partidos que no ganó nadie)
        empates_local = 5 - victorias_local - sum(1 for p in ultimos_local if p.get('resultado') == 'PERDIÓ')
        empates_visit = 5 - victorias_visit - sum(1 for p in ultimos_visit if p.get('resultado') == 'PERDIÓ')
        prob_empate_base = ((empates_local + empates_visit) / 10 * 100) if total_partidos > 0 else 0
        
        # 🔥 NORMALIZAR para que sumen 100%
        total_prob = prob_local_con_localia + prob_visit_base + prob_empate_base
        
        if total_prob > 0:
            prob_local = (prob_local_con_localia / total_prob) * 100
            prob_visit = (prob_visit_base / total_prob) * 100
            prob_empate = (prob_empate_base / total_prob) * 100
        else:
            prob_local = 50
            prob_visit = 50
            prob_empate = 0

        # Lesiones
        lesionados_l = stats_local.get('lesionados', [])
        lesionados_v = stats_visitante.get('lesionados', [])

        return {
            'prob_ht': round(prob_ht, 1),
            'prob_btts': round(prob_btts, 1),
            'prob_over15': round(prob_over15, 1),
            'prob_over25': round(prob_over25, 1),
            'prob_over35': round(prob_over35, 1),
            'prob_local': round(prob_local, 1),
            'prob_visitante': round(prob_visit, 1),
            'prob_empate': round(prob_empate, 1),
            'lesionados_local': lesionados_l,
            'lesionados_visit': lesionados_v,
            'victorias_local': victorias_local,
            'victorias_visit': victorias_visit
        }
