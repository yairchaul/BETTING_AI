def build_smart_parlay(picks):
    if not picks:
        return None
    
    # Filtrar picks con EV > 0
    valid_picks = [p for p in picks if p.get("ev", 0) > 0]
    if not valid_picks:
        return None
    
    # Ordenar por EV descendente, tomar hasta 5
    sorted_picks = sorted(valid_picks, key=lambda x: x.get("ev", 0), reverse=True)[:5]
    
    total_odd = 1.0
    combined_prob = 1.0
    matches_list = []

    for p in sorted_picks:
        odd = p.get("odd", 0)
        prob = p.get("probability", 0)
        match = p.get("match", "Desconocido")
        selection = p.get("selection", "Desconocido")
        
        if odd <= 0 or prob <= 0:
            continue
        
        decimal = (odd / 100 + 1) if odd > 0 else (100 / abs(odd) + 1)
        total_odd *= decimal
        combined_prob *= prob
        matches_list.append(f"{match}: {selection} ({odd})")
    
    if not matches_list:
        return None
    
    total_ev = (combined_prob * total_odd) - 1
    
    return {
        "matches": matches_list,
        "total_odd": round(total_odd, 2),
        "combined_prob": round(combined_prob, 4),
        "total_ev": round(total_ev, 4)
    }