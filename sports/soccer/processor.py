from evento import Evento

class SoccerProcessor:
    def process(self, raw_lines):
        """Procesa líneas y devuelve lista de Eventos"""
        eventos = []
        
        # Aplanar líneas en una lista de palabras
        flat_words = []
        for line in raw_lines:
            if isinstance(line, list):
                flat_words.extend(line)
            elif isinstance(line, str):
                flat_words.append(line)
        
        # Buscar patrones de fútbol (equipo + odds + Empate + odds + equipo + odds)
        i = 0
        while i < len(flat_words) - 5:
            # Buscar "Empate" para identificar el formato
            for j in range(i, min(i+10, len(flat_words))):
                if flat_words[j] == "Empate":
                    empate_idx = j
                    if i + 5 < len(flat_words):
                        # Extraer datos
                        home = " ".join(flat_words[i:empate_idx-1])
                        home_odd = flat_words[empate_idx-1]
                        draw_odd = flat_words[empate_idx+1]
                        away = " ".join(flat_words[empate_idx+2:empate_idx+5])
                        away_odd = flat_words[empate_idx+4]
                        
                        # Crear evento
                        evento = Evento(
                            local=home.strip(),
                            visitante=away.strip(),
                            deporte='FUTBOL',
                            datos_crudos={
                                'home_odd': home_odd,
                                'draw_odd': draw_odd,
                                'away_odd': away_odd
                            }
                        )
                        evento.odds = {
                            'local': home_odd,
                            'draw': draw_odd,
                            'visitante': away_odd
                        }
                        eventos.append(evento)
                        i = empate_idx + 5
                        break
            i += 1
        
        return eventos
