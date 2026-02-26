# modules/cerebro.py
import stats_fetch
import montecarlo
import match_probability
from schemas import PickResult

def procesar_partido_exhaustivo(equipo_h, equipo_a, momios_ocr):
    """
    Analiza CADA uno de los 13 mercados para un partido específico.
    """
    # 1. Obtener data histórica (últimos 5 partidos) de tu API
    stats = stats_fetch.get_team_stats(equipo_h, equipo_a)
    
    # 2. Ejecutar motores de búsqueda y probabilidad
    # Esto usa tu montecarlo.py y match_probability.py
    predicciones = montecarlo.simular_todo(stats) 
    
    posibles_picks = []
    
    # Lista de mercados a evaluar según tu requerimiento
    mercados_objetivo = [
        "Resultado Final", "Ambos Equipos Anotan", "Over 1.5", "Over 2.5", 
        "Over 3.5", "Doble Oportunidad", "1ra Mitad Over/Under"
    ]

    for mercado in mercados_objetivo:
        prob = predicciones.get(mercado)
        # Buscamos el momio real detectado por el OCR para este mercado
        cuota = encontrar_momio_correspondiente(mercado, momios_ocr)
        
        if prob and cuota:
            ev = (prob * cuota) - 1
            if ev > 0: # Solo si hay ventaja estadística real
                posibles_picks.append(PickResult(
                    match=f"{equipo_h} vs {equipo_a}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev
                ))
    
    # Retornamos la "decisión más correcta" (el EV más alto) de este partido
    return max(posibles_picks, key=lambda x: x.ev) if posibles_picks else None
