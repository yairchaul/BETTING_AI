def obtener_stake_sugerido(capital_total, confianza_pick, prob_win=0.55):
    """
    Versión simple con ajuste Kelly aproximado
    """
    unidad_base = capital_total * 0.10
    # Ajuste Kelly básico: f = (p*b - q)/b donde b=1 (odds ~even)
    kelly_frac = (prob_win - (1 - prob_win))  # simplificado
    stake = capital_total * max(0, kelly_frac * 0.5)  # half-Kelly para menos riesgo
    return round(max(stake, unidad_base * 0.05), 2)  # mínimo 5% de unidad
