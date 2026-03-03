# modules/universal_parser.py
import re
import streamlit as st

class UniversalParser:
    """
    Parser universal que detecta automáticamente el formato de la imagen
    y extrae los partidos correctamente.
    """
    
    def __init__(self):
        self.forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']
    
    def _preprocess_lines(self, lines):
        """
        Preprocesa las líneas para corregir el formato antes del parsing.
        Detecta líneas como "-118 Empate" y las separa en dos líneas.
        """
        processed_lines = []
        
        for line in lines:
            # Buscar patrones como: [-118] [Empate] (la cuota pegada a "Empate")
            match = re.match(r'^([+-]\d{3,4})\s+(Empate.*?)$', line, re.IGNORECASE)
            if match:
                # Separar en dos líneas
                processed_lines.append(match.group(1))  # La cuota
                processed_lines.append(match.group(2))  # "Empate"
            else:
                processed_lines.append(line)
        
        return processed_lines
    
    def parse(self, text):
        """Método principal: preprocesa y luego parsea"""
        raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # PREPROCESAMIENTO: Separar cuotas pegadas a "Empate"
        lines = self._preprocess_lines(raw_lines)
        
        # DEBUG: Mostrar líneas después del preprocesamiento
        # st.write("📄 Líneas después de preprocesar:", lines)
        
        matches = []
        
        # ESTRATEGIA 1: Formato de 6 líneas (el de tu imagen)
        six_line_matches = self._parse_six_line_format(lines)
        matches.extend(six_line_matches)
        
        # ESTRATEGIA 2: Formato de 1 línea (6 columnas) - como fallback
        if len(matches) == 0:
            one_line_matches = self._parse_one_line_format(lines)
            matches.extend(one_line_matches)
        
        # Eliminar duplicados
        unique_matches = []
        seen = set()
        for match in matches:
            key = (match.get('home', ''), match.get('away', ''))
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches
    
    def _parse_six_line_format(self, lines):
        """
        Formato de 6 líneas por partido (CORREGIDO):
        Línea 1: Equipo Local
        Línea 2: Cuota Local
        Línea 3: "Empate"
        Línea 4: Cuota Empate
        Línea 5: Equipo Visitante
        Línea 6: Cuota Visitante
        """
        matches = []
        i = 0
        
        while i < len(lines) - 5:
            home = lines[i]
            home_odd = lines[i+1]
            empate_word = lines[i+2]
            empate_odd = lines[i+3]
            away = lines[i+4]
            away_odd = lines[i+5]
            
            # Validar el patrón
            if ('empate' in empate_word.lower()):
                if (re.match(r'^[+-]\d+$', home_odd) and
                    re.match(r'^[+-]\d+$', empate_odd) and
                    re.match(r'^[+-]\d+$', away_odd)):
                    
                    # Limpiar nombres
                    home_clean = re.sub(r'[|•\-_=+*]', '', home).strip()
                    away_clean = re.sub(r'[|•\-_=+*]', '', away).strip()
                    
                    # Verificar que no sean palabras prohibidas
                    if (home_clean.lower() not in self.forbidden_words and 
                        away_clean.lower() not in self.forbidden_words and
                        len(home_clean) > 2 and len(away_clean) > 2):
                        
                        matches.append({
                            'home': home_clean,
                            'away': away_clean,
                            'all_odds': [home_odd, empate_odd, away_odd]
                        })
                        i += 6
                        continue
            i += 1
        
        return matches
    
    def _parse_one_line_format(self, lines):
        """Formato: [Local] [Cuota L] [Empate] [Cuota E] [Visitante] [Cuota V]"""
        matches = []
        pattern = r'^(.+?)\s+([+-]\d{3,4})\s+([Ee]mpat[ea]?)\s+([+-]\d{3,4})\s+(.+?)\s+([+-]\d{3,4})$'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                home = match.group(1).strip()
                local_odd = match.group(2)
                empate_odd = match.group(4)
                away = match.group(5).strip()
                away_odd = match.group(6)
                
                # Limpiar nombres
                home_clean = re.sub(r'[|•\-_=+*]', '', home).strip()
                away_clean = re.sub(r'[|•\-_=+*]', '', away).strip()
                
                if (home_clean.lower() not in self.forbidden_words and 
                    away_clean.lower() not in self.forbidden_words and
                    len(home_clean) > 2 and len(away_clean) > 2):
                    
                    matches.append({
                        'home': home_clean,
                        'away': away_clean,
                        'all_odds': [local_odd, empate_odd, away_odd]
                    })
        return matches
