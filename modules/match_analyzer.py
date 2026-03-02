# modules/match_analyzer.py
import numpy as np
from modules.montecarlo import run_simulations
from modules.team_matcher import TeamMatcher

class MatchAnalyzer:
    def __init__(self):
        self.matcher = TeamMatcher()
    
    def analyze_match(self, home_name, away_name, league_name=None):
        """Analiza un partido y devuelve las mejores opciones"""
        
        # 1. Encontrar equipos en la API
        home_team = self.matcher.match_team_from_image(home_name, league_name)
        away_team = self.matcher.match_team_from_image(away_name, league_name)
        
        if not home_team or not away_team:
            return {
                'error': f"No se pudieron identificar: {home_name if not home_team else ''} {away_name if not away_team else ''}",
                'home_found': home_team is not None,
                'away_found': away_team is not None
            }
        
        # 2. Obtener estadísticas reales
        from modules.cerebro import extraer_stats_avanzadas
        stats_h = extraer_stats_avanzadas(home_team['id'])
        stats_a = extraer_stats_avanzadas(away_team['id'])
        
        if not stats_h or not stats_a:
            return {'error': 'No se pudieron obtener estadísticas'}
        
        # 3. Preparar stats para Monte Carlo
        stats = {
            "home": {
                "attack": stats_h.get("attack_power", 1.2) * 40,  # Escalar
                "defense": stats_h.get("defense_weakness", 1.2) * 40
            },
            "away": {
                "attack": stats_a.get("attack_power", 1.2) * 40,
                "defense": stats_a.get("defense_weakness", 1.2) * 40
            }
        }
        
        # 4. Ejecutar simulaciones
        probs = run_simulations(stats)
        
        # 5. Analizar todos los mercados
        mercados = self.evaluate_all_markets(probs, stats_h, stats_a)
        
        # 6. Determinar la mejor opción
        mejor_opcion = self.find_best_option(mercados)
        
        return {
            'home_team': home_team['name'],
            'away_team': away_team['name'],
            'home_id': home_team['id'],
            'away_id': away_team['id'],
            'probabilidades': probs,
            'mercados': mercados,
            'mejor_opcion': mejor_opcion,
            'stats': {'local': stats_h, 'visitante': stats_a}
        }
    
    def evaluate_all_markets(self, probs, stats_h, stats_a):
        """Evalúa todos los mercados posibles"""
        
        mercados = []
        
        # Resultado final
        mercados.append({
            'nombre': 'Gana Local',
            'probabilidad': probs.get('Resultado Final (Local)', 0),
            'tipo': '1X2',
            'valor': 'local'
        })
        mercados.append({
            'nombre': 'Empate',
            'probabilidad': probs.get('Resultado Final (Empate)', 0),
            'tipo': '1X2',
            'valor': 'empate'
        })
        mercados.append({
            'nombre': 'Gana Visitante',
            'probabilidad': probs.get('Resultado Final (Visitante)', 0),
            'tipo': '1X2',
            'valor': 'visitante'
        })
        
        # Doble oportunidad
        mercados.append({
            'nombre': 'Local o Empate (1X)',
            'probabilidad': probs.get('Resultado Final (Local)', 0) + probs.get('Resultado Final (Empate)', 0),
            'tipo': 'dobles',
            'valor': '1X'
        })
        mercados.append({
            'nombre': 'Visitante o Empate (X2)',
            'probabilidad': probs.get('Resultado Final (Visitante)', 0) + probs.get('Resultado Final (Empate)', 0),
            'tipo': 'dobles',
            'valor': 'X2'
        })
        
        # Totales de goles
        mercados.append({
            'nombre': 'Over 0.5 goles',
            'probabilidad': 1 - probs.get('Total Goles Under 2.5', 0.3),  # Aproximación
            'tipo': 'totales',
            'valor': 'over_0.5'
        })
        mercados.append({
            'nombre': 'Over 1.5 goles',
            'probabilidad': probs.get('Total Goles Over 1.5', 0.5),
            'tipo': 'totales',
            'valor': 'over_1.5'
        })
        mercados.append({
            'nombre': 'Over 2.5 goles',
            'probabilidad': 1 - probs.get('Total Goles Under 2.5', 0.5),
            'tipo': 'totales',
            'valor': 'over_2.5'
        })
        mercados.append({
            'nombre': 'Under 2.5 goles',
            'probabilidad': probs.get('Total Goles Under 2.5', 0.5),
            'tipo': 'totales',
            'valor': 'under_2.5'
        })
        
        # Ambos equipos anotan
        mercados.append({
            'nombre': 'Ambos equipos anotan (BTTS)',
            'probabilidad': probs.get('Ambos Anotan', 0.5),
            'tipo': 'btts',
            'valor': 'si'
        })
        mercados.append({
            'nombre': 'Al menos uno no anota',
            'probabilidad': 1 - probs.get('Ambos Anotan', 0.5),
            'tipo': 'btts',
            'valor': 'no'
        })
        
        # Combinados (Local + Over)
        prob_local = probs.get('Resultado Final (Local)', 0)
        prob_over = probs.get('Total Goles Over 1.5', 0.5)
        mercados.append({
            'nombre': 'Gana Local + Over 1.5',
            'probabilidad': prob_local * prob_over * 1.1,  # Correlación positiva
            'tipo': 'combinado',
            'valor': 'local_over1.5'
        })
        
        prob_visit = probs.get('Resultado Final (Visitante)', 0)
        mercados.append({
            'nombre': 'Gana Visitante + Over 1.5',
            'probabilidad': prob_visit * prob_over * 1.1,
            'tipo': 'combinado',
            'valor': 'visit_over1.5'
        })
        
        # Primer tiempo
        mercados.append({
            'nombre': 'Over 0.5 goles (1T)',
            'probabilidad': 0.65,  # Estimado, idealmente calcular de stats
            'tipo': 'primer_tiempo',
            'valor': 'over_0.5_1t'
        })
        
        return sorted(mercados, key=lambda x: x['probabilidad'], reverse=True)
    
    def find_best_option(self, mercados):
        """Encuentra la mejor opción basada en probabilidad y tipo"""
        if not mercados:
            return None
        
        # Tomar top 3
        top = mercados[:5]
        
        # Buscar el que tenga mejor relación probabilidad/riesgo
        best = None
        best_score = 0
        
        for m in top:
            # Score ponderado por tipo de mercado
            score = m['probabilidad']
            
            # Bonificación para mercados más seguros
            if m['tipo'] in ['dobles', 'totales'] and 'over_0.5' in m['valor']:
                score *= 1.2  # Mercados más probables
            
            if score > best_score:
                best_score = score
                best = m
        
        return best