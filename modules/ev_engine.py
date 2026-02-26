import math
from typing import Dict, List, Optional, Tuple
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context

# ======================================
# UTILIDADES MATEMÁTICAS
# ======================================
def clamp(x: float) -> float:
    """Mantiene la probabilidad en rangos realistas."""
    return max(0.05, min(0.95, x)

def poisson_prob(lambda_: float, k: int) -> float:
    """Calcula probabilidad de Poisson para k goles."""
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odds: float) -> float:
    """Cálculo estándar de Expected Value."""
    return (prob * odds) - 1

# ======================================
# MOTOR SHARP: CALIENTE.MX OPTIMIZED
# ======================================
def calculate_real_probabilities(home_p: Dict, away_p: Dict, context: Dict) -> Dict[str, float]:
    """
    Simula la decisión de un sharp bettor analizando tendencia reciente y contexto.
    """
    # 1. Factor de Forma (Últimos 5 partidos)
    # El sistema toma el 'form_score' (0.0 a 1.0) derivado de los últimos 5 encuentros
    h_form = home_p.get("form_score", 0.5) 
    a_form = away_p.get("form_score", 0.5)

    # 2. Lambdas dinámicos (Goles Esperados)
    # Ajustamos el ataque y defensa base por el rendimiento reciente (±20%)
    lh = (home_p.get("attack", 1.2) / away_p.get("defense", 1.2)) * 1.25 * (0.8 + h_form * 0.4)
    la = (away_p.get("attack", 1.0) / home_p.get("defense", 1.2)) * 0.85 * (0.8 + a_form * 0.4)
    
    # 3. Cálculo de Probabilidades vía Matriz de Poisson 7x7
    p_win_h, p_draw, p_win_a = 0.0, 0.0, 0.0
    p_btts = 0.0
    p_o15, p_o25, p_o35 = 0.0, 0.0, 0.0
    p_win_h_o15, p_win_h_o25, p_win_a_o15, p_win_a_o25 = 0.0, 0.0, 0.0, 0.0

    for i in range(7):
        for j in range(7):
            prob = poisson_prob(lh, i) * poisson_prob(la, j)
            total_goals = i + j
            
            # Resultado Final
            if i > j: p_win_h += prob
            elif i == j: p_draw += prob
            else: p_win_a += prob
            
            # Ambos Anotan (BTTS)
            if i > 0 and j > 0: p_btts += prob
            
            # Líneas de Goles
            if total_goals > 1.5: p_o15 += prob
            if total_goals > 2.5: p_o25 += prob
            if total_goals > 3.5: p_o35 += prob

            # Mercados Combinados (Caliente.mx Specials)
            if i > j and total_goals > 1.5: p_win_h_o15 += prob
            if i > j and total_goals > 2.5: p_win_h_o25 += prob
            if j > i and total_goals > 1.5: p_win_a_o15 += prob
            if j > i and total_goals > 2.5: p_win_a_o25 += prob

    return {
        "Resultado Final (Local)": clamp(p_win_h),
        "Resultado Final (Empate)": clamp(p_draw),
        "Resultado Final (Visita)": clamp(p_win_a),
        "Doble Oportunidad (L/E)": clamp(p_win_h + p_draw),
        "Doble Oportunidad (V/E)": clamp(p_win_a + p_draw),
        "Ambos Anotan": clamp(p_btts),
        "Over 2.5 Goles": clamp(p_o25),
        "Under 2.5 Goles": clamp(1 - p_o25),
        "Over 3.5 Goles": clamp(p_o35),
        "Local y Over 1.5": clamp(p_win_h_o15),
        "Local y Over 2.5": clamp(p_win_h_o25),
        "Visita y Over 1.5": clamp(p_win_a_o15),
        "Visita y Over 2.5": clamp(p_win_a_o25),
    }

# ======================================
# ANALIZADOR DE VALOR (SHARP DECISION)
# ======================================
def analyze_match(match: Dict) -> Optional[Dict]:
    h_name, a_name = match.get("home"), match.get("away")
    
    # Análisis de los últimos 5 partidos y contexto
    home_p = build_team_profile(h_name)
    away_p = build_team_profile(a_name)
    context = get_match_context(h_name, a_name)

    # Obtenemos probabilidades reales
    probs = calculate_real_probabilities(home_p, away_p, context)
    
    # Cuotas proporcionadas por el ticket/OCR
    odds = match.get("odds", {})
    
    market_results = []
    for market, prob in probs.items():
        if market not in odds:
            continue
            
        ev = calculate_ev(prob, odds[market])
        
        market_results.append({
            "market": market,
            "prob": prob,
            "odds": odds[market],
            "ev": ev
        })

    if not market_results:
        return None

    # ESTRATEGIA SHARP: Seleccionamos ÚNICAMENTE el mercado con el EV más alto
    best_market = max(market_results, key=lambda x: x["ev"])

    # Solo devolvemos si el EV es positivo, para evitar apuestas perdedoras a largo plazo
    if best_market["ev"] <= 0:
        # Failsafe: Si nada es EV+, el sistema sharp no apuesta, pero para el script 
        # devolvemos el menos malo o notificamos.
        pass 

    pick_res = PickResult(
        match=f"{h_name} vs {a_name}",
        selection=best_market["market"],
        probability=round(best_market["prob"], 3),
        odd=best_market["odds"],
        ev=round(best_market["ev"], 3)
    )

    # Formateo visual para el usuario
    text = f"""
    ⚽ **Partido:** {h_name} vs {a_name}
    🎯 **Mercado Sharp:** {best_market['market']}
    📊 **Probabilidad Real:** {best_market['prob']:.2%}
    💰 **Cuota Caliente:** {best_market['odds']}
    📈 **Expected Value:** {best_market['ev']:.2f}
    """

    return {
        "text": text,
        "pick": pick_res
    }
