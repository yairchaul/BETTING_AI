# modules/value_detector.py
import streamlit as st

class ValueDetector:
    """
    Detector de apuestas de valor (value betting)
    Usa Valor Esperado (EV) como métrica principal
    """
    
    def __init__(self):
        pass
    
    def american_to_decimal(self, american_odd):
        """Convierte odds americanas a decimales"""
        try:
            if american_odd == 'N/A' or not american_odd:
                return None
            
            odd_str = str(american_odd).strip()
            
            if odd_str.startswith('+'):
                return (int(odd_str[1:]) / 100) + 1
            elif odd_str.startswith('-'):
                return (100 / abs(int(odd_str))) + 1
            else:
                return float(odd_str)
        except:
            return None
    
    def decimal_to_american(self, decimal_odd):
        """Convierte odds decimales a americanas"""
        try:
            if decimal_odd >= 2.0:
                return f"+{int((decimal_odd - 1) * 100)}"
            else:
                return f"-{int(100 / (decimal_odd - 1))}"
        except:
            return "N/A"
    
    def calculate_implied_probability(self, decimal_odd):
        """Calcula probabilidad implícita de una odd decimal"""
        if not decimal_odd or decimal_odd <= 0:
            return None
        return 1 / decimal_odd
    
    def detect_value(self, our_probability, market_odds, threshold=0.05):
        """
        Detecta si hay valor usando Valor Esperado (EV)
        EV = (Probabilidad * Cuota) - 1
        threshold = 0.05 significa 5% de EV positivo
        """
        if not market_odds or market_odds == 'N/A':
            return {
                'has_value': False,
                'ev': 0,
                'fair_odd': None,
                'implied_probability': None,
                'decimal_odd': None,
                'recommendation': 'No hay odds de mercado para comparar'
            }
        
        decimal_odd = self.american_to_decimal(market_odds)
        if not decimal_odd:
            return {
                'has_value': False,
                'ev': 0,
                'fair_odd': None,
                'implied_probability': None,
                'decimal_odd': None,
                'recommendation': 'No se pudo convertir la odd'
            }
        
        # Probabilidad implícita del mercado
        implied_prob = self.calculate_implied_probability(decimal_odd)
        
        # FAIR ODD (Odd justa basada en nuestra probabilidad)
        fair_odd = 1 / our_probability if our_probability > 0 else 0
        
        # VALOR ESPERADO (EV) - Métrica correcta
        ev = (our_probability * decimal_odd) - 1
        
        # Hay valor si EV > umbral
        has_value = ev > threshold
        
        if has_value:
            recommendation = f"🔥 VALUE! EV: {ev:.1%}"
        elif ev > 0:
            recommendation = f"👍 Pequeño EV: {ev:.1%} (menor al umbral de {threshold:.1%})"
        else:
            recommendation = f"👎 EV negativo: {ev:.1%}"
        
        return {
            'has_value': has_value,
            'ev': ev,
            'fair_odd': fair_odd,
            'implied_probability': implied_prob,
            'decimal_odd': decimal_odd,
            'american_odd': market_odds,
            'recommendation': recommendation
        }
    
    def analyze_match_markets(self, match_analysis, match_odds):
        """Analiza todos los mercados de un partido en busca de valor"""
        results = []
        
        # Mapeo flexible de mercados (con búsqueda por substring)
        market_keywords = [
            ('Gana Local', ['local', 'home']),
            ('Empate', ['empate', 'draw']),
            ('Gana Visitante', ['visitante', 'away']),
        ]
        
        for market_name, keywords in market_keywords:
            # Buscar la probabilidad de este mercado en el análisis
            market_prob = None
            for m in match_analysis.get('markets', []):
                # Búsqueda flexible por nombre
                if any(keyword in m['name'].lower() for keyword in keywords):
                    market_prob = m['prob']
                    break
            
            if not market_prob:
                continue
            
            # Obtener la odd real de la imagen
            if 'all_odds' in match_odds and len(match_odds['all_odds']) > 0:
                # Intentar encontrar la odd correspondiente
                if 'local' in market_name.lower() and len(match_odds['all_odds']) > 0:
                    market_odd = match_odds['all_odds'][0]
                elif 'empate' in market_name.lower() and len(match_odds['all_odds']) > 1:
                    market_odd = match_odds['all_odds'][1]
                elif 'visitante' in market_name.lower() and len(match_odds['all_odds']) > 2:
                    market_odd = match_odds['all_odds'][2]
                else:
                    market_odd = 'N/A'
            else:
                market_odd = 'N/A'
            
            # Detectar valor
            value_result = self.detect_value(market_prob, market_odd)
            value_result['market'] = market_name
            value_result['market_prob'] = market_prob
            
            results.append(value_result)
        
        return results
    
    def get_best_value_bet(self, match_analysis, match_odds):
        """Obtiene la mejor apuesta de valor para un partido"""
        results = self.analyze_match_markets(match_analysis, match_odds)
        
        # Filtrar solo las que tienen EV positivo
        value_bets = [r for r in results if r.get('ev', 0) > 0]
        
        if value_bets:
            # Ordenar por EV (mayor a menor)
            value_bets.sort(key=lambda x: x.get('ev', 0), reverse=True)
            best = value_bets[0]
            best['type'] = 'value_bet'
            return best
        else:
            # Si no hay valor, devolver la de mayor probabilidad
            if results:
                results.sort(key=lambda x: x.get('market_prob', 0), reverse=True)
                best = results[0]
                best['type'] = 'probabilidad'
                return best
        
        return None
    
    def get_value_summary(self, match_analysis, match_odds):
        """Obtiene un resumen de todos los valores para un partido"""
        results = self.analyze_match_markets(match_analysis, match_odds)
        return [r for r in results if r.get('ev', 0) > 0]
        
