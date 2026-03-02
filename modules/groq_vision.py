# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq"""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        # Modelo de visión de Groq
        self.model = "llama-3.2-90b-vision-preview"
    
    def encode_image(self, image_bytes):
        """Convierte la imagen a base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision para extraer los partidos en formato estructurado
        """
        try:
            base64_image = self.encode_image(image_bytes)
            
            # Prompt diseñado específicamente para tu formato de tabla de 6 columnas
            prompt = """
            Esta imagen contiene una tabla de apuestas de fútbol con múltiples partidos.
            La tabla tiene 6 columnas en este orden:
            1. Equipo Local
            2. Cuota Local (formato americano: +178, -278, etc)
            3. La palabra "Empate"
            4. Cuota de Empate (formato americano)
            5. Equipo Visitante
            6. Cuota Visitante (formato americano)

            Ejemplo del formato:
            Real Madrid -278 Empate +340 Getafe +900

            Extrae TODOS los partidos que veas en la imagen y devuélvelos en formato JSON con esta estructura:
            [
              {
                "home": "nombre del equipo local",
                "away": "nombre del equipo visitante",
                "all_odds": ["cuota_local", "cuota_empate", "cuota_visitante"]
              }
            ]

            IMPORTANTE:
            - Incluye TODOS los partidos que aparezcan en la imagen
            - Respeta los nombres completos de los equipos
            - Mantén los signos (+ o -) en las cuotas
            - Si la palabra "Empate" aparece como "Empaté" o variantes, normalízala a "Empate"
            - No incluyas texto adicional fuera del JSON
            """
            
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
                max_tokens=2000,
            )
            
            # Extraer el JSON de la respuesta
            content = response.choices[0].message.content
            
            # Limpiar la respuesta (a veces viene con markdown)
            content = re.sub(r'```json\s*|\s*```', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # Buscar el patrón JSON en la respuesta
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            # Parsear JSON
            matches = json.loads(content)
            
            return matches
            
        except Exception as e:
            st.error(f"Error en Groq Vision: {e}")
            return []
    
    def extract_matches_simple(self, image_bytes):
        """
        Versión simplificada si la anterior falla
        """
        try:
            base64_image = self.encode_image(image_bytes)
            
            prompt = """
            Esta imagen contiene una tabla de fútbol. Dame SOLO los nombres de los equipos y sus cuotas.
            Formato de respuesta JSON:
            [
              {
                "home": "equipo local",
                "away": "equipo visitante", 
                "odds": ["cuota_local", "cuota_empate", "cuota_visitante"]
              }
            ]
            """
            
            response = self.client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
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
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            content = re.sub(r'```json\s*|\s*```', '', content)
            content = re.sub(r'```\s*', '', content)
            
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            return json.loads(content)
            
        except Exception as e:
            st.error(f"Error en Groq Vision simple: {e}")
            return []
