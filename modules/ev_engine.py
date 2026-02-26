import math
from typing import Dict, List, Optional, Tuple
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context

# ======================================
# UTILIDADES MATEMÁTICAS
# ======================================
def clamp(x: float) -> float:
    return max(0.05, min(0.95, x))

def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

# ======================================
# MOTOR DE ANÁLISIS DE MERCADOS CALIENTE.MX
# ======================================
def calculate_advanced_markets(home_p: Dict, away_p: Dict, context: Dict) -> Dict[str, float]:
    # 1. Simulación de tendencia (Últimos 5 partidos)
    # Extraemos 'form' o usamos el promedio de ataque/defensa como proxy de tendencia
    h_form = home_p.get("form", (home_p.get("attack", 0.5) + (1 - home_p.get("defense", 0.5))) / 2)
    a_form = away_p.get("form", (away_p.get("attack", 0.5) + (1 - away_p.get("defense", 0.5))) / 2)

    # 2. Cálculo de Goles Esperados (Lambdas)
    lh = (home_p.get("attack", 1.2) / away_p.get("defense", 1.2)) * 1.25 * (0.9 + h_form * 0.2)
    la = (away_p.get("attack", 1.0) / home_p.get("defense", 1.2)) * 0.85 * (0.9 + a_form * 0.2)
    
    # 3. Probabilidades Exactas (Matriz 7x7)
    p_win_h, p_draw, p_win_a = 0.0, 0.0, 0.0
    p_btts = 0.0
    p_over_15, p_over_25, p_over_35 = 0.0, 0.0, 0.0
    p_win_h_btts, p_win_a_btts = 0.0, 0.0

    for i in range(7):
        for j in range(7):
            prob = poisson_prob(lh, i) * poisson_prob(la, j)
            total_g = i + j
            
            # Resultado Final
            if i > j: p_win_h += prob
            elif i == j: p_draw += prob
            else: p_win_a += prob
            
            # Goles
            if total_g > 1.5: p_over_15 += prob
            if total_g > 2.5: p_over_25 += prob
            if total_g > 3.5: p_over_35 += prob
            
            # Ambos Anotan
            if i > 0 and j > 0: p_btts += prob
            
            # Combinados (Caliente.mx Especiales)
            if i > j and i > 0 and j > 0: p_win_h_btts += prob
            if j > i and i > 0 and j > 0: p_win_a_btts += prob

    # 4. Construcción de Diccionario de Opciones Caliente
    # Aquí calculamos Doble Oportunidad basándonos en las prob. base
    probs = {
        "Gana Local": clamp(p_win_h),
        "Empate": clamp(p_draw),
        "Gana Visitante": clamp(p_win_a),
        "Doble Oportunidad (L/E)": clamp(p_win_h + p_draw),
        "Ambos Equipos Anotan": clamp(p_btts),
        "Over 2.5 Goles": clamp(p_over_25),
        "Under 2.5 Goles": clamp(1 - p_over_25),
        "Over 1.5 Goles": clamp(p_over_15),
        "Over 3.5 Goles": clamp(p_over_35),
        "Local y Ambos Anotan": clamp(p_win_h_btts),
        "Visitante y Ambos Anotan": clamp(p_win_a_btts),
        "Resultado/Ambos Anotan (Empate/Sí)": clamp(p_draw * p_btts * 1.1)
    }
    
    return probs

# ======================================
# ANALIZADOR PRINCIPAL
# ======================================
def analyze_match(match: Dict) -> Optional[Dict]:
    h_name, a_name = match.get("home"), match.get("away")
    home_p = build_team_profile(h_name)
    away_p = build_team_profile(a_name)
    context = get_match_context(h_name, a_name)

    probs = calculate_advanced_markets(home_p, away_p, context)
    
    # Cuotas estimadas (esto idealmente vendría del OCR o API de Caliente)
    # Si no hay cuotas en el ticket, el motor asume valores de mercado promedio
    default_odds = {
        "Gana Local": 2.0, "Empate": 3.2, "Gana Visitante": 3.5,
        "Doble Oportunidad (L/E)": 1.3, "Ambos Equipos Anotan": 1.8,
        "Over 2.5 Goles": 1.9, "Under 2.5 Goles": 1.9,
        "Local y Ambos Anotan": 4.5, "Visitante y Ambos Anotan": 6.0
    }

    # SELECCIÓN INTELIGENTE: Buscamos el mejor EV
    best_pick = None
    max_ev = -99.0

    report = []
    for name, prob in probs.items():
        odd = match.get("odds", {}).get(name, default_odds.get(name, 2.0))
        ev = (prob * odd) - 1
        
        # Guardamos en el reporte los mercados principales
        if name in ["Gana Local", "Empate", "Ambos Equipos Anotan", "Over 2.5 Goles"]:
            report.append(f"{name.ljust(20)} {int(prob*100)}% (EV: {round(ev,2)})")
        
        # La lógica de "qué más conviene": Prioriza EV positivo y probabilidad > 40%
        if ev > max_ev and prob > 0.40:
            max_ev = ev
            best_pick = (name, prob, odd, ev)

    if not best_pick: # Failsafe
        best_pick = ("Over 1.5 Goles", probs["Over 1.5 Goles"], 1.3, 0.01)

    # Formateo final
    analysis_text = "\n".join(report)
    analysis_text += f"\n\nPick Recomendado Caliente: **{best_pick[0]}**"
    analysis_text += f"\nConfianza: {int(best_pick[1]*100)}% | EV: {round(best_pick[3],2)}"

    pick_res = PickResult(
        match=f"{h_name} vs {a_name}",
        selection=best_pick[0],
        probability=round(best_pick[1], 3),
        odd=best_pick[2],
        ev=round(best_pick[3], 3)
    )

    return {"text": analysis_text, "pick": pick_res, "all_probs": probs}

def analyze_matches(matches: List[Dict]) -> List[Dict]:
    return [res for m in matches if (res := analyze_match(m))]

def build_smart_parlay(picks: List[PickResult]) -> Optional[ParlayResult]:
    if not picks: return None
    # El parlay ahora solo elige lo más seguro (Probabilidad > 65%)
    safe_picks = [p for p in picks if p.probability > 0.60]
    if not safe_picks: safe_picks = sorted(picks, key=lambda x: x.probability, reverse=True)[:2]
    
    t_odd, t_prob = 1.0, 1.0
    for p in safe_picks:
        t_odd *= p.odd
        t_prob *= p.probability
        
    return ParlayResult(
        matches=[p.match for p in safe_picks],
        total_odd=round(t_odd, 2),
        combined_prob=round(t_prob, 3),
        total_ev=round((t_prob * t_odd) - 1, 3)
    )
