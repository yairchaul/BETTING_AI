import math
import numpy as np

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def _poisson_pmf(self, k, lam):
        return (math.exp(-lam) * (lam**k)) / math.factorial(k) if lam > 0 else (1.0 if k==0 else 0.0)

    def build_parlay(self, games):
        resultados_totales = []
        parlay_final = []
        
        for g in games:
            try:
                # Traducción de momios a fuerza de gol (Agnóstico)
                def to_p(o):
                    v = float(str(o).replace('+', ''))
                    return 100/(v+100) if v > 0 else abs(v)/(abs(v)+100)
                
                # Lambdas basadas en probabilidad implícita
                l_h = to_p(g.get('home_odd', 100)) * 2.8
                l_v = to_p(g.get('away_odd', 100)) * 2.8
            except: l_h, l_v = 1.3, 1.1

            # Matriz de 7x7 marcadores posibles
            m = np.fromfunction(np.vectorize(lambda h, v: self._poisson_pmf(h, l_h) * self._poisson_pmf(v, l_v)), (7, 7))

            # --- EVALUACIÓN DE TODAS LAS CAPAS ---
            opciones = []
            
            # Doble Oportunidad (1X)
            p_1x = m.sum() - np.tril(m, -1).sum()
            opciones.append({"pick": f"{g['home']} o Empate", "p": p_1x, "c": 1.25})
            
            # Over 1.5 Goles
            p_o15 = 1 - (m[0,0] + m[0,1] + m[1,0])
            opciones.append({"pick": "Over 1.5 Goles", "p": p_o15, "c": 1.35})
            
            # Ambos Anotan (BTTS)
            p_btts = (1 - m[0,:].sum()) * (1 - m[:,0].sum())
            opciones.append({"pick": "Ambos Anotan", "p": p_btts, "c": 1.70})

            # --- LÓGICA DE FILTRADO ---
            # Guardamos el mejor de cada partido para mostrarlo aunque no llegue al 85%
            mejor_opcion = max(opciones, key=lambda x: x['p'])
            
            resultado = {
                "partido": f"{g['home']} vs {g['away']}",
                "pick": mejor_opcion['pick'],
                "probabilidad": round(mejor_opcion['p'] * 100, 1),
                "cuota": mejor_opcion['c'],
                "pasa_filtro": mejor_opcion['p'] >= self.threshold
            }
            resultados_totales.append(resultado)
            
            # Solo agregamos al Parlay si cumple tu regla del 85%
            if resultado["pasa_filtro"]:
                parlay_final.append(resultado)

        return resultados_totales, parlay_final[:3]


