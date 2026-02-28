import numpy as np
import streamlit as st

SIMULATIONS = 20000

def adjusted_lambda(home_stats, away_stats):
    """Calcula la expectativa de goles (Lambda) basada en fuerza relativa."""
    league_avg = 1.35
    # Si no hay stats, usamos 50 como base neutra
    home_attack = home_stats.get("attack", 50)
    home_def = home_stats.get("defense", 50)
    away_attack = away_stats.get("attack", 50)
    away_def = away_stats.get("defense", 50)
    
    # Modelo Poisson ajustado
    home_lambda = league_avg * (home_attack / 50) * (50 / away_def)
    away_lambda = league_avg * (away_attack / 50) * (50 / home_def)
    
    # Ventaja de localía (12% extra histórico promedio)
    home_lambda *= 1.12
    return home_lambda, away_lambda

def run_simulations(stats):
    """Ejecuta simulación Monte Carlo para predecir probabilidades."""
    try:
        lam_home, lam_away = adjusted_lambda(stats.get("home", {}), stats.get("away", {}))
        
        # Añadimos ruido para simular la variabilidad real del deporte (volatilidad)
        noise_home = np.random.normal(1, 0.15, SIMULATIONS)
        noise_away = np.random.normal(1, 0.15, SIMULATIONS)
        
        goals_home = np.random.poisson(lam_home * noise_home)
        goals_away = np.random.poisson(lam_away * noise_away)
        
        total_goals = goals_home + goals_away
        
        # Probabilidades estimadas
        return {
            "1": np.mean(goals_home > goals_away),
            "X": np.mean(goals_home == goals_away),
            "2": np.mean(goals_home < goals_away),
            "Over 2.5": np.mean(total_goals > 2.5),
            "Ambos Anotan": np.mean((goals_home > 0) & (goals_away > 0))
        }
    except Exception as e:
        st.error(f"Error en simulación: {e}")
        return {}

def obtener_mejor_apuesta(partido):
    """Compara probabilidades de la IA vs Momios de la Casa (EV Analysis)."""
    home = partido.get("home", "Local")
    away = partido.get("away", "Visitante")
    
    # Por ahora usamos stats base, pero aquí podrías conectar una base de datos real
    stats = {"home": {"attack": 52, "defense": 48}, "away": {"attack": 48, "defense": 52}}

    probs_ia = run_simulations(stats)
    if not probs_ia:
        return None

    # Rescate de momios desde el OCR (Soporta múltiples formatos de clave)
    raw_odds = partido.get("odds") or partido.get("all_odds") or []
    
    # Mapeo de mercados a índices del array de momios
    # 0: Local, 1: Empate, 2: Visitante
    mercados_mapeo = {
        "1": 0,
        "X": 1,
        "2": 2
    }

    mejores_opciones = []

    for mercado, index in mercados_mapeo.items():
        if len(raw_odds) > index:
            try:
                momio_american = int(str(raw_odds[index]).replace('+', ''))
                
                # Convertir Americano a Decimal para calcular EV
                if momio_american > 0:
                    decimal = (momio_american / 100) + 1
                else:
                    decimal = (100 / abs(momio_american)) + 1
                
                prob_ia = probs_ia[mercado]
                # FÓRMULA EV: (Probabilidad IA * Cuota Decimal) - 1
                ev = (prob_ia * decimal) - 1
                
                # Solo sugerir si el EV es positivo (ventaja sobre la casa)
                if ev > 0.02: # Umbral mínimo de 2% de ventaja
                    mejores_opciones.append({
                        "mercado": mercado,
                        "prob": prob_ia,
                        "odd": momio_american,
                        "ev": ev
                    })
            except ValueError:
                continue

    if not mejores_opciones:
        return None

    # Retornamos la opción con mayor Valor Esperado (EV+)
    mejor = max(mejores_opciones, key=lambda x: x["ev"])
    
    return {
        "match": f"{home} vs {away}",
        "selection": mejor["mercado"],
        "odd": mejor["odd"],
        "probability": mejor["prob"],
        "ev": mejor["ev"]
    }
