# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq con fallback silencioso"""
        self.api_key = st.secrets.get("GROQ_API_KEY", "")
        self.client = None
        self.is_available = False
        
        # Solo intentar si hay API key
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                # Verificar si hay modelos sin mostrar mensajes
                models = self.client.models.list()
                # Buscar modelos de visión
                vision_models = [m.id for m in models.data if 'vision' in m.id.lower()]
                self.is_available = len(vision_models) > 0
            except:
                self.is_available = False
    
    def extract_matches_with_vision(self, image_bytes):
        """Si no está disponible, retorna None sin mensajes"""
        if not self.is_available:
            return None
        # ... resto del código (si hay modelos disponibles)# modules/groq_vision.py   
    def _initialize_with_retry(self, max_retries=3):
        """Intenta inicializar Groq con reintentos y modelos alternativos"""
        for attempt in range(max_retries):
            try:
                self.client = Groq(api_key=self.api_key)
                self._fetch_available_models()
                
                if self.available_models:
                    self.model = self.available_models[0]
                    self.is_available = True
                    st.success(f"✅ Groq Vision activo con modelo: {self.model}")
                    return
                else:
                    st.warning(f"⚠️ Intento {attempt + 1}: No se encontró modelo de visión")
            except Exception as e:
                st.warning(f"⚠️ Intento {attempt + 1} falló: {e}")
            time.sleep(1)
        
        st.warning("⚠️ Groq Vision no disponible - Usando solo Google Vision")
        self.is_available = False
    
    def _fetch_available_models(self):
        """Obtiene modelos de visión disponibles"""
        try:
            models = self.client.models.list()
            
            # Palabras clave para identificar modelos de visión
            vision_keywords = ['vision', 'llama-3.2', 'llava']
            
            self.available_models = [
                m.id for m in models.data 
                if any(keyword in m.id.lower() for keyword in vision_keywords)
            ]
            
            # Ordenar por preferencia (modelos más nuevos primero)
            preferred = ['llama-3.2-90b-vision-preview', 'llama-3.2-11b-vision-preview']
            self.available_models.sort(key=lambda x: (
                -preferred.index(x) if x in preferred else 0
            ))
            
        except Exception as e:
            st.error(f"Error consultando modelos: {e}")
            self.available_models = []
    
    def encode_image(self, image_bytes):
        """Convierte la imagen a base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_matches_with_vision(self, image_bytes):
        """Usa Groq Vision con múltiples estrategias de prompt"""
        if not self.is_available:
            return None
        
        prompts = [
            # Prompt para formato de 10 líneas (tu imagen)
            """
            Esta imagen contiene partidos de fútbol en este formato exacto:
            
            [+Número]
            [Equipo Local]
            [Equipo Visitante]
            [Fecha]
            1
            X
            2
            [Cuota Local]
            [Cuota Empate]
            [Cuota Visitante]
            
            Extrae TODOS los partidos. Devuelve JSON con home, away, all_odds [cuota_local, cuota_empate, cuota_visitante]
            """,
            
            # Prompt para formato de 6 líneas
            """
            Extrae los partidos de fútbol de esta imagen. Cada partido tiene:
            1. Nombre del equipo local
            2. Cuota local (+/- números)
            3. Palabra "Empate"
            4. Cuota empate
            5. Nombre del equipo visitante
            6. Cuota visitante
            
            Devuelve JSON con objetos {home, away, all_odds: [cuota_local, cuota_empate, cuota_visitante]}
            """,
            
            # Prompt para formato de 1 línea
            """
            La imagen contiene líneas con este formato:
            [Local] [Cuota L] [Empate] [Cuota E] [Visitante] [Cuota V]
            
            Extrae todos los partidos en formato JSON.
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
                if matches:
                    return matches
                    
            except Exception as e:
                if i == len(prompts) - 1:
                    st.warning(f"Groq Vision falló con todos los prompts: {e}")
                continue
        
        return None
        
