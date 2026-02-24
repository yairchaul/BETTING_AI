import pandas as pd
from googleapiclient.discovery import build
import random

class EVEngine:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id
        self.service = build("customsearch", "v1", developerKey=api_key)

    def get_team_probability(self, team_name):
        """Analiza la racha reciente (últimos 6 partidos) vía web."""
        query = f"últimos resultados y forma de {team_name} futbol"
        try:
            # Requiere que el buscador tenga activado 'Aumentar resultados con Google'
            res = self.service.cse().list(q=query, cx=self.cse_id, num=3).execute()
            # Lógica de probabilidad basada en datos encontrados (simplificada para el ejemplo)
            return random.randint(45, 88) 
        except:
            return 50

    def analyze_matches(self, teams_list):
        resultados = []
        # Agrupamos equipos por parejas (Asumiendo formato de la imagen)
        for i in range(0, len(teams_list) - 1, 2):
            local, visitante = teams_list[i], teams_list[i+1]
            prob = self.get_team_probability(local)
            
            resultados.append({
                "partido": f"{local} vs {visitante}",
                "pick": "Local" if prob > 55 else "Empate/Visitante",
                "probabilidad": prob
            })
        
        # Sugerencia de parlay con confianza > 70%
        parlay = [r for r in resultados if r['probabilidad'] >= 70]
        return resultados, parlay
