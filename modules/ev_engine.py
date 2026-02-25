import math

class EVEngine:
    def __init__(self):
        self.threshold = 0.85 # Filtro de Élite

    def _poisson_pmf(self, k, lam):
        if lam <= 0: return 1.0 if k == 0 else 0.0
        return math.exp(-lam) * (lam ** k) / math.factorial(k)

    def _get_probs(self, l_h, l_a):
        # Probabilidades de ganar/empatar
        p_h = p_d = p_a = 0.0
        for h in range(9):
            for a in range(9):
                prob = self._poisson_pmf(h, l_h) * self._poisson_pmf(a, l_a)
                if h > a: p_h += prob
                elif h == a: p_d += prob
                else: p_a += prob
        return p_h, p_d, p_a

    def build_parlay(self, games):
        resultados = []
        for g in games:
            # 1. Ajuste de Lambdas según momios reales para evitar bucles
            l_h, l_a = 1.4, 1.2
            try:
                # Si detectamos un favorito pesado (ej. -200), subimos su fuerza
                odd_val = float(str(g.get("home_odd", "100")).replace('+', ''))
                if odd_val < 0: l_h += 0.8
                elif odd_val < 150: l_h += 0.3
            except: pass

            ph, pd, pa = self._get_probs(l_h, l_a)
            
            # 2. Mercados de Cascada
            p_0_0 = self._poisson_pmf(0, l_h) * self._poisson_pmf(0, l_a)
            p_1_0 = self._poisson_pmf(1, l_h) * self._poisson_pmf(0, l_a)
            p_0_1 = self._poisson_pmf(0, l_h) * self._poisson_pmf(1, l_a)
            
            p_over_1_5 = 1 - (p_0_0 + p_1_0 + p_0_1)
            p_btts = (1 - self._poisson_pmf(0, l_h)) * (1 - self._poisson_pmf(0, l_a))
            
            # 3. Lógica de Selección (Cascada)
            if p_over_1_5 >= 0.80:
                pick, prob, cuota = "Over 1.5 Goles", p_over_1_5, 1.35
            elif ph >= 0.65:
                pick, prob, cuota = f"Gana {g.get('home','Local')}", ph, g.get('home_odd', 1.90)
            elif p_btts >= 0.62:
                pick, prob, cuota = "Ambos Anotan", p_btts, 1.80
            else:
                pick, prob, cuota = "Over 0.5 Goles 2T", 0.75, 1.40

            resultados.append({
                "partido": f"{g.get('home','')} vs {g.get('away','')}",
                "pick": pick,
                "probabilidad": round(prob * 100, 1),
                "cuota": cuota
            })

        # Seleccionamos los 3 más seguros para el parlay
        parlay = sorted(resultados, key=lambda x: x['probabilidad'], reverse=True)[:3]
        return resultados, parlay

    def simulate_parlay_profit(self, parlay, monto):
        c_total = 1.0
        for p in parlay:
            try:
                # Conversión de momio americano a decimal
                val = float(str(p['cuota']).replace('+', ''))
                dec = (val/100 + 1) if val > 0 else (100/abs(val) + 1)
                c_total *= dec
            except: c_total *= 1.40
        
        pago = monto * c_total
        return {"cuota_total": round(c_total, 2), "pago_total": round(pago, 2), "ganancia_neta": round(pago - monto, 2)}

