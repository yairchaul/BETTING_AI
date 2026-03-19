"""
ANALIZADOR FÚTBOL GEMINI - Análisis con IA
"""
import google.generativeai as genai
import json
import re
import streamlit as st

class AnalizadorFutbolGemini:
    def __init__(self, api_key):
        self.api_key = api_key
        self.disponible = False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.disponible = True
            print("✅ Gemini Fútbol conectado")
        except Exception as e:
            st.warning(f"⚠️ Gemini no disponible: {e}")
    
    def analizar(self, partido, stats_local, stats_visitante, resultado_heurístico):
        """
        Analiza partido con Gemini
        """
        if not self.disponible:
            return {
                'apuesta': 'GEMINI NO DISPONIBLE',
                'confianza': 0,
                'razones': [],
                'color': 'red',
                'tipo': 'gemini'
            }
        
        local = partido['local']
        visitante = partido['visitante']
        liga = partido.get('liga', '')
        
        # Extraer estadísticas resumidas
        goles_local = [p.get('goles_favor', 0) for p in stats_local.get('ultimos_5', [])]
        goles_visit = [p.get('goles_favor', 0) for p in stats_visitante.get('ultimos_5', [])]
        goles_ht_local = [p.get('goles_ht', 0) for p in stats_local.get('ultimos_5', [])]
        
        prompt = f"""
        Eres un analista de fútbol experto. Analiza este partido:
        
        **{local} vs {visitante}** ({liga})
        
        ESTADÍSTICAS ÚLTIMOS 5 PARTIDOS:
        
        {local}:
        - Goles: {goles_local}
        - Goles HT: {goles_ht_local}
        - Victorias: {stats_local.get('victorias_recientes', 0)}/5
        - Lesionados: {len(stats_local.get('lesionados', []))}
        
        {visitante}:
        - Goles: {goles_visit}
        - Victorias: {stats_visitante.get('victorias_recientes', 0)}/5
        - Lesionados: {len(stats_visitante.get('lesionados', []))}
        
        PROBABILIDADES HEURÍSTICAS:
        - Over 1.5 HT: {resultado_heurístico.get('prob_ht', 0)}%
        - Over 2.5: {resultado_heurístico.get('prob_over25', 0)}%
        - Over 3.5: {resultado_heurístico.get('prob_over35', 0)}%
        - BTTS: {resultado_heurístico.get('prob_btts', 0)}%
        
        Basado en estos datos, ¿cuál es la MEJOR apuesta?
        Considera las 6 opciones: Over HT, Over FT, BTTS, Over específico, Ganador, Combinación.
        
        Responde SOLO con JSON:
        {{
            "apuesta": "OVER 2.5",
            "confianza": 68,
            "razones": ["Razón 1", "Razón 2"],
            "color": "green"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                resultado = json.loads(match.group(0))
                resultado['tipo'] = 'gemini'
                return resultado
        except:
            pass
        
        return {
            'apuesta': 'Error en análisis',
            'confianza': 0,
            'razones': [],
            'color': 'red',
            'tipo': 'gemini'
        }
