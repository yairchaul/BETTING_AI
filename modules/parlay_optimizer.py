# modules/parlay_optimizer.py
class ParlayOptimizer:
    def find_optimal_parlays(self, available_picks, max_size=3, target_ev=0.01):
        if len(available_picks) < 2: return None
        
        # PRIORIDAD 1: Picks con EV positivo real
        value_picks = [p for p in available_picks if p['ev'] > target_ev]
        
        # Si no hay picks con EV, usamos los de mayor probabilidad (pero el EV será bajo)
        picks_to_use = value_picks if len(value_picks) >= 2 else available_picks
        
        best_parlays = []
        for size in range(2, max_size + 1):
            for combo in combinations(picks_to_use, size):
                # VALIDACIÓN: No repetir partido Y No repetir mercado (DIVERSIFICACIÓN)
                matches = set()
                categories = set()
                for p in combo:
                    matches.add(p['match'])
                    categories.add(p['category'])
                
                if len(matches) < size: continue # Evita mismo partido
                
                # Bonus por diversidad de categorías (evita solo Over 1.5)
                diversity_score = len(categories) / size 
                
                prob_total = np.prod([p['prob'] for p in combo])
                odds_total = np.prod([p['odd'] for p in combo])
                ev_combined = (prob_total * odds_total) - 1
                
                # Ajustar EV por diversidad para el ranking
                fitness = ev_combined * diversity_score

                best_parlays.append({
                    'picks': list(combo),
                    'prob': prob_total,
                    'odds': odds_total,
                    'ev_combined': ev_combined,
                    'fitness': fitness
                })

        if not best_parlays: return None
        
        # Ordenar por fitness (mezcla de EV y diversidad)
        best_parlays.sort(key=lambda x: x['fitness'], reverse=True)
        return best_parlays[0]
