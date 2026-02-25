class CerebroAuditor:
    def __init__(self):
        pass

    def decidir_mejor_apuesta(self, poisson_data, context_factors, learning_data):
        """
        Fusiona 3 fuentes de datos:
        1. Poisson (Matemática)
        2. Contexto (Noticias/Bajas)
        3. Learning (Estadística histórica)
        """
        confianza_base = poisson_data['prob']
        ajuste_contexto = 0
        
        # Ajuste por Bajas (Google Search)
        if context_factors['bajas']:
            ajuste_contexto -= 15  # Penalizamos confianza si hay bajas
        
        # Ajuste por Learning (Estadística)
        ajuste_learning = learning_data['ajuste'] * 100
        
        # Cálculo de Confianza Final
        confianza_final = confianza_base + ajuste_contexto + ajuste_learning
        confianza_final = max(5, min(98, confianza_final)) # Limitar entre 5% y 98%

        # Determinación de "Bandera de Valor"
        es_segura = "ALTA" if confianza_final > 75 else "MEDIA" if confianza_final > 55 else "BAJA"

        return {
            "pick_final": poisson_data['pick'],
            "confianza_final": round(confianza_final, 1),
            "ev_final": poisson_data['ev'],
            "estatus": es_segura,
            "nota": learning_data['mensaje']
        }
