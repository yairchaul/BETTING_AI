import pandas as pd
import random # Simulación temporal hasta conectar API de resultados

class EVEngine:
    def __init__(self):
        # Base de datos ficticia de tendencias por equipo (Liga MX ejemplo)
        self.team_stats = {
            "Pachuca": {"win": 0.65, "over_ht": 0.78, "btts": 0.60, "corners": 10.2},
            "Mazatlán FC": {"win": 0.35, "over_ht": 0.65, "btts": 0.50, "corners": 8.1},
            "Club América": {"win": 0.70, "over_ht": 0.85, "btts": 0.45, "corners": 11.0},
            "Pumas UNAM": {"win": 0.45, "over_ht": 0.70, "btts": 0.65, "corners": 9.3}
        }

    def get_dynamic_probs(self, team_name):
        """Busca estadísticas reales del equipo o genera una basada en promedio de liga."""
        return self.team_stats.get(team_name, {
            "win": round(random.uniform(0.4, 0.6), 2),
            "over_ht": round(random.uniform(0.5, 0.8), 2),
            "btts": round(random.uniform(0.45, 0.65), 2),
            "corners": round(random.uniform(8.0, 10.5), 1)
        })

    def analyze_matches(self, datos_ia):
        juegos = datos_ia.get("juegos", []) if isinstance(datos_ia, dict) else []
        df = pd.DataFrame(juegos)
        if df.empty: return []

        resultados = []
        for _, row in df.iterrows():
            local = row.get('home', 'Equipo L')
            visitante = row.get('away', 'Equipo V')
            
            # OBTENER ESTADÍSTICAS DIFERENTES PARA CADA PARTIDO
            st_l = self.get_dynamic_probs(local)
            st_v = self.get_dynamic_probs(visitante)

            # Cálculo de probabilidad combinada (Capa de Cascada)
            prob_victoria = st_l['win']
            prob_goals = (st_l['over_ht'] + st_v['over_ht']) / 2

            resultados.append({
                "partido": f"{local} vs {visitante}",
                "metrics": [
                    {"label": "Victoria", "val": f"{int(prob_victoria*100)}%", "status": "ALTA" if prob_victoria > 0.6 else "MED"},
                    {"label": "Over HT", "val": f"{int(prob_goals*100)}%", "status": "ALTA" if prob_goals > 0.7 else "MED"},
                    {"label": "BTTS", "val": "SÍ", "prob": f"{int(st_l['btts']*100)}%"},
                    {"label": "Corners", "val": f"+{int(st_l['corners'])}", "prob": "68%"}
                ]
            })
        return resultados
