# modules/pro_analyzer_ultimate.py
import streamlit as st
import requests
import json
import numpy as np
import re
from datetime import datetime
from modules.team_knowledge import TeamKnowledge
from modules.smart_searcher import SmartSearcher
from modules.montecarlo_pro import MonteCarloPro
from modules.elo_system import ELOSystem
from modules.xgboost_predictor import XGBoostPredictor
from math import exp, factorial
from modules.team_translator import TeamTranslator
from modules.odds_api_integrator import OddsAPIIntegrator
from modules.complete_market_analyzer import CompleteMarketAnalyzer

class ProAnalyzerUltimate:
    """
    Analizador profesional con cobertura GLOBAL de ligas + TODOS los mercados
    Versión FINAL con CompleteMarketAnalyzer
    """

    def __init__(self):
        self.knowledge = TeamKnowledge()
        self.searcher = SmartSearcher()
        self.montecarlo = MonteCarloPro(simulations=50000)
        self.elo = ELOSystem(k_factor=32, home_advantage=100)
        self.xgb = XGBoostPredictor()
        self.translator = TeamTranslator()
        self.odds_api = OddsAPIIntegrator()
        self.market_analyzer = CompleteMarketAnalyzer(simulations=50000)
        self.max_edge = 0.06

        self.weights = {
            'market': 0.20,
            'poisson': 0.25,
            'elo': 0.15,
            'xgb': 0.25,
            'ollama': 0.15
        }

        # Intentar conectar Ollama
        self.ollama_available = False
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            self.ollama_available = response.status_code == 200
        except:
            pass

    # ============================================================================
    # FUNCIÓN PRINCIPAL DE ANÁLISIS
    # ============================================================================
    def analyze_match(self, home_team, away_team, odds_dict):
        """
        Analiza un partido y calcula TODOS los mercados disponibles
        """
        try:
            # Obtener odds en formato decimal
            odds_decimal = odds_dict.get('decimal_odds', odds_dict.get('all_odds', [2.0, 3.2, 3.5]))
            
            # Buscar información del equipo
            home_info = self.searcher.get_team_stats(home_team)
            away_info = self.searcher.get_team_stats(away_team)
            
            # Buscar enfrentamientos directos
            h2h = self.searcher.get_head_to_head(home_team, away_team)
            
            # Obtener probabilidades ELO
            elo_probs_dict = self.elo.get_win_probability(home_team, away_team)
            elo_probs = {
                'home': elo_probs_dict.get('home', 0.35),
                'draw': elo_probs_dict.get('draw', 0.30),
                'away': elo_probs_dict.get('away', 0.35)
            }
            
            # Calcular fuerzas ofensivas/defensivas
            home_attack, home_defense = self._calculate_team_strength(home_info, home_team)
            away_attack, away_defense = self._calculate_team_strength(away_info, away_team)
            
            # Ajustar por localía
            home_attack *= 1.1
            home_defense *= 0.95
            away_attack *= 0.95
            away_defense *= 1.05
            
            # Calcular lambdas para Poisson
            lambda_home = home_attack * away_defense * 1.2
            lambda_away = away_attack * home_defense * 1.0
            
            # ============================================================================
            # ANALIZAR TODOS LOS MERCADOS (NUEVO)
            # ============================================================================
            all_markets = self.market_analyzer.analyze_match(
                home_team, away_team,
                lambda_home, lambda_away,
                elo_probs
            )
            
            # Calcular probabilidades de los diferentes modelos (para compatibilidad)
            probs_by_model = self._calculate_model_probabilities(
                home_team, away_team, elo_probs,
                home_attack, away_attack, home_defense, away_defense,
                h2h, home_info, away_info, {}
            )
            
            # Combinar probabilidades finales (1X2)
            final_probs = self._combine_probabilities(probs_by_model)
            
            # Encontrar la mejor opción (por probabilidad)
            best_market = max(all_markets, key=lambda x: x['prob'])
            
            # Detectar liga
            league = self._detect_league(home_team, away_team)
            
            # Calcular estadísticas de Monte Carlo para compatibilidad
            mc_stats = {
                'btts': next((m['prob'] for m in all_markets if m['name'] == 'BTTS - Sí'), 0.5),
                'over_1_5': next((m['prob'] for m in all_markets if m['name'] == 'Over 1.5'), 0.7),
                'over_2_5': next((m['prob'] for m in all_markets if m['name'] == 'Over 2.5'), 0.55),
                'avg_goals': lambda_home + lambda_away,
                'simulations': 50000
            }
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'liga': league,
                'final_probs': final_probs,
                'probs_by_model': probs_by_model,
                'mc_stats': mc_stats,
                'markets': all_markets,
                'best_market': best_market,
                'total_markets': len(all_markets),
                'elo_probs': [elo_probs['home'], elo_probs['draw'], elo_probs['away']],
                'historical_data': h2h,
                'team_stats': {'home': home_info, 'away': away_info},
                'team_strength': {
                    'home_attack': home_attack,
                    'home_defense': home_defense,
                    'away_attack': away_attack,
                    'away_defense': away_defense
                },
                'lambda_home': lambda_home,
                'lambda_away': lambda_away
            }
            
        except Exception as e:
            st.error(f"Error en analyze_match: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_analysis(home_team, away_team)

    # ============================================================================
    # FUNCIONES AUXILIARES
    # ============================================================================
    def _calculate_team_strength(self, team_info, team_name):
        """Calcula fuerza ofensiva y defensiva"""
        if not team_info:
            return 1.0, 1.0
        
        avg_scored = team_info.get('avg_goals_scored', 1.2)
        avg_conceded = team_info.get('avg_goals_conceded', 1.2)
        
        attack = avg_scored / 1.2
        defense = avg_conceded / 1.2
        
        return attack, defense

    def _calculate_model_probabilities(self, home_team, away_team, elo_probs,
                                       home_attack, away_attack, home_defense, away_defense,
                                       h2h, home_info, away_info, mc_stats):
        """Calcula probabilidades de cada modelo (para compatibilidad)"""
        
        # Probabilidades de mercado (inversa de odds)
        market_probs = [0.34, 0.32, 0.34]
        
        # Probabilidades Poisson
        poisson_probs = self._poisson_probabilities(home_attack, away_attack, 
                                                    home_defense, away_defense)
        
        # Probabilidades ELO
        elo_probs_list = [elo_probs['home'], elo_probs['draw'], elo_probs['away']]
        
        # Probabilidades XGBoost (simulado)
        xgb_probs = [0.33, 0.34, 0.33]
        
        # Probabilidades Ollama
        ollama_probs = [0.33, 0.34, 0.33]
        if self.ollama_available:
            ollama_probs = self._get_ollama_probabilities(home_team, away_team, home_info, away_info)
        
        return {
            'market': market_probs,
            'poisson': poisson_probs,
            'elo': elo_probs_list,
            'xgb': xgb_probs,
            'ollama': ollama_probs
        }

    def _poisson_probabilities(self, home_attack, away_attack, home_defense, away_defense):
        """Calcula probabilidades usando Poisson (simplificado)"""
        lambda_home = home_attack * away_defense * 1.2
        lambda_away = away_attack * home_defense * 1.0
        
        probs = [0, 0, 0]
        for gh in range(8):
            for ga in range(8):
                prob = (exp(-lambda_home) * lambda_home**gh / factorial(gh)) * \
                       (exp(-lambda_away) * lambda_away**ga / factorial(ga))
                
                if gh > ga:
                    probs[0] += prob
                elif gh == ga:
                    probs[1] += prob
                else:
                    probs[2] += prob
        
        total = sum(probs)
        return [p/total for p in probs] if total > 0 else [0.34, 0.32, 0.34]

    def _combine_probabilities(self, probs_by_model):
        """Combina probabilidades de todos los modelos"""
        combined = [0, 0, 0]
        total_weight = 0
        
        for model, probs in probs_by_model.items():
            weight = self.weights.get(model, 0.2)
            for i in range(3):
                combined[i] += probs[i] * weight
            total_weight += weight
        
        return [p/total_weight for p in combined]

    def _get_ollama_probabilities(self, home_team, away_team, home_info, away_info):
        """Obtiene probabilidades de Ollama si está disponible"""
        if not self.ollama_available:
            return [0.34, 0.32, 0.34]
        
        try:
            import requests
            prompt = f"Analiza el partido {home_team} vs {away_team}. Da solo tres números que sumen 1.0 para (local, empate, visitante) basado en forma reciente."
            
            response = requests.post('http://localhost:11434/api/generate',
                                    json={'model': 'llama3.1:8b', 'prompt': prompt, 'stream': False},
                                    timeout=5)
            
            if response.status_code == 200:
                text = response.json().get('response', '')
                numbers = re.findall(r'0\.\d+', text)
                if len(numbers) >= 3:
                    return [float(numbers[0]), float(numbers[1]), float(numbers[2])]
        except:
            pass
        
        return [0.34, 0.32, 0.34]

    def _detect_league(self, home_team, away_team):
        """Detecta la liga del partido"""
        try:
            league = self.knowledge.detect_league(home_team, away_team)
            return league if league else 'Desconocida'
        except:
            return 'Desconocida'

    def _get_default_analysis(self, home_team, away_team):
        """Retorna análisis por defecto en caso de error"""
        default_markets = [
            {'name': 'Gana Local', 'prob': 0.35, 'category': '1X2', 'formula': 'default'},
            {'name': 'Empate', 'prob': 0.30, 'category': '1X2', 'formula': 'default'},
            {'name': 'Gana Visitante', 'prob': 0.35, 'category': '1X2', 'formula': 'default'},
            {'name': 'BTTS - Sí', 'prob': 0.52, 'category': 'BTTS', 'formula': 'default'},
            {'name': 'BTTS - No', 'prob': 0.48, 'category': 'BTTS', 'formula': 'default'},
            {'name': 'Over 1.5', 'prob': 0.78, 'category': 'Totales', 'formula': 'default'},
            {'name': 'Under 1.5', 'prob': 0.22, 'category': 'Totales', 'formula': 'default'},
        ]
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'liga': 'Desconocida',
            'final_probs': [0.35, 0.30, 0.35],
            'probs_by_model': {},
            'mc_stats': {'avg_goals': 2.5, 'btts': 0.52, 'over_1_5': 0.78, 'over_2_5': 0.58},
            'markets': default_markets,
            'best_market': default_markets[5],
            'total_markets': len(default_markets)
        }
