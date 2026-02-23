import pandas as pd
import random

class EVEngine:
    def get_stats_last_5(self, equipo):
        """
        Simulación de análisis de últimos 5 partidos.
        En una fase avanzada, aquí se llamaría a una API de resultados reales.
        """
        victorias = random.randint(0, 5) # Simula forma reciente
        goles_favor = random.uniform(4, 12)
        
        prob_victoria = victorias / 5
        prob_gol_ht = (goles_favor / 5) * 0.45 # Probabilidad de gol en 1er tiempo
        
        return {
            "prob_v": prob_victoria,
            "prob_ht": prob_gol_ht,
            "racha": f"{victorias}W-{5-victorias}L"
        }

    def analyze_matches(self, datos_ia):
        juegos = datos_ia.get("juegos", [])
        if not juegos: return [], None

        resultados = []
        candidatos_parlay = []

        for j in juegos:
            st_l = self.get_stats_last_5(j['home'])
            st_v = self.get_stats_last_5(j['away'])

            # Capas de cascada dinámicas
            prob_final_v = (st_l['prob_v'] + (1 - st_v['prob_v'])) / 2
            prob_final_ht = (st_l['prob_ht'] + st_v['prob_ht']) / 2

            analisis = {
                "partido": f"{j['home']} vs {j['away']}",
                "victoria": {"val": f"{int(prob_final_v*100)}%", "pick": j['home']},
                "ht": {"val": f"{int(prob_final_ht*100)}%", "pick": "Over 0.5"},
                "confianza_max": max(prob_final_v, prob_final_ht)
            }
            resultados.append(analisis)
            
            # Guardamos el mejor pick de este partido para el parlay
            pick_parlay = {
                "partido": analisis['partido'],
                "pick": j['home'] if prob_final_v > prob_final_ht else "Over 0.5 HT",
                "prob": analisis['confianza_max']
            }
            candidatos_parlay.append(pick_parlay)

        # EL MEJOR PARLAY: Tomamos los 3 picks con mayor probabilidad de toda la lista
        mejor_parlay = sorted(candidatos_parlay, key=lambda x: x['prob'], reverse=True)[:3]
        return resultados, mejor_parlay

