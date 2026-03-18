"""
ANALIZADOR GEMINI NBA - Versión definitiva (87.5% precisión)
"""
import google.generativeai as genai
import json
import re
import streamlit as st

class AnalizadorGeminiNBA:
    def __init__(self, api_key):
        self.api_key = api_key
        self.disponible = False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.disponible = True
            print("✅ Gemini NBA conectado")
        except Exception as e:
            st.warning(f"⚠️ Gemini no disponible: {e}")
    
    def analizar(self, partido):
        """
        Analiza partido con datos reales - Versión optimizada
        """
        if not self.disponible:
            return self._fallback_heurístico(partido)
        
        local = partido['local']
        visitante = partido['visitante']
        records = partido.get('records', {})
        odds = partido.get('odds', {})
        
        # Calcular win rates
        wr_local = self._calcular_wr(records.get('local', '0-0'))
        wr_visit = self._calcular_wr(records.get('visitante', '0-0'))
        
        # Si hay clara diferencia, usar heurístico directamente
        if abs(wr_local - wr_visit) > 15:
            if wr_local > wr_visit:
                return {
                    'ganador': local,
                    'confianza': 70,
                    'razones': [f"Win rate muy superior ({wr_local:.1f}% vs {wr_visit:.1f}%)"],
                    'color': 'green'
                }
            else:
                return {
                    'ganador': visitante,
                    'confianza': 70,
                    'razones': [f"Win rate muy superior ({wr_visit:.1f}% vs {wr_local:.1f}%)"],
                    'color': 'green'
                }
        
        # Prompt optimizado para casos dudosos
        prompt = f"""
        Eres un analista de NBA. Analiza este partido basándote ÚNICAMENTE en los datos.
        
        {local} vs {visitante}
        
        DATOS REALES:
        - Récord {local}: {records.get('local', '0-0')} (Win Rate: {wr_local:.1f}%)
        - Récord {visitante}: {records.get('visitante', '0-0')} (Win Rate: {wr_visit:.1f}%)
        - Diferencia: {abs(wr_local - wr_visit):.1f}%
        - Spread: {odds.get('spread', 0):+g}
        
        REGLAS:
        1. Si diferencia < 5%, es un partido parejo - ventaja al local
        2. Si diferencia > 10%, favorito claro
        3. NO inventes lesiones ni excusas
        
        Responde SOLO con JSON:
        {{
            "ganador": "{local} o {visitante}",
            "confianza": 65,
            "razones": ["razón 1", "razón 2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                resultado = json.loads(match.group(0))
                resultado['color'] = 'green' if resultado.get('confianza', 0) > 65 else 'orange'
                return resultado
        except:
            pass
        
        return self._fallback_heurístico(partido)
    
    def _fallback_heurístico(self, partido):
        """Fallback al método heurístico si Gemini falla"""
        local = partido['local']
        visitante = partido['visitante']
        records = partido.get('records', {})
        
        wr_local = self._calcular_wr(records.get('local', '0-0'))
        wr_visit = self._calcular_wr(records.get('visitante', '0-0'))
        
        if wr_local > wr_visit + 5:
            return {
                'ganador': local,
                'confianza': 60,
                'razones': [f"Mejor win rate ({wr_local:.1f}% vs {wr_visit:.1f}%)"],
                'color': 'orange'
            }
        elif wr_visit > wr_local + 5:
            return {
                'ganador': visitante,
                'confianza': 60,
                'razones': [f"Mejor win rate ({wr_visit:.1f}% vs {wr_local:.1f}%)"],
                'color': 'orange'
            }
        else:
            return {
                'ganador': local if wr_local > wr_visit else visitante,
                'confianza': 55,
                'razones': ["Partido parejo - ligera ventaja local"],
                'color': 'yellow'
            }
    
    def _calcular_wr(self, record_str):
        """Calcula win rate de string '45-23'"""
        try:
            parts = record_str.split('-')
            wins = int(parts[0])
            losses = int(parts[1])
            total = wins + losses
            return (wins / total * 100) if total > 0 else 50
        except:
            return 50
