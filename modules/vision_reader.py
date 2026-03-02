# modules/vision_reader.py
import re
import streamlit as st
from google.cloud import vision

class ImageParser:
    def __init__(self):
        """Inicializa el cliente de Google Vision"""
        try:
            self.client = vision.ImageAnnotatorClient.from_service_account_info(
                dict(st.secrets["google_credentials"])
            )
        except Exception as e:
            st.error(f"Error inicializando Google Vision: {e}")
            self.client = None

    def process_image(self, image_bytes):
        """Procesa la imagen y extrae pares de equipos"""
        if not self.client:
            return []
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return []

            full_text = texts[0].description
            
            # ============================================================================
            # ORGANIZAR EN 6 COLUMNAS
            # ============================================================================
            return self.organize_six_columns(full_text)
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def organize_six_columns(self, text):
        """
        Organiza el texto en 6 columnas:
        Col1: Equipo Local
        Col2: Cuota Local
        Col3: "Empate"
        Col4: Cuota Empate
        Col5: Equipo Visitante
        Col6: Cuota Visitante
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # ============================================================================
        # PASO 1: Identificar todos los elementos
        # ============================================================================
        elementos = []
        for line in lines:
            # Si la línea contiene espacios, podría tener múltiples elementos
            if ' ' in line and len(line.split()) > 1:
                partes = line.split()
                for parte in partes:
                    if parte:  # Evitar vacíos
                        elementos.append(parte)
            else:
                elementos.append(line)
        
        # ============================================================================
        # PASO 2: Clasificar cada elemento
        # ============================================================================
        col1 = []  # Equipos Locales
        col2 = []  # Cuotas Locales
        col3 = []  # "Empate"
        col4 = []  # Cuotas Empate
        col5 = []  # Equipos Visitantes
        col6 = []  # Cuotas Visitantes
        
        i = 0
        while i < len(elementos):
            elemento = elementos[i]
            
            # Detectar si es una odds
            if re.match(r'^[+-]\d{3,4}$', elemento):
                # Determinar qué columna de odds es según el contexto
                if len(col2) <= len(col1):  # Si faltan cuotas locales
                    col2.append(elemento)
                elif len(col4) < len(col2):  # Si faltan cuotas de empate
                    col4.append(elemento)
                else:  # Si no, es cuota visitante
                    col6.append(elemento)
            
            # Detectar si es "Empate"
            elif "Empate" in elemento or "empaté" in elemento.lower():
                col3.append("Empate")
            
            # Si no es odds ni "Empate", es nombre de equipo
            elif len(elemento) > 2 and re.search(r'[A-Za-z]', elemento):
                # Determinar si es local o visitante
                if len(col1) <= len(col5):  # Si hay menos locales que visitantes
                    col1.append(elemento)
                else:
                    col5.append(elemento)
            
            i += 1
        
        # ============================================================================
        # PASO 3: Mostrar la estructura en forma de tabla para debug
        # ============================================================================
        st.write("### 📊 Estructura de 6 columnas detectada:")
        
        # Crear tabla HTML
        html_table = "<table style='width:100%; border-collapse: collapse;'>"
        html_table += "<tr style='background-color: #4CAF50; color: white;'>"
        html_table += "<th style='padding: 8px; border: 1px solid #ddd;'>Local</th>"
        html_table += "<th style='padding: 8px; border: 1px solid #ddd;'>Cuota L</th>"
        html_table += "<th style='padding: 8px; border: 1px solid #ddd;'>Empate</th>"
        html_table += "<th style='padding: 8px; border: 1px solid #ddd;'>Cuota E</th>"
        html_table += "<th style='padding: 8px; border: 1px solid #ddd;'>Visitante</th>"
        html_table += "<th style='padding: 8px; border: 1px solid #ddd;'>Cuota V</th>"
        html_table += "</tr>"
        
        max_rows = max(len(col1), len(col2), len(col3), len(col4), len(col5), len(col6))
        for j in range(max_rows):
            html_table += "<tr>"
            
            # Columna 1: Local
            val1 = col1[j] if j < len(col1) else ""
            html_table += f"<td style='padding: 8px; border: 1px solid #ddd;'>{val1}</td>"
            
            # Columna 2: Cuota Local
            val2 = col2[j] if j < len(col2) else ""
            html_table += f"<td style='padding: 8px; border: 1px solid #ddd;'>{val2}</td>"
            
            # Columna 3: Empate
            val3 = col3[j] if j < len(col3) else ""
            html_table += f"<td style='padding: 8px; border: 1px solid #ddd;'>{val3}</td>"
            
            # Columna 4: Cuota Empate
            val4 = col4[j] if j < len(col4) else ""
            html_table += f"<td style='padding: 8px; border: 1px solid #ddd;'>{val4}</td>"
            
            # Columna 5: Visitante
            val5 = col5[j] if j < len(col5) else ""
            html_table += f"<td style='padding: 8px; border: 1px solid #ddd;'>{val5}</td>"
            
            # Columna 6: Cuota Visitante
            val6 = col6[j] if j < len(col6) else ""
            html_table += f"<td style='padding: 8px; border: 1px solid #ddd;'>{val6}</td>"
            
            html_table += "</tr>"
        
        html_table += "</table>"
        st.markdown(html_table, unsafe_allow_html=True)
        
        # ============================================================================
        # PASO 4: Construir matches con la estructura correcta
        # ============================================================================
        matches = []
        for j in range(min(len(col1), len(col5))):  # Usar el mínimo entre locales y visitantes
            if (j < len(col2) and j < len(col4) and j < len(col6)):
                matches.append({
                    "home": col1[j],
                    "away": col5[j],
                    "all_odds": [
                        col2[j],
                        col4[j],
                        col6[j]
                    ]
                })
        
        return matches

    def is_team_name(self, text):
        """Determina si un texto es probable nombre de equipo"""
        if not text or len(text) < 2:
            return False
        if re.match(r'^[+-]\d{3,4}$', text):
            return False
        if text == "Empate" or "empate" in text.lower():
            return False
        if not re.search(r'[A-Za-z]', text):
            return False
        return True

    def is_odds(self, text):
        """Determina si un texto es una odds"""
        return bool(re.match(r'^[+-]\d{3,4}$', text))


# Función de respaldo para entrada manual
def procesar_texto_manual(texto):
    """Procesa texto ingresado manualmente"""
    lineas = texto.split('\n')
    partidos = []
    for linea in lineas:
        if ' vs ' in linea.lower():
            teams = re.split(r' vs ', linea, flags=re.IGNORECASE)
            if len(teams) == 2:
                partidos.append({
                    "home": teams[0].strip(), 
                    "away": teams[1].strip(),
                    "all_odds": ['N/A', 'N/A', 'N/A']
                })
    return partidos
