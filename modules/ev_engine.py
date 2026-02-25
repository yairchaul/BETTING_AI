def simulate_parlay_profit(self, parlay, monto):
        cuota_total = 1.0
        for p in parlay:
            try:
                # Limpiamos el texto del momio (ej. "+118" -> 118.0)
                val = float(str(p["cuota"]).replace('+', '').strip())
                
                # Conversión estándar de Momio Americano a Decimal
                if val > 0:
                    decimal = (val / 100) + 1
                else:
                    decimal = (100 / abs(val)) + 1
                
                cuota_total *= decimal
            except:
                cuota_total *= 1.85 # Valor de respaldo si falla el OCR
        
        pago_total = monto * cuota_total
        ganancia_neta = pago_total - monto
        
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(ganancia_neta, 2)
        }

