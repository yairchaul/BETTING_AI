"""
ANALIZADOR FÚTBOL GEMINI MEJORADO - Con manejo de errores
"""
import google.generativeai as genai
import json
import re
import streamlit as st

class AnalizadorFutbolGeminiMejorado:
    def __init__(self, api_key):
        self.api_key = api_key
        self.disponible = False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.disponible = True
            print("✅ Gemini Fútbol Mejorado conectado")
        except Exception as e:
            st.warning(f"⚠️ Gemini no disponible: {e}")
    
    def analizar(self, partido, stats_local, stats_visitante, probabilidades):
        """
        Analiza partido con Gemini siguiendo jerarquía estricta
        """
        if not self.disponible:
            return {
                'apuesta': 'GEMINI NO DISPONIBLE',
                'confianza': 0,
                'razones': ['Gemini no está conectado'],
                'color': 'red',
                'tipo': 'gemini'
            }
        
        local = partido['local']
        visitante = partido['visitante']
        liga = partido.get('liga', '')
        
        # Pre-procesamos los datos de lesiones
        lesionados_l = stats_local.get('lesionados', [])
        lesionados_v = stats_visitante.get('lesionados', [])
        
        prompt = f"""
        Eres un analista estadístico de fútbol. Analiza este partido:

        DATOS DEL PARTIDO:
        - {local} vs {visitante} ({liga})
        - Probabilidades Calculadas:
          * BTTS: {probabilidades.get('prob_btts', 0)}%
          * Over 1.5 HT: {probabilidades.get('prob_ht', 0)}%
          * Over 2.5: {probabilidades.get('prob_over25', 0)}%
          * Win Local: {probabilidades.get('prob_local', 0)}%
          * Win Visitante: {probabilidades.get('prob_visitante', 0)}%

        LESIONES CLAVE:
        - {local}: {", ".join(lesionados_l) if lesionados_l else "Ninguna"}
        - {visitante}: {", ".join(lesionados_v) if lesionados_v else "Ninguna"}

        Basado en estos datos, ¿cuál es la mejor apuesta?

        Responde SOLO con JSON:
        {{
            "apuesta": "NOMBRE_APUESTA",
            "confianza": 65,
            "razones": ["razón 1", "razón 2"],
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
        except Exception as e:
            st.warning(f"Error en Gemini: {e}")
        
        return {
            'apuesta': 'Error en análisis',
            'confianza': 0,
            'razones': ['Error al consultar Gemini'],
            'color': 'red',
            'tipo': 'gemini'
        }
