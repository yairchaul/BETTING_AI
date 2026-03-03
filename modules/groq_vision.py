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
        Consulta la API de Groq para obtener una lista de modelos disponibles
        y selecciona el primero que sea un modelo de visión.
        """
        if not self.client:
            st.warning("Cliente de Groq no inicializado.")
            return None

        try:
            # Listar todos los modelos disponibles
            models = self.client.models.list()
            vision_models = []

            # Palabras clave para identificar modelos de visión
            vision_keywords = ['vision', 'llama-3.2-11b', 'llama-3.2-90b']

            for model in models.data:
                model_id = model.id
                # Filtrar modelos que contengan palabras clave de visión
                if any(keyword in model_id for keyword in vision_keywords):
                    vision_models.append(model_id)

            if vision_models:
                # Usar el primer modelo de visión encontrado
                selected_model = vision_models[0]
                st.info(f"✅ Usando modelo de Groq: {selected_model}")
                return selected_model
            else:
                st.warning("⚠️ No se encontró un modelo de visión activo en Groq. Por favor, revisa la documentación de Groq para modelos actualizados.")
                # Modelo de respaldo conocido (podría seguir funcionando)
                return "llama-3.2-11b-vision-preview"

        except Exception as e:
            st.error(f"Error al consultar modelos de Groq: {e}")
            return None

    def encode_image(self, image_bytes):
        """Convierte la imagen a base64."""
        return base64.b64encode(image_bytes).decode('utf-8')

    def extract_matches_with_vision(self, image_bytes):
        """
        Usa Groq Vision para extraer los partidos en formato estructurado.
        """
        if not self.model:
            st.error("No hay un modelo de visión disponible en Groq.")
            return []

        try:
            base64_image = self.encode_image(image_bytes)

            prompt = """
            Esta imagen contiene una tabla de apuestas de fútbol con múltiples partidos.
            Los partidos pueden estar en diferentes formatos. Tu tarea es extraerlos todos.

            Presta atención a estos formatos comunes:

            1.  **Formato de 6 líneas:** Un partido se compone de 6 líneas consecutivas:
                [Equipo Local]
                [Cuota Local] (ej: +148, -176)
                [La palabra "Empate" o "Empaté"]
                [Cuota Empate]
                [Equipo Visitante]
                [Cuota Visitante]

            2.  **Formato de Bloque:** A veces, los partidos están agrupados en bloques con información extra:
                [Nombre de la Liga]
                [+número] (opcional)
                [Equipo Local]
                [Equipo Visitante]
                [Fecha y Hora]
                [1] [+número] (cuota para local)
                [2] [+número] (cuota para empate)
                [3] [+número] (cuota para visitante)

            Extrae TODOS los partidos que veas y devuélvelos en formato JSON con esta estructura:
            [
              {
                "home": "nombre del equipo local",
                "away": "nombre del equipo visitante",
                "all_odds": ["cuota_local", "cuota_empate", "cuota_visitante"]
              }
            ]

            IMPORTANTE:
            - Incluye TODOS los partidos que aparezcan en la imagen.
            - Respeta el orden exacto de los equipos y sus cuotas.
            - Si ves "Empate", "Empaté" o similares, es la palabra clave, no un equipo.
            - Ignora información como fechas, horas o nombres de liga. Solo necesitamos los nombres de los equipos y sus cuotas.
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
                max_tokens=4000,
            )

            content = response.choices[0].message.content
            content = re.sub(r'```json\s*|\s*```', '', content)
            content = re.sub(r'```\s*', '', content)

            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group()

            matches = json.loads(content)
            return matches

        except Exception as e:
            st.error(f"Error en Groq Vision: {e}")
            return []
