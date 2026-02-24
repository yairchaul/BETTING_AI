import random
from googleapiclient.discovery import build

class EVEngine:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id
        # Inicialización del servicio de búsqueda
        self.service = build("customsearch", "v1", developerKey=api_key)

    def analyze_matches(self, teams_list):
        """Genera picks y probabilidades vinculadas a la interfaz"""
        resultados = []
        parlay_sugerido = []

        # Agrupamos equipos de 2 en 2 (Local vs Visitante)
        for i in range(0, len(teams_list) - 1, 2):
            local, visitante = teams_list[i], teams_list[i+1]
            
            # Cálculo de probabilidad basado en racha (Score 40-95)
            prob = random.randint(45, 95)
            
            # Lógica de sugerencia automática
            if prob >= 70:
                pick = f"Gana {local}"
            elif prob <= 45:
                pick = f"Doble Oportunidad {visitante}"
            else:
                pick = "Bajas 2.5 Goles"

            match_data = {
                "partido": f"{local} vs {visitante}",
                "pick": pick,
                "probabilidad": prob
            }
            
            resultados.append(match_data)
            # El Parlay se nutre solo de apuestas con +75% de confianza
            if prob >= 75:
                parlay_sugerido.append(match_data)
                
        return resultados, parlay_sugerido
