import random
from googleapiclient.discovery import build

class EVEngine:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id
        # Inicialización del servicio de búsqueda de Google
        self.service = build("customsearch", "v1", developerKey=api_key)

    def analyze_matches(self, teams_list):
        """Genera picks y probabilidades vinculadas al Main."""
        resultados = []
        parlay_sugerido = []

        # Agrupar de 2 en 2 (Local vs Visitante)
        for i in range(0, len(teams_list) - 1, 2):
            local, visitante = teams_list[i], teams_list[i+1]
            
            # Cálculo de probabilidad basado en racha (simulado 45-95)
            prob = random.randint(45, 95)
            
            # Definición del pick según confianza
            pick = f"Gana {local}" if prob >= 70 else "Doble Oportunidad / Empate"
            
            match_data = {
                "partido": f"{local} vs {visitante}",
                "pick": pick,
                "probabilidad": prob
            }
            
            resultados.append(match_data)
            
            # Nutre el parlay solo con selecciones de alta confianza
            if prob >= 75:
                parlay_sugerido.append(match_data)
                
        return resultados, parlay_sugerido
from modules.schemas import BetData, EVResult

def calculate_ev(bet: BetData) -> EVResult:
    implied_prob = 1 / bet.odds
    ev = (bet.probability * bet.odds) - 1
    edge = bet.probability - implied_prob

    return EVResult(
        ev=ev,
        edge=edge
    )

