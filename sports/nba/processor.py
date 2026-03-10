import re
from evento import Evento

class NBAProcessor:
    def _limpiar_nombre(self, texto):
        """Limpia nombres de equipos de basura OCR"""
        if not texto:
            return ""
        # Eliminar cuotas, números y palabras sueltas
        texto = re.sub(r'[+-]\d+', '', texto)
        texto = re.sub(r'\b(FC|vs|VS|to|is|t|s|a|los|las|de)\b', '', texto, flags=re.IGNORECASE)
        return texto.strip()

    def process(self, raw_lines):
        """
        Procesa líneas de NBA y devuelve lista de Eventos.
        Estructura esperada (por equipo):
        - Equipo
        - Spread (ej: +3)
        - Cuota Spread (ej: -110)
        - O/U (O o U)
        - Total (ej: 227.5)
        - Cuota Total (ej: -110)
        - Moneyline (ej: +125)
        """
        eventos = []
        
        # Aplanar líneas en una lista de palabras
        flat_words = []
        for line in raw_lines:
            if isinstance(line, list):
                flat_words.extend(line)
            elif isinstance(line, str):
                # Dividir por espacios y limpiar
                words = line.split()
                flat_words.extend([w.strip() for w in words if w.strip()])
        
        # Debug: mostrar palabras detectadas
        # st.write("Palabras NBA:", flat_words)
        
        # Buscar patrones: cada equipo tiene 7 campos
        i = 0
        while i < len(flat_words) - 13:
            try:
                # Equipo local (puede tener varias palabras)
                home_words = []
                while i < len(flat_words) and not re.match(r'^[+-]', flat_words[i]):
                    home_words.append(flat_words[i])
                    i += 1
                
                if i + 6 < len(flat_words):
                    home = self._limpiar_nombre(' '.join(home_words))
                    home_spread = flat_words[i]
                    home_spread_odds = flat_words[i+1]
                    home_ou = flat_words[i+2]
                    home_total = flat_words[i+3]
                    home_total_odds = flat_words[i+4]
                    home_ml = flat_words[i+5]
                    i += 6
                    
                    # Equipo visitante
                    away_words = []
                    while i < len(flat_words) and not re.match(r'^[+-]', flat_words[i]):
                        away_words.append(flat_words[i])
                        i += 1
                    
                    if i + 5 < len(flat_words):
                        away = self._limpiar_nombre(' '.join(away_words))
                        away_spread = flat_words[i]
                        away_spread_odds = flat_words[i+1]
                        away_ou = flat_words[i+2]
                        away_total = flat_words[i+3]
                        away_total_odds = flat_words[i+4]
                        away_ml = flat_words[i+5]
                        i += 6
                        
                        # Crear evento NBA
                        evento = Evento(
                            local=home,
                            visitante=away,
                            deporte='NBA',
                            datos_crudos={
                                'home_spread': home_spread,
                                'home_spread_odds': home_spread_odds,
                                'home_ou': home_ou,
                                'home_total': home_total,
                                'home_total_odds': home_total_odds,
                                'home_ml': home_ml,
                                'away_spread': away_spread,
                                'away_spread_odds': away_spread_odds,
                                'away_ou': away_ou,
                                'away_total': away_total,
                                'away_total_odds': away_total_odds,
                                'away_ml': away_ml
                            }
                        )
                        # Guardar odds en formato estructurado
                        evento.odds = {
                            'home_ml': home_ml,
                            'home_spread': f"{home_spread} ({home_spread_odds})",
                            'home_total': f"{home_ou} {home_total} ({home_total_odds})",
                            'away_ml': away_ml,
                            'away_spread': f"{away_spread} ({away_spread_odds})",
                            'away_total': f"{away_ou} {away_total} ({away_total_odds})"
                        }
                        eventos.append(evento)
            except Exception as e:
                i += 1
                continue
        
        return eventos
