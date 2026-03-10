from evento import Evento

class UFCProcessor:
    def process(self, raw_lines):
        """Procesa líneas y devuelve lista de Eventos de UFC"""
        eventos = []
        
        # Aplanar líneas
        flat_words = []
        for line in raw_lines:
            if isinstance(line, list):
                flat_words.extend(line)
            elif isinstance(line, str):
                flat_words.append(line)
        
        # Las peleas vienen en pares de peleadores
        i = 0
        while i < len(flat_words) - 3:
            try:
                # Peleador 1
                f1_words = []
                while i < len(flat_words) and not flat_words[i][0] in '+-':
                    f1_words.append(flat_words[i])
                    i += 1
                
                if i < len(flat_words):
                    f1 = ' '.join(f1_words).strip()
                    f1_odds = flat_words[i]
                    i += 1
                    
                    # Peleador 2
                    f2_words = []
                    while i < len(flat_words) and not flat_words[i][0] in '+-':
                        f2_words.append(flat_words[i])
                        i += 1
                    
                    if i < len(flat_words):
                        f2 = ' '.join(f2_words).strip()
                        f2_odds = flat_words[i]
                        i += 1
                        
                        # Crear evento UFC
                        evento = Evento(
                            local=f1,
                            visitante=f2,
                            deporte='UFC',
                            datos_crudos={
                                'f1_odds': f1_odds,
                                'f2_odds': f2_odds
                            }
                        )
                        evento.odds = {
                            'local': f1_odds,
                            'visitante': f2_odds
                        }
                        eventos.append(evento)
            except:
                i += 1
        
        return eventos
