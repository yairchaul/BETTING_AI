# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re
import time

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq con fallback automático"""
        self.api_key = st.secrets.get("GROQ_API_KEY", "")
        self.client = None
        self.model = None
        self.is_available = False
        
        if self.api_key:
            self._initialize_with_retry()
    
    def _initialize_with_retry(self, max_retries=3):
        """Intenta inicializar Groq con reintentos y modelos alternativos"""
        for attempt in range(max_retries):
            try:
                self.client = Groq(api_key=self.api_key)
                self.model = self._get_best_available_model()
                if self.model:
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
    
    def _get_best_available_model(self):
        """Obtiene el mejor modelo de visión disponible con múltiples estrategias"""
        try:
            # Estrategia 1: Listar modelos directamente
            models = self.client.models.list()
            
            # Modelos de visión conocidos (ordenados por preferencia)
            preferred_vision_models = [
                "llama-3.2-11b-vision-preview",
                "llama-3.2-90b-vision-preview",
                "llava-v1.5-7b-4096-preview",
                "llava-v1.5-13b-4096-preview"
            ]
            
            # Buscar modelos de visión disponibles
            available_models = [m.id for m in models.data]
            vision_models = [m for m in preferred_vision_models if m in available_models]
            
            if vision_models:
                return vision_models[0]
            
            # Estrategia 2: Buscar cualquier modelo con "vision" en el nombre
            vision_models = [m for m in available_models if 'vision' in m.lower()]
            if vision_models:
                return vision_models[0]
            
            return None
            
        except Exception as e:
            st.error(f"Error consultando modelos: {e}")
            return None
    
    def encode_image(self, image_bytes):
        """Convierte la imagen a base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision con múltiples estrategias de prompt
        """
        if not self.is_available:
            return None
        
        prompts = [
            # Prompt para formato de 6 líneas
            """
            Extrae los partidos de fútbol de esta imagen. Cada partido tiene:
            1. Nombre del equipo local
            2. Cuota local (+/- números)
            3. Palabra "Empate"
            4. Cuota empate
            5. Nombre del equipo visitante
            6. Cuota visitante
            
            Devuelve SOLO un array JSON con objetos {home, away, all_odds: [cuota_local, cuota_empate, cuota_visitante]}
            """,
            
            # Prompt para formato de bloques
            """
            Esta imagen contiene partidos de fútbol. Cada partido puede tener:
            - Nombre de liga
            - Equipo local y visitante
            - Fecha/hora
            - Cuotas etiquetadas como 1, 2, 3 (local, empate, visitante)
            
            Extrae TODOS los partidos. Devuelve JSON con home, away, all_odds [cuota_local, cuota_empate, cuota_visitante]
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