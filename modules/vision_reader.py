def analyze_betting_image(uploaded_file):
    # ... (parte inicial de Google Vision igual hasta obtener word_list) ...
    
    # 1. Agrupar por filas (Y similares)
    word_list.sort(key=lambda w: w["y"])
    rows = []
    if word_list:
        current_row = [word_list[0]]
        for i in range(1, len(word_list)):
            if abs(word_list[i]["y"] - current_row[-1]["y"]) < 40:
                current_row.append(word_list[i])
            else:
                rows.append(current_row)
                current_row = [word_list[i]]
        rows.append(current_row)

    data_final = []
    for row in rows:
        # Ordenar elementos de la fila de izquierda a derecha
        row.sort(key=lambda w: w["x"])
        
        # Separar Momios de Nombres usando RE y posición X
        # Los momios suelen estar a la derecha (X > 500 aprox en una imagen estándar)
        odds = [w["text"] for w in row if re.match(r'^[+-]\d{3}$', w["text"])]
        
        if len(odds) >= 3:
            # Filtrar nombres: Quitamos momios, fechas (Feb), horas (03:00) y el "+43"
            clean_names = []
            for w in row:
                t = w["text"]
                is_trash = (
                    re.match(r'^[+-]\d+$', t) or  # Momios o +43
                    re.match(r'\d{2}:\d{2}', t) or # Horas
                    t.lower() in ["feb", "mar", "apr", "jan"] or # Meses
                    re.match(r'^\d{1,2}$', t) # Números sueltos (días)
                )
                if not is_trash:
                    clean_names.append(t)
            
            # Dividir nombres: El primer bloque es LOCAL, el segundo VISITANTE
            # Como suelen estar uno sobre otro, el orden en 'clean_names' es correcto
            if len(clean_names) >= 2:
                mid = len(clean_names) // 2
                home = " ".join(clean_names[:mid])
                away = " ".join(clean_names[mid:])
                
                data_final.append({
                    "Local": home,
                    "Visitante": away,
                    "1": odds[0],
                    "X": odds[1],
                    "2": odds[2]
                })

    return data_final
