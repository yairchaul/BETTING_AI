import pandas as pd
import os

class LearningModule:
    def __init__(self):
        self.path_stats = "data/player_stats.csv"
        self._load_database()

    def _load_database(self):
        if not os.path.exists("data"): os.makedirs("data")
        if not os.path.exists(self.path_stats):
            data = {
                "Sujeto": ["Zion Williamson", "PSG", "Real Madrid", "Man City"],
                "Promedio_Historico": [24.8, 2.5, 2.1, 2.8],
                "Over_Rate_Historico": [0.65, 0.70, 0.62, 0.75]
            }
            pd.DataFrame(data).to_csv(self.path_stats, index=False)
        self.db = pd.read_csv(self.path_stats)

    def analizar_valor_historico(self, nombre, linea_actual=2.5):
        row = self.db[self.db['Sujeto'].str.contains(nombre, case=False, na=False)]
        if not row.empty:
            promedio = row.iloc[0]['Promedio_Historico']
            if linea_actual < promedio:
                return {"ajuste": 0.15, "mensaje": f"📈 Historial: {nombre} promedia {promedio} goles/puntos."}
        return {"ajuste": 0, "mensaje": "📊 Sin anomalías estadísticas."}
