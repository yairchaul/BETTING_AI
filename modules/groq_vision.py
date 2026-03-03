# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq con el nuevo modelo estable."""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        # Se actualiza al modelo 'instant' que reemplaza a los 'preview' decommissioned
        self.model = "llama-3.2-11b-vision-instant"

    def encode_image(self, image_bytes):
        """Convierte la imagen a base64."""
        return base64.b64encode(image_bytes).decode('utf-8')

    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision para extraer partidos. 
        Mantiene la estructura original del código del usuario.
        """
        if not self.client.api_key:
            st.error("API Key de Groq no configurada en secrets.")
            return []

        try:
            base64_image = self.encode_image(image_bytes)

            # Prompt optimizado para la estructura visual de tu imagen (Melbourne, Fethiyespor, etc.)
            prompt = """
            Analiza esta imagen de apuestas deportivas. 
            Extrae los nombres de los equipos y las cuotas de los mercados 1, X, 2 (Local, Empate, Visitante).
            
            Reglas de extracción:
            1. El primer equipo es 'home', el segundo es 'away'.
            2. Las cuotas están en los cuadros debajo de 1, X, 2.
            3. Si el cuadro tiene un candado, pon "LOCKED".
            
            Devuelve ESTRICTAMENTE un JSON array:
            [
              {
                "home": "Nombre Local",
                "away": "Nombre Visitante",
                "all_odds": ["+125", "+220", "+200"]
              }
            ]
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
                temperature=0, # Menor temperatura para mayor precisión en datos numéricos
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            
            # --- Lógica de limpieza original preservada ---
            content = re.sub(r'```json\s*|\s*```', '', content)
            content = re.sub(r'```\s*', '', content)

            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()

            return json.loads(content)

        except Exception as e:
            # Mantenemos el reporte de error original
            st.error(f"Error en Groq Vision: {e}")
            return []
