# modules/bankroll.py
import pandas as pd

def obtener_stake_sugerido(capital_total, confianza_pick):
    """
    Calcula cuánto apostar basado en la confianza del 70-90%
    """
    unidad_base = capital_total * 0.10  # 10% de inversión sugerida
    
    # Ajuste por aprendizaje: más confianza, ligeramente más stake
    if confianza_pick >= 90:
        return round(unidad_base * 1.2, 2)
    return round(unidad_base, 2)

def calcular_roi(ganancia, inversion):
    """Calcula el retorno de inversión para el badge verde"""
    if inversion == 0: return 0
    return round((ganancia / inversion) * 100, 2)
