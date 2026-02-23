# modules/bankroll.py
import pandas as pd

def obtener_stake_sugerido(capital_total, confianza_pick):
    """
    Calcula stake basado en confianza.
    - 10% base
    - +20% si confianza >=90%
    - Mejora: Agrega ajuste Kelly aproximado (fraccional para menos riesgo)
    """
    if capital_total <= 0:
        return 0.0
    
    unidad_base = capital_total * 0.10  # 10% sugerido
    
    # Ajuste por confianza
    if confianza_pick >= 90:
        multiplier = 1.2
    elif confianza_pick >= 70:
        multiplier = 1.0
    else:
        multiplier = 0.5
    
    # Ajuste Kelly simple (asumiendo prob_win ~ confianza/100, odds even)
    prob_win = confianza_pick / 100
    kelly_frac = max(0, prob_win - (1 - prob_win))  # Simplificado
    stake = unidad_base * multiplier * (kelly_frac * 0.5)  # Half-Kelly para seguridad
    
    return round(stake, 2)

def calcular_roi(ganancia, inversion):
    """Calcula el retorno de inversión en porcentaje"""
    if inversion == 0:
        return 0.0
    return round((ganancia / inversion) * 100, 2)
