def extract_teams_by_rows(response):
    """
    Analiza la posición Y (vertical) de cada palabra para agrupar 
    elementos que pertenecen a la misma fila del ticket.
    """
    document = response.full_text_annotation
    lines = []
    
    # Extraemos bloques de texto con su coordenada vertical media
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                # Unimos las palabras del párrafo
                text = "".join([
                    "".join([symbol.text for symbol in word.symbols]) 
                    for word in paragraph.words
                ])
                
                # Obtenemos la altura media del bloque
                vertices = paragraph.bounding_box.vertices
                y_center = sum([v.y for v in vertices]) / 4
                
                lines.append({"text": text, "y": y_center})

    # Ordenamos por posición vertical
    lines.sort(key=lambda x: x['y'])

    # Agrupamos los que tengan una Y similar (margen de 20px)
    rows = []
    if not lines: return []
    
    current_row = [lines[0]["text"]]
    last_y = lines[0]["y"]
    
    for i in range(1, len(lines)):
        if abs(lines[i]["y"] - last_y) < 25: # Umbral de misma fila
            current_row.append(lines[i]["text"])
        else:
            rows.append(current_row)
            current_row = [lines[i]["text"]]
            last_y = lines[i]["y"]
    rows.append(current_row)

    # Filtrado final: Solo filas que parezcan un partido (Local, Empate, Visitante)
    partidos_reales = []
    for row in rows:
        # Limpiamos términos basura
        clean_row = [t for t in row if "Empate" not in t and not any(c.isdigit() for c in t)]
        if len(clean_row) >= 2:
            # El primero suele ser Local y el último Visitante de esa fila
            partidos_reales.append(clean_row[0]) # Local
            partidos_reales.append(clean_row[-1]) # Visitante
            
    return partidos_reales
