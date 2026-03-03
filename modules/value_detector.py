# modules/value_detector.py
class ValueDetector:
    def american_to_decimal(self, american_odd):
        try:
            if not american_odd or american_odd == 'N/A': return None
            odd_str = str(american_odd).replace(' ', '').strip()
            if odd_str.startswith('+'):
                return (float(odd_str[1:]) / 100) + 1
            elif odd_str.startswith('-'):
                return (100 / abs(float(odd_str))) + 1
            else:
                return float(odd_str)
        except: return None

    def detect_value(self, our_probability, market_odds, threshold=0.02):
        """
        Calcula el EV Real. 
        Si el EV es > 0, tenemos una apuesta de valor.
        """
        decimal_odd = self.american_to_decimal(market_odds)
        if not decimal_odd or our_probability <= 0:
            return {'has_value': False, 'ev': -1, 'fair_odd': 0}

        # Fair Odd: Cuota justa según tu análisis de IA
        fair_odd = 1 / our_probability
        
        # EV REAL: (Probabilidad IA * Cuota Mercado) - 1
        ev = (our_probability * decimal_odd) - 1
        
        return {
            'has_value': ev > threshold,
            'ev': ev,
            'fair_odd': fair_odd,
            'decimal_odd': decimal_odd
        }
