# modules/groq_enhancer.py
import streamlit as st
from groq import Groq
import json

class GroqEnhancer:
    """
    Usa Groq para mejorar el análisis cuando faltan datos
    """
    
    def __init__(self):
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        self.model = "llama-3.3-70b-versatile"
    
    def analyze_unknown_teams(self, home_team, away_team):
        """
        Analiza equipos desconocidos usando el conocimiento de Groq
        """
        try:
            prompt = f"""
            Eres un experto en fútbol mundial. Analiza este partido:
            
            EQUIPO LOCAL: {home_team}
            EQUIPO VISITANTE: {away_team}
            
            Necesito que investigues y me digas:
            
            1. ¿En qué país y liga juegan estos equipos?
            2. ¿Son equipos grandes, medianos o pequeños en su liga?
            3. ¿Cómo es su estilo de juego? (ofensivo, defensivo, equilibrado)
            4. ¿Suelen haber muchos goles en sus partidos?
            5. ¿Qué patrón histórico tienen? (local fuerte, visitante débil, etc.)
            6. ¿Qué apuesta recomendarías para este partido y por qué?
            
            Responde SOLO con JSON válido:
            {{
                "pais": "nombre del país",
                "liga": "nombre de la liga",
                "nivel_local": "GRANDE/MEDIANO/PEQUEÑO/DESCONOCIDO",
                "nivel_visitante": "GRANDE/MEDIANO/PEQUEÑO/DESCONOCIDO",
                "estilo_local": "ofensivo/defensivo/equilibrado",
                "estilo_visitante": "ofensivo/defensivo/equilibrado",
                "goles_promedio_liga": número,
                "local_ventaja": "ALTA/MEDIA/BAJA",
                "patron": "descripción breve",
                "mejor_apuesta": "nombre del mercado",
                "probabilidad_estimada": número (0-100),
                "confianza": "ALTA/MEDIA/BAJA",
                "explicacion": "por qué recomiendas esa apuesta"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un enciclopedista de fútbol mundial. Respondes con JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            st.warning(f"Groq no pudo analizar: {e}")
            return None
    
    def get_league_context(self, team_name):
        """
        Pide a Groq contexto sobre la liga de un equipo
        """
        try:
            prompt = f"""
            ¿En qué liga juega {team_name}? Dame información de esa liga:
            - País
            - Nivel (ALTO/MEDIO/BAJO)
            - Goles promedio por partido
            - Ventaja local (ALTA/MEDIA/BAJA)
            - Estilo general
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except:
            return None
