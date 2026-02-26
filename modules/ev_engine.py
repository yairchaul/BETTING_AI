import random
import math
from typing import Dict, List, Optional, Tuple
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context

# ======================================
# UTILIDADES MATEMÁTICAS
# ======================================

def clamp(x: float) -> float:
    """Mantiene la probabilidad dentro de límites realistas (Regla de Oro: 15%-82%)."""
    return max(0.15, min(0.82, x))

def expected_value(prob: float, odd: float) -> float:
    """Calcula el Valor Esperado (EV)."""
    return (prob * odd) - 1

def poisson_prob(lambda_: float, k: int) -> float:
    """Calcula la probabilidad de que ocurran exactamente k eventos."""
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (exp_val := math.exp(-lambda_)) * (lambda_ ** k) / math.factorial(k)

# ======================================
# MOTOR DE PROBABILIDAD (LAMBDAS)
# ======================================

def calculate_lambdas(home: Dict, away: Dict, context: Dict) -> Tuple[float, float]:
    """Calcula los goles esperados (λ) ajustados por contexto y localía."""
    # Extracción segura de atributos
    h_atk = home.get("attack", home.get("home_strength", 1.3))
    h_def = home.get("defense", home.get("home_defense", 1.2))
    a_atk = away.get("attack", away.get("away_strength", 1.1))
    a_def = away.get("defense", away.get("away_defense", 1.3))
    
    # Ventaja local (HFA) y Tempo
    hfa = 1.25 # Factor multiplicador local
    tempo = (home.get("tempo", 0.5) + away.get("tempo", 0.5)) / 2
    tempo_factor = 0.8 + (tempo * 0.4) # Escala de 0.8 a 1.2

    # Cálculo de Lambdas (Goles Esperados)
    lambda_h = (h_atk / a_def) * hfa * tempo_factor
    lambda_a = (a_atk / h_def) * (1 / hfa) * tempo_factor

    # Ajustes de Contexto (Lesiones e Importancia)
    importance = context.get("importance", 0.5)
    # Partidos de alta importancia tienden a ser más cerrados (menos goles)
    if importance > 0.8:
        lambda_h *= 0.9
        lambda_a *= 0.9

    # Impacto de lesiones
    lambda_h *= (1 - context.get("injuries_home", 0.0) * 0.15)
    lambda_away = lambda_a * (1 - context.get("injuries_away", 0.0) * 0.15)

    return round(lambda_h, 2), round(lambda_away, 2)

# ======================================
# GENERADOR DE MERCADOS (ALL MARKETS)
# ======================================

def calculate_all_markets(home_profile: Dict, away_profile: Dict, context: Dict) -> Dict[str, float]:
    """Calcula todas las probabilidades de mercado usando Poisson y heurística de corners."""
    
    lh, la = calculate_lambdas(home_profile, away_profile, context)
    
    # 1. Probabilidades 1X2 mediante Matriz de Poisson
    prob_h, prob_d, prob_a = 0.0, 0.0, 0.0
    for i in range(7): # Goles local
        for j in range(7): # Goles visitante
            p = poisson_prob(lh, i) * poisson_prob(la, j)
            if i > j: prob_h += p
            elif i == j: prob_d += p
            else: prob_a += p

    # 2. Over / Under 2.5
    # P(U2.5) = P(0-0, 1-0, 0-1, 1-1, 2-0, 0-2)
    l_total = lh + la
    prob_u25 = poisson_prob(l_total, 0) + poisson_prob(l_total, 1) + poisson_prob(l_total, 2)
    prob_o25 = 1.0 - prob_u25

    # 3. BTTS (Ambos Anotan)
    # P(BTTS) = (1 - P(Home 0)) * (1 - P(Away 0))
    prob_btts = (1.0 - poisson_prob(lh, 0)) * (1.0 - poisson_prob(la, 0))

    # 4. Corners Over 8.5
    # Basado en el ataque total y el tempo del partido
    h_atk = home_profile.get("attack", 0.5)
    a_atk = away_profile.get("attack", 0.5)
    tempo = (home_profile.get("tempo", 0.5) + away_profile.get("tempo", 0.5)) / 2
    prob_corners = clamp((h_atk + a_atk) * 0.4 + tempo * 0.3 + 0.10)

    # 5. Over 1.5 (Bonus para cálculos internos)
    prob_o15 = 1.0 - (poisson_prob(l_total, 0) + poisson_prob(l_total, 1))

    return {
        "Empate": clamp(prob_d),
        "BTTS Sí": clamp(prob_btts),
        "Over 2.5": clamp(prob_o25),
        "Local Win": clamp(prob_h),
        "Under 2.5": clamp(prob_u25),
        "Corners Over 8.5": prob_corners,
        "Over 1.5": clamp(prob_o15)
    }

# ======================================
# ANALIZADOR POR PARTIDO
# ======================================

def analyze_match(match: Dict) -> Optional[Dict]:
    """Realiza el análisis completo y genera el reporte textual."""
    
    h_name = match.get("home", "Local")
    a_name = match.get("away", "Visitante")
    
    # Perfiles y Contexto
    home_p = build_team_profile(h_name)
    away_p = build_team_profile(a_name)
    ctx = get_match_context(h_name, a_name)
    
    # Ejecución de motores
    probs = calculate_all_markets(home_p, away_p, ctx)
    
    # Construcción del reporte visual solicitado
    report = [
        f"Empate              {int(probs['Empate']*100)}%",
        f"BTTS Sí             {int(probs['BTTS Sí']*100)}%",
        f"Over 2.5            {int(probs['Over 2.5']*100)}%",
        f"Local Win           {int(probs['Local Win']*100)}%",
        f"Under 2.5           {int(probs['Under 2.5']*100)}%",
        f"Corners Over 8.5    {int(probs['Corners Over 8.5']*100)}%"
    ]

    # Selección del Pick Recomendado (Mayor Probabilidad)
    # Excluimos Over 1.5 de la recomendación principal para cumplir con la lista base
    selectable = {k: v for k, v in probs.items() if k != "Over 1.5"}
    best_name, best_val = max(selectable.items(), key=lambda x: x[1])
    
    report.append("")
    report.append(f"Resultado esperado después del análisis en el partido de {h_name} vs {a_name}:")
    report.append(f"corresponde al **{best_name}** ({int(best_val*100)}%)")

    analysis_text = "\n".join(report)

    # Objeto PickResult para el sistema de apuestas
    pick = PickResult(
        match=f"{h_name} vs {a_name}",
        selection=best_name,
        probability=round(best_val, 3),
        odd=match.get("odds", {}).get(best_name, 1.85), # Cuota real o default
        ev=0.0 # Se calcula en el módulo de odds
    )

    return {
        "text": analysis_text,
        "pick": pick,
        "all_probs": probs
    }

# ======================================
# ANALISIS GLOBAL Y PARLAY
# ======================================

def analyze_matches(matches: List[Dict]) -> List[Dict]:
    """Procesa una lista de partidos."""
    return [res for m in matches if (res := analyze_match(m))]

def build_smart_parlay(picks: List[PickResult]) -> Optional[ParlayResult]:
    """Crea una combinada con los 3 picks de mayor probabilidad."""
    if not picks: return None
    
    # Ordenar por probabilidad pura
    top_picks = sorted(picks, key=lambda x: x.probability, reverse=True)[:3]
    
    t_odd, t_prob = 1.0, 1.0
    names = []
    for p in top_picks:
        t_odd *= p.odd
        t_prob *= p.probability
        names.append(p.match)
        
    return ParlayResult(
        matches=names,
        total_odd=round(t_odd, 2),
        combined_prob=round(t_prob, 3),
        total_ev=round((t_prob * t_odd) - 1, 3)
    )
