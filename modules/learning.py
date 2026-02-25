import pandas as pd
import os

class LearningModule:
    def __init__(self):
        self.path_stats = "data/player_stats.csv"
        self._load_database()

    def _load_database(self):
        if not os.path.exists("data"): os.makedirs("data")
        if not os.path.exists(self.path_stats):
            # Base de datos inicial de ejemplo
            data = {
                "Sujeto": ["Zion Williamson", "Saddiq Bey", "PSG", "Real Madrid"],
                "Promedio_Historico": [24.8, 13.5, 2.5, 2.1],
                "Over_Rate_Historico": [0.65, 0.55, 0.70, 0.62]
            }
            pd.DataFrame(data).to_csv(self.path_stats, index=False)
        self.db = pd.read_csv(self.path_stats)

    def analizar_valor_historico(self, nombre, linea_actual):
        """Compara la línea de la apuesta con la realidad estadística."""
        # Buscar en la base de datos (insensible a mayúsculas)
        row = self.db[self.db['Sujeto'].str.contains(nombre, case=False, na=False)]
        
        if not row.empty:
            promedio = row.iloc[0]['Promedio_Historico']
            rate = row.iloc[0]['Over_Rate_Historico']
            
            # Si la línea de la apuesta es menor al promedio, hay valor en el OVER
            if linea_actual < promedio:
                ventaja = (promedio - linea_actual) / promedio
                return {"ajuste": ventaja * 0.20, "mensaje": f"📈 Valor: {nombre} suele promediar {promedio}"}
        
        return {"ajuste": 0, "mensaje": "📊 Sin anomalías en promedio histórico"}
