class CerebroAuditor:
    def decidir_mejor_apuesta(self, poisson_raw, context_factors, learning_data):
        # 1. Base matemática
        confianza = poisson_raw['prob'] * 100
        
        # 2. Filtro de Realidad (Google)
        if context_factors.get('bajas'):
            confianza -= 15 # Penalización por bajas importantes
            
        # 3. Filtro de Experiencia (Learning)
        confianza += (learning_data.get('ajuste', 0) * 100)
        
        # Limitadores
        confianza = max(5, min(98, confianza))
        
        estado = "ALTA" if confianza > 75 else "MEDIA" if confianza > 55 else "BAJA"
        
        return {
            "pick_final": poisson_raw['pick'],
            "confianza_final": round(confianza, 1),
            "ev_final": poisson_raw['ev'],
            "estatus": estado,
            "nota": learning_data.get('mensaje', ""),
            "cuota_ref": poisson_raw.get('cuota_ref', 1.80)
        }
