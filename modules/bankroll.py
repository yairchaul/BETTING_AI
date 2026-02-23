# modules/bankroll.py
import pandas as pd

def obtener_stake_sugerido(capital_total, confianza_pick):
    """
    Calcula cuánto apostar basado en la confianza del pick.
    - 10% base
    - +20% si confianza >=90%
    """
    if capital_total <= 0:
        return 0.0
    
    unidad_base = capital_total * 0.10  # 10% sugerido
    
    # Ajuste por confianza
    if confianza_pick >= 90:
        return round(unidad_base * 1.2, 2)
    elif confianza_pick >= 70:
        return round(unidad_base, 2)
    else:
        return round(unidad_base * 0.5, 2)  # Menos si baja confianza

def calcular_roi(ganancia, inversion):
    """Calcula el retorno de inversión en porcentaje"""
    if inversion == 0:
        return 0.0
    return round((ganancia / inversion) * 100, 2)
