from modules.autopicks import generar_picks_auto
from modules.bankroll import calcular_stake
from modules.telegram_bot import enviar_pick
from modules.connector import obtener_juegos
from modules.montecarlo import simular_total
from modules.ev_engine import calcular_ev
from modules.bankroll import calcular_stake
from modules.injuries import verificar_lesiones
from modules.ranking import ranking_edges
from modules.tracker import guardar_pick, calcular_roi

print("\n🔥 NBA AI +EV v10.0")

bankroll = float(input("💰 Ingresa Bankroll MXN: "))

juegos = obtener_juegos()

if not juegos:
    print("No hay juegos disponibles.")
    exit()

picks = []

for g in juegos:

    media_modelo = g["line"] + 4

    prob = simular_total(media_modelo)

    ev = calcular_ev(prob)

    if ev < 0:
        continue

    if ev > 0.08:
        confianza = "🔥 EXCELENTE"
    elif ev > 0.04:
        confianza = "⚡ BUENA"
    else:
        confianza = "➖ BAJA"

    stake = calcular_stake(bankroll, confianza)

    lesiones = verificar_lesiones(g["home"])

    juego_txt = f"{g['away']} vs {g['home']}"

    print("\n====================")
    print(juego_txt)
    print("Prob Over:", round(prob*100,2),"%")
    print("EV:", round(ev*100,2),"%")
    print("Stake sugerido:", round(stake,2),"MXN")
    print("Lesiones:", lesiones)

    guardar_pick(juego_txt, stake, ev)

    picks.append({
        "game": juego_txt,
        "ev": ev
    })

ranking_edges(picks)

calcular_roi()
picks = generar_picks_auto()

for p in picks:
    stake = calcular_stake(bankroll,p["ev"])

    texto=f"""
🔥 AUTO PICK
Juego: {p['game']}
EV: {round(p['ev']*100,2)}%
Stake: ${round(stake,2)}
"""

    print(texto)
    enviar_pick(texto)