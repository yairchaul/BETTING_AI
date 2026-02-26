import math
from typing import List, Optional

# Corrección de importación para Streamlit Cloud
try:
    from modules.schemas import PickResult, ParlayResult
except ImportError:
    from schemas import PickResult, ParlayResult

def build_smart_parlay(picks: List[PickResult]) -> Optional[ParlayResult]:
    """
    Selecciona los mejores 5 picks y los une en una sola sugerencia de parlay.
    """
    if not picks:
        return None
    
    # Filtramos y ordenamos los mejores picks por ventaja estadística (EV)
    # Solo tomamos picks con EV positivo real
    mejores_picks = sorted([p for p in picks if p.ev > 0], key=lambda x: x.ev, reverse=True)[:5]
    
    if not mejores_picks:
        return None

    total_odd = 1.0
    combined_prob = 1.0
    matches_list = []

    for p in mejores_picks:
        # Convertimos momio americano a decimal para el cálculo total
        decimal = (p.odd/100 + 1) if p.odd > 0 else (100/abs(p.odd) + 1)
        total_odd *= decimal
        combined_prob *= p.probability
        matches_list.append(f"{p.match}: {p.selection} ({p.odd})")
        
    total_ev = (combined_prob * total_odd) - 1
    
    return ParlayResult(
        matches=matches_list,
        total_odd=round(total_odd, 2),
        combined_prob=round(combined_prob, 4),
        total_ev=round(total_ev, 4)
    )

