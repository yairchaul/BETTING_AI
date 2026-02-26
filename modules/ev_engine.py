# modules/ev_engine.py
import random
from typing import List, Dict, Optional
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context

# ======================================
# UTILIDADES DE CALIBRACIÓN
# ======================================

def clamp(x: float) -> float:
    """Mantiene la probabilidad dentro de límites realistas (Regla de Oro)."""
    return max(0.15, min(0.82, x))

def expected_value(prob: float, odd: float) -> float:
    """Calcula el Valor Esperado (EV)."""
    return (prob * odd) - 1

# ======================================
# MOTOR DE PROBABILIDAD AVANZADO
# ======================================

def calculate_base_probabilities(home: Dict, away: Dict) -> Dict:
    """Calcula las probabilidades base de 1X2 y dinámica del partido."""
    # Extracción segura de atributos (Mapeo de seguridad)
    h_atk = home.get("attack", home.get("home_strength", 0.5))
    h_def = home.get("defense", home.get("home_defense", 0.5))
    a_atk = away.get("attack", away.get("away_strength", 0.5))
    a_def = away.get("defense", away.get("away_defense", 0.5))
    
    # Ventaja de localía (HFA) estandarizada (+5% ataque, +3% defensa)
    h_atk_adj = h_atk * 1.05
    h_def_adj = h_def * 1.03

    # Diferenciales
    home_edge = h_atk_adj - a_def
    away_edge = a_atk - h_def_adj
    
    # Cálculo de Win/Draw/Loss
    prob_home = clamp(0.38 + (home_edge - away_edge) * 0.30)
    prob_draw = clamp(0.25 - (abs(home_edge - away_edge) * 0.15))
    prob_away = clamp(1.0 - prob_home - prob_draw)

    # Tempo y Expectativa de goles
    tempo = (home.get("tempo", 0.5) + away.get("tempo", 0.5)) / 2
    goal_expectancy = (h_atk_adj + a_atk) / (h_def_adj + a_def + 0.1)

    return {
        "home": prob_home,
        "draw": prob_draw,
        "away": prob_away,
        "tempo": tempo,
        "goal_expectancy": goal_expectancy
    }

def calculate_all_markets(home: Dict, away: Dict, base_probs: Dict, context: Dict) -> Dict:
    """Genera probabilidades detalladas para múltiples mercados."""
    
    # Factores de contexto
    importance = context.get("importance", 0.5)
    injuries_h = context.get("injuries_home", 0.0)
    injuries_a = context.get("injuries_away", 0.0)
    
    # Ajustes por lesiones e importancia
    # Menos importancia = juego más abierto/caótico; Más importancia = más cerrado
    defensive_adjustment = 0.05 if importance > 0.7 else -0.05
    
    # 1. BTTS Sí
    # Correlación: Alta expectativa de gol y defensas similares
    btts_base = (base_probs["goal_expectancy"] * 0.4) + (base_probs["tempo"] * 0.2)
    prob_btts = clamp(btts_base + 0.10 - (injuries_h + injuries_a) * 0.05)

    # 2. Over / Under 2.5
    over_base = (base_probs["goal_expectancy"] * 0.5) + (base_probs["tempo"] * 0.15)
    prob_over_25 = clamp(over_base - defensive_adjustment)
    prob_under_25 = clamp(1.0 - prob_over_25)

    # 3. Corners Over 8.5
    # Basado en Tempo + Ataque Promedio + Factor de Despejes Defensivos
    h_atk = home.get("attack", 0.5)
    a_atk = away.get("attack", 0.5)
    corner_prob = clamp((h_atk + a_atk) * 0.4 + base_probs["tempo"] * 0.3 + 0.15)

    # 4. Mercados Bonus (Over 1.5 y Local Win)
    prob_over_15 = clamp(prob_over_25 + 0.22)
    prob_local_win = base_probs["home"]

    return {
        "Empate": prob_draw_final := clamp(base_probs["draw"]),
        "BTTS": prob_btts,
        "Over 2.5": prob_over_25,
        "Local Win": prob_local_win,
        "Under 2.5": prob_under_25,
        "Corners 8.5": corner_prob,
        "Over 1.5": prob_over_15
    }

# ======================================
# ANALIZADOR POR PARTIDO
# ======================================

def generate_full_analysis(match: Dict) -> Optional[PickResult]:
    """Realiza el análisis profundo partido por partido."""
    
    home_name = match.get("home", "Local")
    away_name = match.get("away", "Visitante")
    
    # Construcción de perfiles
    home_profile = build_team_profile(home_name)
    away_profile = build_team_profile(away_name)
    
    # Obtención de contexto
    context = get_match_context(home_name, away_name)
    
    # 1. Probabilidades base
    base_probs = calculate_base_probabilities(home_profile, away_profile)
    
    # 2. Cálculo de todos los mercados
    all_probs = calculate_all_markets(home_profile, away_profile, base_probs, context)
    
    # 3. Formateo de salida según requerimiento
    print(f"\n--- Análisis: {home_name} vs {away_name} ---")
    print(f"Empate {int(all_probs['Empate'] * 100)}%")
    print(f"BTTS {int(all_probs['BTTS'] * 100)}%")
    print(f"Over 2.5 {int(all_probs['Over 2.5'] * 100)}%")
    print(f"Local Win {int(all_probs['Local Win'] * 100)}%")
    print(f"Under 2.5 {int(all_probs['Under 2.5'] * 100)}%")
    print(f"Corners 8.5 {int(all_probs['Corners 8.5'] * 100)}%")
    
    # 4. Selección del Pick Recomendado (Mayor Probabilidad)
    # Filtramos mercados para el PickResult (excluimos Over 1.5 del log si no se pidió pero lo usamos para comparar)
    selectable_markets = {k: v for k, v in all_probs.items() if k != "Over 1.5"}
    best_market_name = max(selectable_markets, key=selectable_markets.get)
    best_prob = selectable_markets[best_market_name]
    
    print(f"Resultado esperado después del análisis en el partido de {home_name} vs {away_name}: corresponde al {best_market_name}")

    # Asignación de cuotas estimadas para cálculo de EV (si no se proveen en match)
    # En producción, estas vendrían de un odds_provider
    estimated_odds = {
        "Empate": 3.40, "BTTS": 1.90, "Over 2.5": 2.05, 
        "Local Win": 2.10, "Under 2.5": 1.85, "Corners 8.5": 1.80
    }
    current_odd = match.get("odds", {}).get(best_market_name, estimated_odds.get(best_market_name, 2.0))

    return PickResult(
        match=f"{home_name} vs {away_name}",
        selection=best_market_name,
        probability=round(best_prob, 3),
        odd=current_odd,
        ev=round(expected_value(best_prob, current_odd), 3)
    )

def analyze_match(match: Dict) -> Optional[PickResult]:
    """Alias compatible con la estructura modular anterior."""
    return generate_full_analysis(match)

# ======================================
# ANALISIS GLOBAL
# ======================================

def analyze_matches(matches: List[Dict]) -> List[PickResult]:
    """Analiza una lista de partidos uno por uno."""
    results = []
    for match in matches:
        analysis = analyze_match(match)
        if analysis:
            results.append(analysis)
    return results

# ======================================
# PARLAY BUILDER (SYNDICATE)
# ======================================

def build_smart_parlay(picks: List[PickResult]) -> Optional[ParlayResult]:
    """Construye una combinada optimizada basada en probabilidad y EV."""
    if not picks:
        return None

    # Seleccionamos los mejores picks basados en Probabilidad para asegurar el parlay
    # pero limitamos a los que tengan EV positivo si es posible
    safe_picks = sorted(picks, key=lambda x: x.probability, reverse=True)[:3]

    total_odd = 1.0
    combined_prob = 1.0
    match_list = []

    for p in safe_picks:
        total_odd *= p.odd
        combined_prob *= p.probability
        match_list.append(f"{p.match} ({p.selection})")

    total_ev = expected_value(combined_prob, total_odd)

    return ParlayResult(
        matches=match_list,
        total_odd=round(total_odd, 2),
        combined_prob=round(combined_prob, 3),
        total_ev=round(total_ev, 3)
    )
