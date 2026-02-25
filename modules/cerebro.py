class CerebroAuditor:
    def __init__(self):
        self.umbral_confianza_minima = 45.0

    def decidir_mejor_apuesta(self, poisson_raw, context_factors, learning_data):
        """
        Fusiona el Edge matemático con factores externos.
        """
        # 1. Probabilidad base del pick seleccionado por el motor de Edge
        confianza_matematica = poisson_raw['prob'] * 100
        edge_detectado = poisson_raw['ev'] * 100
        
        # 2. Ajustes de Contexto (Google Search)
        ajuste_contexto = 0
        if context_factors.get('bajas'):
            # Si hay bajas y el pick era a favor del favorito, bajamos confianza agresivamente
            ajuste_contexto = -12.5
        
        # 3. Ajustes de Learning (Historial)
        ajuste_learning = learning_data.get('ajuste', 0) * 100
        
        # 4. Cálculo de Confianza Final
        confianza_final = confianza_matematica + ajuste_contexto + ajuste_learning
        
        # 5. Validación de Seguridad
        # Si la confianza cae por debajo del umbral, se marca como riesgo
        confianza_final = max(0, min(99, confianza_final))
        
        estado = "ALTA" if confianza_final > 70 else "MEDIA" if confianza_final > 50 else "RIESGO"

        return {
            "pick_final": poisson_raw['pick'],
            "confianza_final": round(confianza_final, 1),
            "ev_final": poisson_raw['ev'],
            "estatus": estado,
            "nota": learning_data.get('mensaje', "Análisis estándar realizado."),
            "cuota_ref": poisson_raw.get('cuota_ref', 1.85),
            "edge_puro": round(edge_detectado, 2)
        }
