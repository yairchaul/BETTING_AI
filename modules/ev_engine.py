import math
from modules.ev_scanner import calculate_ev

# 1. Funciones matemáticas globales para cálculo de Poisson
def poisson_pmf(k, lam):
    if lam <= 0: return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def get_poisson_probs(lambda_home, lambda_away):
    max_goals = 8
    p_home = p_draw = p_away = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
            if h > a: p_home += prob
            elif h == a: p_draw += prob
            else: p_away += prob
    total = p_home + p_draw + p_away
    return p_home/total, p_draw/total, p_away/total

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold
        self.min_ev_threshold = 0.13

    def build_parlay(self, games):
        resultados_totales = []
        
        for g in games:
            home_name = g.get('home', 'Local')
            away_name = g.get('away', 'Visita')
            
            # --- AJUSTE DINÁMICO DE FUERZA (LAMBDA) ---
            l_home, l_away = 1.65, 1.20 # Base
            try:
                # Convertir momio americano a probabilidad implícita para ajustar Lambdas
                h_odd_str = str(g.get("home_odd", "0")).replace('+', '')
                h_odd = float(h_odd_str)
                if h_odd < 0: l_home += 0.8  # Favorito claro
                elif h_odd < 150: l_home += 0.4
            except: pass

            # --- CÁLCULO DE PROBABILIDADES POR MERCADO (CAPAS) ---
            ph, pd, pa = get_poisson_probs(l_home, l_away)
            
            # Capa 1: Over 1.5 Goles
            p_over_1_5 = 1 - (poisson_pmf(0, l_home)*poisson_pmf(0, l_away) + 
                             poisson_pmf(1, l_home)*poisson_pmf(0, l_away) + 
                             poisson_pmf(0, l_home)*poisson_pmf(1, l_away))
            
            # Capa 2: Doble Oportunidad (Local o Empate)
            p_1x = ph + pd
            
            # Capa 3: Ambos Anotan
            p_btts = (1 - poisson_pmf(0, l_home)) * (1 - poisson_pmf(0, l_away))

            # --- EVALUACIÓN DE OPCIONES ---
            opciones = [
                {"pick": f"{home_name} o Empate", "p": p_1x, "c": 1.25},
                {"pick": "Over 1.5 Goles", "p": p_over_1_5, "c": 1.35},
                {"pick": "Ambos Anotan", "p": p_btts, "c": 1.70}
            ]

            # FILTRO: De las opciones que pasan el 85%, elegimos la de mejor cuota (c)
            validas = [o for o in opciones if o['p'] >= self.threshold]
            
            if validas:
                # Elegir la que mejor paga de las seguras
                mejor_opcion = max(validas, key=lambda x: x['c'])
            else:
                # Si



