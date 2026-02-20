# bankroll.py
import pandas as pd

def calcular_gestion_profesional(capital_actual, nivel_confianza):
    """
    Aplica el Criterio de Kelly simplificado para ajustar la inversión.
    Evita el error de invertir siempre lo mismo sin importar el riesgo.
    """
    # Inversión base sugerida del 10%
    stake_base = capital_actual * 0.10
    
    # Ajuste por confianza: Si el pick es >85%, sube un poco el riesgo.
    # Si es <75%, lo baja para proteger el capital.
    if nivel_confianza > 85:
        factor_ajuste = 1.2  # Arriesga un 20% más de la unidad base
    elif nivel_confianza < 75:
        factor_ajuste = 0.8  # Arriesga un 20% menos
    else:
        factor_ajuste = 1.0

    monto_final = stake_base * factor_ajuste
    return round(monto_final, 2)

def actualizar_balance_post_jornada(ganancia_neta):
    """
    Actualiza el capital disponible después de registrar los resultados.
    """
    # Aquí se conectaría con tu base de datos o archivo de registro
    pass
