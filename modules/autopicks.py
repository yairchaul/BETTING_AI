from modules.connector import obtener_eventos_nba_hoy

def generar_picks():

    juegos = obtener_eventos_nba_hoy()
    picks = []

    for g in juegos:
        picks.append(g)

    return picks