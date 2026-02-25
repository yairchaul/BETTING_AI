def simulate_parlay_profit(self, parlay, monto):
        cuota_total = 1.0
        for p in parlay:
            try:
                # Limpiar el string de la cuota (quitar +, etc)
                val = float(str(p["cuota"]).replace('+', '').strip())
                
                # Conversión Real de Momio Americano a Decimal
                if val > 0:
                    decimal = (val / 100) + 1
                else:
                    decimal = (100 / abs(val)) + 1
                
                cuota_total *= decimal
            except Exception as e:
                # Cuota por defecto si falla el parseo
                cuota_total *= 1.85
        
        pago_total = monto * cuota_total
        ganancia_neta = pago_total - monto
        
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(ganancia_neta, 2)
        }

