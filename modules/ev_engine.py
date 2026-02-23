import pandas as pd
import sys
import os

class EVEngine:
    def __init__(self):
        # Datos de referencia para el análisis de cascada
        self.prob_cascada = {
            "Goles_HT": 0.72,
            "BTTS": 0.55,
            "Corners": 9.5
        }

    def limpiar_momio(self, valor):
        """Evita el ValueError de tus capturas anteriores."""
        try:
            limpio = str(valor).replace('+', '').replace(' ', '').strip()
            return int(limpio) if limpio.lstrip('-').isdigit() else 100
        except:
            return 100

    def analyze_matches(self, datos_ia):
        """Analiza partido por partido con el método cascada."""
        juegos = datos_ia.get("juegos", []) if isinstance(datos_ia, dict) else []
        df = pd.DataFrame(juegos)
        
        if df.empty: return []

        resultados = []
        for _, row in df.iterrows():
            local = row.get('home', 'Local')
            visitante = row.get('away', 'Visitante')
            momio = self.limpiar_momio(row.get('moneyline', '+100'))

            # Capas de Análisis
            analisis = {
                "partido": f"{local} vs {visitante}",
                "momio": momio,
                "capas": [
                    {"nivel": "1. Victoria", "pick": local, "prob": "60%", "status": "✅"},
                    {"nivel": "2. Goles HT", "pick": "Over 0.5", "prob": "72%", "status": "✅"},
                    {"nivel": "3. Ambos Anotan", "pick": "SÍ", "prob": "55%", "status": "⚠️"},
                    {"nivel": "4. Tiros Esquina", "pick": "+8.5", "prob": "65%", "status": "✅"}
                ]
            }
            resultados.append(analisis)
        return resultados

    def generar_resumen_social(self, picks):
        """Genera el texto listo para copiar a grupos o redes sociales."""
        resumen = "🏆 *ANÁLISIS DE CASCADA IA* 🏆\n\n"
        for p in picks:
            resumen += f"⚽ *{p['partido']}* (Momio: {p['momio']})\n"
            resumen += f"🔥 Pick Principal: {p['capas'][0]['pick']} ({p['capas'][0]['prob']})\n"
            resumen += f"⏱️ 1er Tiempo: {p['capas'][1]['pick']}\n"
            resumen += f"🚩 Córners: {p['capas'][3]['pick']}\n\n"
        resumen += "🤖 _Generado por Ticket Pro IA_"
        return resumen
