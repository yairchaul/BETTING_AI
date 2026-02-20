# injuries.py
def verificar_disponibilidad(nombre_jugador):
    """
    Simula una consulta a un reporte de lesiones (NBA Injury Report).
    """
    lesionados = ["Joel Embiid", "Ja Morant", "Julius Randle"]
    
    if nombre_jugador in lesionados:
        return False # El jugador no debe aparecer en el ticket
    return True
