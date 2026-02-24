import random
from modules.caliente_api import get_market_lines

class EVEngine:

    def __init__(self):
        pass

    # =============================
    # MODELO IA (SIMULADO)
    # =============================
    def model_probability(self):
        """Simula el cálculo de probabilidad del modelo de machine learning."""
        return random.randint(55, 92)

    # =============================
    # ANALISIS EN CASCADA
    # =============================
    def cascade_analysis(self, local, visitante):
        """
        Aplica lógica de selección de mercado basada en la probabilidad detectada.
        Prioriza mercados de menor riesgo según el umbral.
        """
        markets = get_market_lines(local, visitante)
        prob = self.model_probability()

        # 1. Mercado de Alta Confianza (Goles 1T)
        if prob >= 85:
            return {
                "partido": f"{local} vs {visitante}",
                "pick": "Over 1.5 goles 1T",
                "probabilidad": prob,
                "cuota": 1.65
            }

        # 2. Mercado de Confianza Media-Alta (Goles Totales)
        if prob >= 75:
            line = markets["totals"][1]
            return {
                "partido": f"{local} vs {visitante}",
                "pick": f"Over {line} goles",
                "probabilidad": prob,
                "cuota": 1.75
            }

        # 3. Mercado de Confianza Media (Corners)
        if prob >= 65:
            line = markets["corners"][0]
            return {
                "partido": f"{local} vs {visitante}",
                "pick": f"Over {line} corners",
                "probabilidad": prob,
                "cuota": 1.85
            }

        # 4. Mercado por Defecto (Ganador)
        return {
            "partido": f"{local} vs {visitante}",
            "pick": f"Gana {local}",
            "probabilidad": prob,
            "cuota": 2.00
        }

    # =============================
    # CONSTRUCCION DE PARLAY (CORREGIDO)
    # =============================
    def build_parlay(self, equipos):
        """
        Toma la lista de equipos detectados y construye las parejas de partidos.
        Filtra automáticamente para el parlay los picks con prob >= 80%.
        """
        resultados = []
        parlay = []
        
        # El OCR procesa la lista como [Local1, Vis1, Local2, Vis2...]
        # Usamos un paso de 2 para saltar de partido en partido
        for i in range(0, len(equipos) - 1, 2):
            local = equipos[i]
            visitante = equipos[i + 1]
            
            # Validación: Evitamos emparejar un equipo consigo mismo 
            # o procesar filas vacías
            if local.strip() != visitante.strip():
                analisis = self.cascade_analysis(local, visitante)
                resultados.append(analisis)
                
                # Criterio de selección para el Parlay Maestro
                if analisis["probabilidad"] >= 80:
                    parlay.append(analisis)
                    
        return resultados, parlay

    # =============================
    # SIMULADOR DE GANANCIA
    # =============================
    def simulate_parlay_profit(self, parlay, monto):
        """Calcula el rendimiento potencial del parlay seleccionado."""
        if not parlay:
            return {"cuota_total": 0, "pago_total": 0, "ganancia_neta": 0}

        cuota_total = 1.0

        for pick in parlay:
            cuota_total *= pick["cuota"]

        ganancia_total = monto * cuota_total
        profit_neto = ganancia_total - monto

        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(ganancia_total, 2),
            "ganancia_neta": round(profit_neto, 2)
        }
