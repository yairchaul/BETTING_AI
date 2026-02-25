import math
import numpy as np

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def _poisson_pmf(self, k, lam):
        return (math.exp(-lam) * (lam**k)) / math.factorial(k) if lam > 0 else (1.0 if k==0 else 0.0)

    def build_parlay(self, games):
        resultados_finales = []
        
        for g in games:
            # 1. Inferir Lambdas (Fuerza) de los momios reales detectados
            try:
                # Convertimos momio americano a probabilidad implícita para obtener la fuerza real
                def get_prob(o):
                    o = float(str(o).replace('+', ''))
                    return 100/(o+100) if o>0 else abs(o)/(abs(o)+100)
                
                p_h = get_prob(g.get('home_odd', 100))
                p_v = get_prob(g.get('away_odd', 100))
                
                # Lambdas conservadoras basadas en el mercado real
                l_h, l_v = p_h * 2.8, p_v * 2.8 
            except:
                l_h, l_v = 1.3, 1.1

            # 2. Generar matriz de probabilidades (Marcadores exactos 0-6 goles)
            max_g = 7
            matrix = np.zeros((max_g, max_g))
            for h in range(max_g):
                for v in range(max_g):
                    matrix[h, v] = self._poisson_pmf(h, l_h) * self._poisson_pmf(v, l_v)

            # 3. Calcular todas las opciones posibles
            posibilidades = []
            
            # Mercados de Over Puro
            p_o15 = 1 - (matrix[0,0] + matrix[0,1] + matrix[1,0])
            posibilidades.append({"pick": "Over 1.5 Goles", "p": p_o15, "c": 1.35})
            
            p_o25 = p_o15 - (matrix[1,1] + matrix[2,0] + matrix[0,2])
            posibilidades.append({"pick": "Over 2.5 Goles", "p": p_o25, "c": 1.85})

            # BTTS
            p_btts = (1 - sum(matrix[0, :])) * (1 - sum(matrix[:, 0]))
            posibilidades.append({"pick": "BTTS Si", "p": p_btts, "c": 1.75})

            # Ganador Simple
            p_win_h = np.sum(np.tril(matrix, -1))
            posibilidades.append({"pick": f"Gana {g['home']}", "p": p_win_h, "c": g.get('home_odd', 2.0)})

            # Combos (Gana + Over)
            p_h_o15 = np.sum([matrix[h, v] for h in range(max_g) for v in range(max_g) if h > v and (h+v) > 1.5])
            posibilidades.append({"pick": f"{g['home']} & Over 1.5", "p": p_h_o15, "c": 2.20})

            # 4. FILTRADO DURO (85%) Y SELECCIÓN DE MEJOR CUOTA
            # Solo pasan las que tienen prob >= threshold
            validas = [opt for opt in posibilidades if opt['p'] >= self.threshold]

            if validas:
                # Elegimos la que tenga la cuota ('c') más alta entre las seguras
                mejor = max(validas, key=lambda x: x['c'])
                resultados_finales.append({
                    "partido": f"{g['home']} vs {g['away']}",
                    "pick": mejor['pick'],
                    "probabilidad": round(mejor['p'] * 100, 1),
                    "cuota": mejor['c']
                })
        
        # El parlay se arma con los mejores 3 picks globales encontrados
        parlay = sorted(resultados_finales, key=lambda x: x['probabilidad'], reverse=True)[:3]
        return resultados_finales, parlay

    def simulate_parlay_profit(self, parlay, monto):
        c_tot = 1.0
        for p in parlay:
            try:
                val = float(str(p['cuota']).replace('+', ''))
                dec = (val/100 + 1) if val > 0 else (100/abs(val) + 1)
                c_tot *= dec
            except: c_tot *= 1.30
        
        pago = monto * c_tot
        return {"cuota_total": round(c_tot, 2), "pago_total": round(pago, 2), "ganancia_neta": round(pago - monto, 2)}

