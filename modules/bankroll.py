from modules.learning import ajustar_modelo

def calcular_stake(bankroll, confianza, ev):

    factor_aprendizaje = ajustar_modelo()

    base = bankroll * 0.02

    if confianza == "🔥 EXCELENTE":
        base = bankroll * 0.05
    elif confianza == "⚡ BUENA":
        base = bankroll * 0.02
    else:
        base = bankroll * 0.01

    # ajuste IA automático
    stake_final = base * factor_aprendizaje

    return round(stake_final,2)