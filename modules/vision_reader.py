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
            
            # Primero mostramos el debug con la estructura actual
            st.write("### 📊 Estructura detectada por OCR:")
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            # Crear tabla temporal para mostrar cómo está leyendo el OCR
            html_temp = "<table style='width:100%; border-collapse: collapse;'>"
            html_temp += "<tr style='background-color: #FF5722; color: white;'>"
            html_temp += "<th style='padding: 8px; border: 1px solid #ddd;'>#</th>"
            html_temp += "<th style='padding: 8px; border: 1px solid #ddd;'>Línea detectada</th>"
            html_temp += "</tr>"
            
            for i, line in enumerate(lines[:20]):  # Mostrar primeras 20 líneas
                html_temp += f"<tr><td style='padding: 8px; border: 1px solid #ddd;'>{i+1}</td>"
                html_temp += f"<td style='padding: 8px; border: 1px solid #ddd;'>{line}</td></tr>"
            
            html_temp += "</table>"
            st.markdown(html_temp, unsafe_allow_html=True)
            
            # Ahora procesamos con una lógica más inteligente
            return self.parse_with_context(full_text)
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def parse_with_context(self, text):
        """
        Interpreta el texto respetando los nombres completos de los equipos
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # ============================================================================
        # PASO 1: Identificar el patrón de la tabla de 6 columnas en el debug
        # ============================================================================
        matches = []
        
        # Buscar el patrón: Equipo, Cuota, Empate, Cuota, Equipo, Cuota
        i = 0
        while i < len(lines) - 5:
            # Posibles elementos de una fila completa
            posible_local = lines[i]
            posible_cuota_local = lines[i+1]
            posible_empate = lines[i+2]
            posible_cuota_empate = lines[i+3]
            posible_visitante = lines[i+4]
            posible_cuota_visitante = lines[i+5]
            
            # Validar el patrón
            if (self.is_team_name(posible_local) and
                self.is_odds(posible_cuota_local) and
                "Empate" in posible_empate and
                self.is_odds(posible_cuota_empate) and
                self.is_team_name(posible_visitante) and
                self.is_odds(posible_cuota_visitante)):
                
                # Verificar que los nombres de equipos no sean parte de un nombre más grande
                local_completo = self.get_full_team_name(posible_local, lines, i)
                visitante_completo = self.get_full_team_name(posible_visitante, lines, i+4)
                
                matches.append({
                    "home": local_completo,
                    "away": visitante_completo,
                    "all_odds": [
                        posible_cuota_local,
                        posible_cuota_empate,
                        posible_cuota_visitante
                    ]
                })
                i += 6
            else:
                i += 1
        
        # ============================================================================
        # PASO 2: Si no encuentra, usar el método de agrupación por contexto
        # ============================================================================
        if not matches:
            # Lista de equipos conocidos de LaLiga para reconstruir nombres
            equipos_conocidos = [
                "Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Bilbao",
                "Real Sociedad", "Real Betis", "Villarreal", "Valencia",
                "Sevilla", "Espanyol", "Getafe", "Rayo Vallecano",
                "Celta de Vigo", "Real Valladolid", "Osasuna", "Cadiz",
                "Almeria", "Elche", "RCD Mallorca", "Girona",
                "Real Oviedo", "Levante", "Granada", "Las Palmas",
                "Racing Santander", "Sporting Gijon", "Zaragoza", "Tenerife"
            ]
            
            # Extraer todas las odds
            odds_list = [line for line in lines if self.is_odds(line)]
            
            # Extraer todas las palabras que parecen equipos
            team_parts = []
            for line in lines:
                if self.is_team_name(line) and "Empate" not in line:
                    team_parts.append(line)
            
            # Intentar reconstruir nombres completos
            st.write("### 🔍 Reconstruyendo nombres de equipos:")
            
            # Crear tabla de reconstrucción
            html_rebuild = "<table style='width:100%; border-collapse: collapse;'>"
            html_rebuild += "<tr style='background-color: #4CAF50; color: white;'>"
            html_rebuild += "<th style='padding: 8px; border: 1px solid #ddd;'>#</th>"
            html_rebuild += "<th style='padding: 8px; border: 1px solid #ddd;'>Partes detectadas</th>"
            html_rebuild += "<th style='padding: 8px; border: 1px solid #ddd;'>Posible equipo</th>"
            html_rebuild += "</tr>"
            
            # Agrupar partes para formar nombres completos
            i = 0
            reconstruidos = []
            while i < len(team_parts):
                current = team_parts[i]
                combinado = current
                
                # Verificar si combinado con el siguiente forma un equipo conocido
                if i + 1 < len(team_parts):
                    prueba = current + " " + team_parts[i+1]
                    for equipo in equipos_conocidos:
                        if prueba.lower() in equipo.lower() or equipo.lower() in prueba.lower():
                            combinado = prueba
                            i += 1
                            break
                
                reconstruidos.append(combinado)
                html_rebuild += f"<tr><td style='padding: 8px; border: 1px solid #ddd;'>{len(reconstruidos)}</td>"
                html_rebuild += f"<td style='padding: 8px; border: 1px solid #ddd;'>{current}</td>"
                html_rebuild += f"<td style='padding: 8px; border: 1px solid #ddd;'>{combinado}</td></tr>"
                i += 1
            
            html_rebuild += "</table>"
            st.markdown(html_rebuild, unsafe_allow_html=True)
            
            # Construir matches con los nombres reconstruidos
            num_partidos = min(len(reconstruidos) // 2, len(odds_list) // 3)
            for j in range(num_partidos):
                if j * 2 + 1 < len(reconstruidos) and j * 3 + 2 < len(odds_list):
                    matches.append({
                        "home": reconstruidos[j * 2],
                        "away": reconstruidos[j * 2 + 1],
                        "all_odds": [
                            odds_list[j * 3],
                            odds_list[j * 3 + 1],
                            odds_list[j * 3 + 2]
                        ]
                    })
        
        return matches

    def get_full_team_name(self, start_word, all_lines, start_index):
        """
        Intenta obtener el nombre completo del equipo mirando las líneas siguientes
        """
        nombre = start_word
        i = start_index + 1
        
        # Mirar las siguientes líneas para ver si forman parte del mismo equipo
        while i < len(all_lines):
            next_word = all_lines[i]
            # Si la siguiente línea es una odds o "Empate", detenerse
            if self.is_odds(next_word) or "Empate" in next_word:
                break
            # Si no, probablemente es parte del nombre
            nombre += " " + next_word
            i += 1
        
        return nombre.strip()

    def is_team_name(self, text):
        """Determina si un texto es probable nombre de equipo"""
        if not text or len(text) < 2:
            return False
        if re.match(r'^[+-]\d{3,4}$', text):
            return False
        if "Empate" in text or "empate" in text.lower():
            return False
        if not re.search(r'[A-Za-z]', text):
            return False
        if re.match(r'^\d{1,2}\s+[A-Za-z]{3}', text) or re.match(r'^\d{2}:\d{2}$', text):
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
