import pandas as pd
from googleapiclient.discovery import build
import random

class EVEngine:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id
        # Configuración del servicio de búsqueda de Google
        self.service = build("customsearch", "v1", developerKey=api_key)

    def get_team_form(self, team_name):
        """
        Simula la búsqueda de los últimos 6 partidos.
        En una versión avanzada, aquí procesarías los snippets de Google Search.
        """
        try:
            query = f"últimos 6 resultados {team_name} futbol"
            # Ejecuta la búsqueda en los sitios permitidos (ej. google.com/*)
            res = self.service.cse().list(q=query, cx=self.cse_id, num=1).execute()
            
            # Generamos una probabilidad basada en "forma reciente" (simulado para estabilidad)
            # 80-90: Excelente racha, 60-75: Regular, <50: Mala racha
            probabilidad = random.randint(40, 95)
            return probabilidad
        except Exception:
            return 50 # Probabilidad neutra si falla la búsqueda

    def analyze_matches(self, teams_list):
        """
        Toma la lista de equipos detectados por Vision y genera los picks.
        """
        resultados = []
        parlay_sugerido = []

        # Emparejamos los equipos de dos en dos (Local vs Visitante)
        for i in range(0, len(teams_list) - 1, 2):
            local = teams_list[i]
            visitante = teams_list[i+1]
            
            # Analizamos la forma del equipo local para el cálculo
            prob = self.get_team_form(local)
            
            # Determinamos el Pick basado en la probabilidad calculada
            if prob >= 70:
                pick = f"Gana {local}"
            elif prob <= 45:
                pick = f"Gana {visitante} / Empate"
            else:
                pick = "Empate / Menos de 2.5 goles"

            datos_partido = {
                "partido": f"{local} vs {visitante}",
                "pick": pick,
                "probabilidad": prob
            }
            
            resultados.append(datos_partido)
            
            # Si la confianza es alta (Verde en el semáforo), va al parlay
            if prob >= 75:
                parlay_sugerido.append(datos_partido)
                
        return resultados, parlay_sugerido
