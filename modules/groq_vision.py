# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re
import time

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq con fallback silencioso"""
        self.api_key = st.secrets.get("GROQ_API_KEY", "")
        self.client = None
        self.model = None
        self.is_available = False
        self.available_models = []
        
        # Solo intentar si hay API key
        if self.api_key:
            self._initialize_with_retry()
    
    def _initialize_with_retry(self, max_retries=2):
        """Intenta inicializar Groq con reintentos (silencioso)"""
        for attempt in range(max_retries):
            try:
                self.client = Groq(api_key=self.api_key)
                self._fetch_available_models()
                
                if self.available_models:
                    self.model = self.available_models[0]
                    self.is_available = True
                    # Solo mostrar éxito si realmente hay modelo (sin warnings)
                    return
                else:
                    # Silencioso - no mostrar advertencias
                    pass
            except:
                # Silencioso - no mostrar errores
                pass
            time.sleep(0.5)
        
        self.is_available = False
    
    def _fetch_available_models(self):
        """Obtiene modelos de visión disponibles (silencioso)"""
        try:
            models = self.client.models.list()
            
            # Palabras clave para identificar modelos de visión
            vision_keywords = ['vision', 'llama-3.2', 'llava']
            
            self.available_models = [
                m.id for m in models.data 
                if any(keyword in m.id.lower() for keyword in vision_keywords)
            ]
            
            # Ordenar por preferencia
            preferred = ['llama-3.2-90b-vision-preview', 'llama-3.2-11b-vision-preview']
            self.available_models.sort(key=lambda x: (
                -preferred.index(x) if x in preferred else 0
            ))
            
        except:
            self.available_models = []
    
    def encode_image(self, image_bytes):
        """Convierte la imagen a base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision con múltiples estrategias de prompt
        Retorna None silenciosamente si no está disponible
        """
        if not self.is_available or not self.model:
            return None
        
        prompts = [
            # Prompt para formato de 9-10 líneas
            """
            Esta imagen contiene partidos de fútbol. Puede estar en este formato:
            
            [+Número]
            [Equipo Local]
            [Equipo Visitante]
            [Fecha]
            1
            [X] (opcional)
            2
            [Cuota Local]
            [Cuota Empate]
            [Cuota Visitante]
            
            Extrae TODOS los partidos. Devuelve JSON con home, away, all_odds.
            """,
            
            # Prompt para formato de 6 líneas
            """
            Extrae los partidos de fútbol de esta imagen. Cada partido tiene:
            1. Equipo local
            2. Cuota local
            3. Palabra "Empate"
            4. Cuota empate
            5. Equipo visitante
            6. Cuota visitante
            
            Devuelve JSON con objetos {home, away, all_odds}.
            """,
            
            # Prompt para formato de 1 línea
            """
            La imagen contiene líneas con formato:
            [Local] [Cuota L] [Empate] [Cuota E] [Visitante] [Cuota V]
            
            Extrae todos los partidos en formato JSON.
            """,
            
            # Prompt para lista vertical
            """
            La imagen contiene una lista vertical de equipos con sus cuotas.
            Agrupa los equipos en partidos (local y visitante) con sus cuotas.
            Devuelve JSON con objetos {home, away, all_odds}.
            """
        ]
        
        for i, prompt in enumerate(prompts):
            try:
                base64_image = self.encode_image(image_bytes)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.1,
                    max_tokens=4000,
                )
                
                content = response.choices[0].message.content
                content = re.sub(r'```json\s*|\s*```', '', content)
                content = re.sub(r'```\s*', '', content)
                
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    content = json_match.group()
                
                matches = json.loads(content)
                if matches and len(matches) > 0:
                    return matches
                    
            except:
                # Silencioso - intentar con el siguiente prompt
                continue
        
        return None
        
