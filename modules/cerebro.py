import numpy as np
import streamlit as st

SIMULATIONS = 25000 # Aumentamos simulaciones para mayor precisión

def run_simulations(stats):
    """Simulación Monte Carlo basada en Poisson para proyectar mercados."""
    try:
        # Expectativas de goles basadas en equilibrio de fuerzas
        lam_home = 1.40 * (stats["home"]["attack"] / 50) * (50 / stats["away"]["defense"])
        lam_away = 1.10 * (stats["away"]["attack"] / 50) * (50 / stats["home"]["defense"])
        
        # Generar distribución de goles
        goals_home = np.random.poisson(lam_home, SIMULATIONS)
        goals_away = np.random.poisson(lam_away, SIMULATIONS)
        total_goals = goals_home + goals_away
        
        return {
            "1": np.mean(goals_home > goals_away),
            "X": np.mean(goals_home == goals_away),
            "2": np.mean(goals_home < goals_away),
            "Ambos Anotan": np.mean((goals_home > 0) & (goals_away > 0)),
            "Over 2.5": np.mean(total_goals > 2.5),
            "Local o Empate (1X)": np.mean(goals_home >= goals_away)
        }
    except:
        return {}

def obtener_mejor_apuesta(partido):
    home = partido.get("home", "Local")
    away = partido.get("away", "Visitante")
    raw_odds = partido.get("odds") or [] 
    
    if len(raw_odds) < 3: return None

    # 1. Ejecutar IA
    stats = {"home": {"attack": 50, "defense": 50}, "away": {"attack": 50, "defense": 50}}
    probs = run_simulations(stats)
    
    opciones_analizadas = []

    # 2. EVALUAR MERCADOS DISPONIBLES EN IMAGEN (1X2)
    # Mapeo: Índice 0=Local, 1=Empate, 2=Visita
    mapa_1x2 = {"1": 0, "X": 1, "2": 2}
    labels_1x2 = {"1": f"Gana {home}", "X": "Empate", "2": f"Gana {away}"}

    for clave, idx in mapa_1x2.items():
        try:
            momio_am = int(str(raw_odds[idx]).replace('+', ''))
            decimal = (momio_am/100+1) if momio_am > 0 else (100/abs(momio_am)+1)
            prob = probs[clave]
            ev = (prob * decimal) - 1
            
            # Filtro Seguro: Probabilidad alta y ventaja real
            if prob > 0.42 and ev > 0.02 and momio_am < 350:
                opciones_analizadas.append({
                    "selection": labels_1x2[clave],
                    "prob": prob, "odd": momio_am, "ev": ev
                })
        except: continue

    # 3. EVALUAR MERCADOS DE PROBABILIDAD (Ambos Anotan / Over)
    # Como no tenemos el momio de la imagen, usamos un momio base de -115 (1.87) 
    # que es el estándar de las casas para estos mercados equilibrados.
    mercados_extra = ["Ambos Anotan", "Over 2.5", "Local o Empate (1X)"]
    for m in mercados_extra:
        prob_m = probs[m]
        momio_base = -115 
        decimal_base = 1.87
        ev_m = (prob_m * decimal_base) - 1
        
        # Filtro de alta seguridad para mercados secundarios
        if prob_m > 0.60 and ev_m > 0.05:
            opciones_analizadas.append({
                "selection": m,
                "prob": prob_m, "odd": momio_base, "ev": ev_m
            })

    if not opciones_analizadas: return None

    # 4. DECISIÓN FINAL: Seleccionar la opción con mayor probabilidad de éxito
    # Esto garantiza que el parlay sea lo más "seguro" posible.
    mejor = max(opciones_analizadas, key=lambda x: x["prob"])

    return {
        "match": f"{home} vs {away}",
        "selection": mejor["selection"],
        "odd": mejor["odd"],
        "probability": mejor["prob"],
        "ev": mejor["ev"]
    }
