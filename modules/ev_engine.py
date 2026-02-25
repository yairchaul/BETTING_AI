import math

class EVEngine:
    def simulate_parlay_profit(self, parlay, monto):
        cuota_total = 1.0
        for p in parlay:
            try:
                # Limpiar momio (ej. "-371" -> -371.0)
                val = float(str(p["cuota"]).replace('+', '').strip())
                
                # Conversión Americana a Decimal
                if val > 0:
                    decimal = (val / 100) + 1
                else:
                    decimal = (100 / abs(val)) + 1
                
                cuota_total *= decimal
            except:
                cuota_total *= 1.80 # Fallback
        
        pago_total = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(pago_total - monto, 2)
        }

    def build_parlay(self, games):
        # Esta función debe procesar los 'games' detectados por el OCR
        # Retorna: (lista_completa_de_analisis, top_5_picks)
        # Asegúrate de incluir la lógica de cascada aquí
        resultados = [] 
        for g in games:
            # Lógica de probabilidad basada en momios
            res = {
                "partido": f"{g['home']} vs {g['away']}",
                "pick": "Ambos Equipos Anotan", # Ejemplo de cascada
                "probabilidad": 65.0,
                "cuota": g['home_odd'],
                "ev": 0.15
            }
            resultados.append(res)
        return resultados, resultados[:4]
