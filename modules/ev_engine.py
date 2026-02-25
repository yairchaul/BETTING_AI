import math

class EVEngine:
    # ... (funciones poisson_pmf y get_poisson_probs fuera de la clase) ...

    def simulate_parlay_profit(self, parlay, monto):
        cuota_total = 1.0
        for p in parlay:
            try:
                # Limpieza de momio y conversión real
                val = float(str(p["cuota"]).replace('+', '').strip())
                # Conversión Americana -> Decimal
                decimal = (val/100 + 1) if val > 0 else (100/abs(val) + 1)
                cuota_total *= decimal
            except:
                cuota_total *= 1.85
        
        pago_total = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(pago_total - monto, 2)
        }

    def build_parlay(self, games):
        # Asegúrate de que esta función devuelva los momios detectados por el OCR
        # para que simulate_parlay_profit use datos reales
        resultados = []
        for g in games:
            # Lógica de cascada aquí...
            pass
        return resultados, resultados[:5] # Ejemplo
