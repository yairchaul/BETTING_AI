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
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return []

            full_text = texts[0].description
            return self.parse_table_structure(full_text)
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return []

    def parse_table_structure(self, text):
        """
        Interpreta la estructura de tabla de 2 partes:
        PARTE 1: Equipos Locales + Cuotas Locales + "Empate" + Cuotas Empate
        PARTE 2: Equipos Visitantes + Cuotas Visitantes
        """
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # ============================================================================
        # 1. DETECTAR EQUIPOS LOCALES Y SUS CUOTAS (Primera parte)
        # ============================================================================
        equipos_locales = []
        cuotas_locales = []
        cuotas_empate = []
        
        i = 0
        # Los primeros 5 equipos son los locales
        while i < len(lines) and len(equipos_locales) < 5:
            line = lines[i]
            
            # Si la línea parece un equipo (contiene letras, no es número)
            if re.search(r'[A-Za-z]', line) and "Empate" not in line:
                equipos_locales.append(line)
                i += 1
                
                # La siguiente línea debería ser la cuota local
                if i < len(lines) and re.match(r'[+-]\d{3,4}', lines[i]):
                    cuotas_locales.append(lines[i])
                    i += 1
                    
                    # La siguiente línea debería ser "Empate"
                    if i < len(lines) and "Empate" in lines[i]:
                        i += 1
                        
                        # La siguiente línea debería ser la cuota de empate
                        if i < len(lines) and re.match(r'[+-]\d{3,4}', lines[i]):
                            cuotas_empate.append(lines[i])
                            i += 1
            else:
                i += 1
        
        # ============================================================================
        # 2. DETECTAR EQUIPOS VISITANTES Y SUS CUOTAS (Segunda parte)
        # ============================================================================
        equipos_visitantes = []
        cuotas_visitantes = []
        
        # Continuar desde donde quedamos
        while i < len(lines) and len(equipos_visitantes) < 5:
            line = lines[i]
            
            # Buscar equipos visitantes
            if re.search(r'[A-Za-z]', line) and "Empate" not in line:
                equipos_visitantes.append(line)
                i += 1
                
                # La siguiente línea debería ser la cuota visitante
                if i < len(lines) and re.match(r'[+-]\d{3,4}', lines[i]):
                    cuotas_visitantes.append(lines[i])
                    i += 1
            else:
                i += 1
        
        # ============================================================================
        # 3. CONSTRUIR MATCHES
        # ============================================================================
        matches = []
        for j in range(min(len(equipos_locales), len(equipos_visitantes))):
            if (j < len(cuotas_locales) and 
                j < len(cuotas_empate) and 
                j < len(cuotas_visitantes)):
                
                matches.append({
                    "home": equipos_locales[j],
                    "away": equipos_visitantes[j],
                    "all_odds": [
                        cuotas_locales[j],
                        cuotas_empate[j],
                        cuotas_visitantes[j]
                    ]
                })
        
        return matches

    def parse_alternative(self, text):
        """
        Método alternativo si el principal falla
        """
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Buscar patrones de 4 líneas consecutivas: Equipo, Cuota, "Empate", Cuota
        matches = []
        i = 0
        while i < len(lines) - 3:
            if (re.search(r'[A-Za-z]', lines[i]) and 
                re.match(r'[+-]\d{3,4}', lines[i+1]) and 
                "Empate" in lines[i+2] and 
                re.match(r'[+-]\d{3,4}', lines[i+3])):
                
                # Este es un local, buscar su visitante después
                local = lines[i]
                cuota_local = lines[i+1]
                cuota_empate = lines[i+3]
                
                # Buscar visitante (debe ser después de todos los locales)
                i += 4
            
            i += 1
        
        return matches


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
