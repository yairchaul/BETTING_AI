# modules/groq_vision.py
import base64
import streamlit as st
from groq import Groq
import json
import re

class GroqVisionParser:
    def __init__(self):
        """Inicializa el cliente de Groq y obtiene un modelo de visión activo."""
        self.client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        self.model = self._get_available_vision_model()

    def _get_available_vision_model(self):
        """
        Consulta la API de Groq y selecciona el modelo 'instant' para evitar errores de baja.
        """
        if not self.client:
            return "llama-3.2-11b-vision-instant"

        try:
            models = self.client.models.list()
            vision_models = [m.id for m in models.data if "vision" in m.id and "preview" not in m.id]
            
            if "llama-3.2-11b-vision-instant" in vision_models:
                return "llama-3.2-11b-vision-instant"
            return vision_models[0] if vision_models else "llama-3.2-11b-vision-instant"
        except:
            return "llama-3.2-11b-vision-instant"

    def encode_image(self, image_bytes):
        """Convierte la imagen a base64."""
        return base64.b64encode(image_bytes).decode('utf-8')

    def extract_matches_with_vision(self, image_bytes):
        """
        Extrae partidos y valida cuotas bloqueadas (candados).
        """
        if not self.model:
            return []

        try:
            base64_image = self.encode_image(image_bytes)

            prompt = """
            Analiza la imagen de apuestas. Para cada partido:
            1. Identifica Equipo Local y Visitante.
            2. Extrae cuotas 1, X, 2. 
            3. SI HAY UN CANDADO, la cuota es "LOCKED".
            4. Limpia los nombres: quita (M), (W), (R), etc.
            
            Devuelve solo JSON:
            [{"home": "Nombre", "away": "Nombre", "all_odds": ["1", "X", "2"]}]
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                temperature=0,
            )

            content = response.choices[0].message.content
            # Limpieza de Markdown
            content = re.sub(r'```json\s*|\s*```|```', '', content)
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            
            if json_match:
                matches = json.loads(json_match.group())
                # Validación extra: Filtrar partidos con cuotas bloqueadas
                valid_matches = []
                for m in matches:
                    if "LOCKED" in m['all_odds']:
                        st.warning(f"⚠️ Partido omitido por cuotas bloqueadas: {m['home']} vs {m['away']}")
                    else:
                        valid_matches.append(m)
                return valid_matches
            
            return []

        except Exception as e:
            st.error(f"Error en Groq Vision: {e}")
            return []
