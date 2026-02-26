import math
from typing import List, Optional
try:
    from modules.schemas import PickResult, ParlayResult
except ImportError:
    from schemas import PickResult, ParlayResult

def build_smart_parlay(picks: List[PickResult]) -> Optional[ParlayResult]:
    """
    Toma los picks analizados y construye la mejor combinada (Top 5).
    """
    if not picks:
        return None
    
    # Ordenar por el Valor Esperado (EV) más alto
    selected = sorted(picks, key=lambda x: x.ev, reverse=True)[:5]
    
    total_odd = 1.0
    combined_prob = 1.0
    
    for p in selected:
        total_odd *= p.odd
        combined_prob *= p.probability
        
    total_ev = (combined_prob * total_odd) - 1
    
    return ParlayResult(
        matches=[f"{p.match} ({p.selection})" for p in selected],
        total_odd=round(total_odd, 2),
        combined_prob=round(combined_prob, 4),
        total_ev=round(total_ev, 4)
    )

