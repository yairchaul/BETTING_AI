# learning.py
def calcular_probabilidad_real(nombre_jugador, linea_actual, tipo_mercado):
    """
    Compara la línea de Caliente con el promedio histórico del jugador.
    """
    # Base de datos simplificada (en producción esto carga un .csv o SQL)
    historico = {
        "Zion Williamson": {"promedio_puntos": 24.8, "over_rate": 0.65},
        "Saddiq Bey": {"promedio_puntos": 13.5, "over_rate": 0.55}
    }
    
    stats = historico.get(nombre_jugador, {"promedio_puntos": 0, "over_rate": 0.50})
    
    # Si la línea de Caliente es menor a su promedio, sube la probabilidad
    if linea_actual < stats["promedio_puntos"]:
        return stats["over_rate"] + 0.15
    return stats["over_rate"]
