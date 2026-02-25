class CerebroAuditor:
    def auditar(self, poisson_data, context_data):
        # Si el contexto menciona bajas o lesiones, ajustamos confianza
        confianza = poisson_data['p'] * 100
        
        if "lesión" in context_data.lower() or "ausente" in context_data.lower():
            confianza -= 10
            nota = "⚠️ Alerta de lesiones en el equipo."
        else:
            nota = "✅ Sin alertas externas detectadas."

        return {
            "pick_final": poisson_data['name'],
            "confianza": round(confianza, 1),
            "cuota": round(poisson_data['c'], 2),
            "nota": nota
        }
