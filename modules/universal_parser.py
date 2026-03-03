# modules/universal_parser.py
import re
import streamlit as st

class UniversalParser:
    """
    Parser universal que detecta automáticamente TODOS los formatos de imagen
    y extrae los partidos correctamente.
    """
    
    def __init__(self):
        self.forbidden_words = ['empate', 'empaté', 'draw', 'vs', 'v', 'local', 'visitante', 'cuota', 'odds']
    
    def parse(self, text):
        """Método principal: detecta TODOS los formatos y parsea"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # DEBUG: Mostrar líneas detectadas (opcional)
        # st.write("📄 Líneas detectadas por OCR:", lines)
        
        matches = []
        
        # ============================================================================
        # ESTRATEGIA 1: Formato de lista vertical (nuevo)
        # ============================================================================
        vertical_matches = self._parse_vertical_list(lines)
        matches.extend(vertical_matches)
        
        # ============================================================================
        # ESTRATEGIA 2: Formato de 9 líneas
        # ============================================================================
        nine_line_matches = self._parse_nine_line_format(lines)
        matches.extend(nine_line_matches)
        
        # ============================================================================
        # ESTRATEGIA 3: Formato flexible de 8-10 líneas
        # ============================================================================
        flexible_matches = self._parse_flexible_format(lines)
        matches.extend(flexible_matches)
        
        # ============================================================================
        # ESTRATEGIA 4: Formato de bloques humanos
        # ============================================================================
        human_matches = self._parse_human_style(lines)
        matches.extend(human_matches)
        
        # ============================================================================
        # ESTRATEGIA 5: Formato de 6 líneas
        # ============================================================================
        six_line_matches = self._parse_six_line_format(lines)
        matches.extend(six_line_matches)
        
        # ============================================================================
        # ESTRATEGIA 6: Formato de 1 línea (6 columnas)
        # ============================================================================
        one_line_matches = self._parse_one_line_format(lines)
        matches.extend(one_line_matches)
        
        # ============================================================================
        # ESTRATEGIA 7: Formato de 2 líneas
        # ============================================================================
        two_line_matches = self._parse_two_line_format(lines)
        matches.extend(two_line_matches)
        
        # Eliminar duplicados (mismo partido detectado por diferentes estrategias)
        unique_matches = []
        seen = set()
        for match in matches:
            key = (match.get('home', ''), match.get('away', ''))
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches
    
    def _detect_vertical_list(self, lines):
        """
        Detecta si el texto es una lista vertical de equipos
        """
        if len(lines) < 10:
            return False
        
        team_lines = 0
        for line in lines[:20]:
            if re.search(r'[A-Za-z]', line) and len(line) > 3:
                team_lines += 1
        
        return team_lines > len(lines[:20]) * 0.7
    
    def _parse_vertical_list(self, lines):
        """
        Parsea formato de lista vertical:
        [Equipo 1]
        [+XXX] (opcional)
        [Equipo 2]
        [+XXX] (opcional)
        ...
        """
        matches = []
        
        # Extraer todas las odds
        all_odds = []
        for line in lines:
            odds_in_line = re.findall(r'[+-]\d{3,4}', line)
            all_odds.extend(odds_in_line)
        
        # Extraer nombres de equipos (líneas sin odds)
        team_names = []
        for line in lines:
            if not re.search(r'[+-]\d{3,4}', line) and re.search(r'[A-Za-z]', line):
                clean_name = re.sub(r'[|•\-_=+*]', '', line).strip()
                if len(clean_name) > 3 and clean_name.lower() not in self.forbidden_words:
                    team_names.append(clean_name)
        
        # Crear partidos con los primeros N equipos
        if len(team_names) >= 2:
            for i in range(0, len(team_names) - 1, 2):
                if i + 1 < len(team_names):
                    idx_odds = i
                    if idx_odds + 2 < len(all_odds):
                        matches.append({
                            'home': team_names[i],
                            'away': team_names[i + 1],
                            'all_odds': [
                                all_odds[idx_odds],
                                all_odds[idx_odds + 1],
                                all_odds[idx_odds + 2] if idx_odds + 2 < len(all_odds) else 'N/A'
                            ]
                        })
        
        return matches
    
    def _parse_nine_line_format(self, lines):
        """
        Formato específico de 9 líneas:
        1: +XX (metadata)
        2: Equipo Local
        3: Equipo Visitante
        4: Fecha
        5: 1
        6: 2
        7: Cuota Local
        8: Cuota Empate
        9: Cuota Visitante
        """
        matches = []
        i = 0
        
        while i < len(lines):
            if i + 8 < len(lines):
                if re.match(r'^[+-]\d+$', lines[i]):
                    if lines[i+4] == '1' and lines[i+5] == '2':
                        if (re.match(r'^[+-]\d+$', lines[i+6]) and
                            re.match(r'^[+-]\d+$', lines[i+7]) and
                            re.match(r'^[+-]\d+$', lines[i+8])):
                            
                            local_clean = re.sub(r'\s*\([^)]*\)', '', lines[i+1]).strip()
                            visitante_clean = re.sub(r'\s*\([^)]*\)', '', lines[i+2]).strip()
                            
                            matches.append({
                                'home': local_clean,
                                'away': visitante_clean,
                                'all_odds': [lines[i+6], lines[i+7], lines[i+8]],
                                'fecha': lines[i+3],
                                'metadata': lines[i]
                            })
                            i += 9
                            continue
            i += 1
        
        return matches
    
    def _parse_flexible_format(self, lines):
        """
        Formato flexible que acepta variaciones con X opcional
        """
        matches = []
        i = 0
        
        while i < len(lines):
            if i + 7 < len(lines):
                if re.match(r'^[+-]\d+$', lines[i]):
                    potencial_local = lines[i+1]
                    potencial_visitante = lines[i+2]
                    potencial_fecha = lines[i+3]
                    
                    offset = 4
                    
                    if i+offset < len(lines) and lines[i+offset] == '1':
                        offset += 1
                        
                        if i+offset < len(lines) and lines[i+offset] == 'X':
                            offset += 1
                        
                        if i+offset < len(lines) and lines[i+offset] == '2':
                            offset += 1
                            
                            if i+offset+2 < len(lines):
                                cuota_local = lines[i+offset]
                                cuota_empate = lines[i+offset+1]
                                cuota_visitante = lines[i+offset+2]
                                
                                if re.match(r'^[+-]\d+$', cuota_local) and re.match(r'^[+-]\d+$', cuota_visitante):
                                    if not re.match(r'^[+-]\d+$', cuota_empate):
                                        cuota_empate = 'N/A'
                                    
                                    local_clean = re.sub(r'\s*\([^)]*\)', '', potencial_local).strip()
                                    visitante_clean = re.sub(r'\s*\([^)]*\)', '', potencial_visitante).strip()
                                    
                                    matches.append({
                                        'home': local_clean,
                                        'away': visitante_clean,
                                        'all_odds': [cuota_local, cuota_empate, cuota_visitante],
                                        'fecha': potencial_fecha
                                    })
                                    i += offset + 3
                                    continue
            i += 1
        
        return matches
    
    def _parse_human_style(self, lines):
        """Formato de bloques con estructura flexible"""
        matches = []
        i = 0
        
        while i < len(lines):
            if re.match(r'^[+-]\d+$', lines[i]):
                if i + 3 < len(lines):
                    local = lines[i+1]
                    visitante = lines[i+2]
                    fecha = lines[i+3]
                    
                    odds = []
                    j = i + 4
                    cuotas_encontradas = 0
                    
                    while j < len(lines) and cuotas_encontradas < 3:
                        linea = lines[j]
                        
                        match_1 = re.match(r'^(\d)\s+([+-]\d+)$', linea)
                        if match_1:
                            odds.append(match_1.group(2))
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        match_2 = re.match(r'^[+-]\d+$', linea)
                        if match_2:
                            odds.append(linea)
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        if linea in ['A', 'X']:
                            odds.append('N/A')
                            cuotas_encontradas += 1
                            j += 1
                            continue
                        
                        break
                    
                    if len(odds) >= 2:
                        while len(odds) < 3:
                            odds.append('N/A')
                        
                        local_clean = re.sub(r'\s*\([^)]*\)', '', local).strip()
                        visitante_clean = re.sub(r'\s*\([^)]*\)', '', visitante).strip()
                        
                        liga = "Desconocida"
                        if i > 0 and len(lines[i-1]) > 5:
                            liga = lines[i-1]
                        
                        matches.append({
                            'home': local_clean,
                            'away': visitante_clean,
                            'all_odds': odds[:3],
                            'liga': liga,
                            'fecha': fecha
                        })
                        i = j
                        continue
            i += 1
        
        return matches
    
    def _parse_six_line_format(self, lines):
        """Formato de 6 líneas por partido"""
        matches = []
        i = 0
        while i < len(lines) - 5:
            home = lines[i]
            home_odd = lines[i+1]
            empate_word = lines[i+2]
            empate_odd = lines[i+3]
            away = lines[i+4]
            away_odd = lines[i+5]
            
            if ('empate' in empate_word.lower()):
                if (re.match(r'^[+-]\d+$', home_odd) and
                    re.match(r'^[+-]\d+$', empate_odd) and
                    re.match(r'^[+-]\d+$', away_odd)):
                    
                    if self._is_valid_team(home) and self._is_valid_team(away):
                        matches.append({
                            'home': home,
                            'away': away,
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
                
                if self._is_valid_team(home) and self._is_valid_team(away):
                    matches.append({
                        'home': home,
                        'away': away,
                        'all_odds': [local_odd, empate_odd, away_odd]
                    })
        return matches
    
    def _parse_two_line_format(self, lines):
        """Formato: 2 líneas por partido"""
        matches = []
        i = 0
        while i < len(lines) - 1:
            line1 = lines[i]
            line2 = lines[i+1]
            
            odds_line1 = re.findall(r'[+-]\d{3,4}', line1)
            
            if len(odds_line1) >= 2 and not re.search(r'[+-]\d{3,4}', line2):
                local_part = line1.split(odds_line1[0])[0].strip()
                home = re.sub(r'Empate.*', '', local_part).strip()
                away = line2.strip()
                
                if self._is_valid_team(home) and self._is_valid_team(away):
                    away_odd = odds_line1[2] if len(odds_line1) > 2 else 'N/A'
                    matches.append({
                        'home': home,
                        'away': away,
                        'all_odds': [odds_line1[0], odds_line1[1], away_odd]
                    })
                i += 2
            else:
                i += 1
        return matches
    
    def _is_valid_team(self, name):
        """Valida que un nombre sea un equipo válido"""
        if not name or len(name) < 2:
            return False
        if name.lower() in self.forbidden_words:
            return False
        if re.match(r'^[+-]?\d+$', name):
            return False
        return True
