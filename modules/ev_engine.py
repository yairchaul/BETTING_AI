# modules/ev_engine.py
def calcular_probabilidad_over(equipo_a, equipo_b, linea_over):
    # Aquí es donde integrarás tu base de datos de promedios
    # Por ahora simulamos la lógica: suma de promedios de los últimos 5 juegos
    promedio_a = 115.5  # Esto vendría de tu tracker.py o clv.py
    promedio_b = 118.2
    proyeccion_total = promedio_a + promedio_b
    
    # Si la proyección supera la línea de la casa por mucho, la probabilidad sube
    diferencia = proyeccion_total - linea_over
    
    # Lógica de probabilidad dinámica
    prob = 0.50 + (diferencia * 0.02) 
    return min(max(prob, 0.01), 0.99) # Limitamos entre 1% y 99%
