def detect_value(self, our_probability, market_odds, threshold=0.05):
    """
    Detecta si hay valor (edge) positivo
    threshold = 0.05 significa 5% de ventaja
    """
    if not market_odds or market_odds == 'N/A':
        return {
            'has_value': False,
            'edge': 0,
            'recommendation': 'No hay odds de mercado para comparar'
        }
    
    decimal_odd = self.american_to_decimal(market_odds)
    if not decimal_odd:
        return {
            'has_value': False,
            'edge': 0,
            'recommendation': 'No se pudo convertir la odd'
        }
    
    # Probabilidad implícita del mercado (1 / odd)
    implied_prob = 1 / decimal_odd
    
    # Calcular edge (diferencia entre nuestra probabilidad y la del mercado)
    edge = our_probability - implied_prob
    
    # Solo considerar VALUE si el edge es positivo y significativo
    has_value = edge > threshold
    
    if has_value:
        recommendation = f"🔥 VALUE BET! Ventaja de {edge:.1%}"
    elif edge > 0:
        recommendation = f"👍 Pequeña ventaja: {edge:.1%} (menor al umbral)"
    else:
        recommendation = f"👎 Desventaja: {edge:.1%}"
    
    return {
        'has_value': has_value,
        'edge': edge,
        'implied_probability': implied_prob,
        'decimal_odd': decimal_odd,
        'recommendation': recommendation
    }
