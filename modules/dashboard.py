# modules/dashboard.py

def generar_parlay_elite(partidos):
    seleccionados = []
    for p in partidos:
        # El sistema busca la opción más segura de cada partido
        analisis = ev_engine.buscar_mejor_valor_global(p, stats)
        if analisis['prob'] >= 0.75: # Solo lo más seguro entra al parlay
            seleccionados.append(analisis)
            
    if len(seleccionados) >= 3:
        # Si juntamos 3, disparamos la alerta de Telegram
        telegram_bot.enviar_alerta_parlay(seleccionados)
        return seleccionados
    return None




