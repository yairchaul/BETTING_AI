from evento import Evento

class SoccerProcessor:
    def process(self, raw_lines):
        """Procesa líneas y devuelve lista de Eventos"""
        eventos = []
        for line in raw_lines:
            # Buscar "Empate" para identificar el formato
            empate_index = -1
            for i, word in enumerate(line):
                if word == "Empate":
                    empate_index = i
                    break
            
            if empate_index > 0 and len(line) >= empate_index + 3:
                home = " ".join(line[:empate_index-1])
                home_odd = line[empate_index-1]
                away = " ".join(line[empate_index+2:-1])
                away_odd = line[-1]
                draw_odd = line[empate_index+1]
                
                # Crear evento en lugar de diccionario simple
                evento = Evento(
                    local=home,
                    visitante=away,
                    deporte='FUTBOL',
                    datos_crudos={'home_odd': home_odd, 'draw_odd': draw_odd, 'away_odd': away_odd}
                )
                # Guardar odds originales
                evento.odds = {
                    'local': home_odd,
                    'draw': draw_odd,
                    'visitante': away_odd
                }
                eventos.append(evento)
        return eventos
