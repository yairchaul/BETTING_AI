
import numpy as np

def simular_total(media_modelo, simulaciones=10000):
    """
    Simulación Monte Carlo para determinar la probabilidad de 'Over'.
    """
    if media_modelo <= 0:
        return 0.5
    
    # Genera una distribución basada en la media proyectada
    resultados = np.random.poisson(media_modelo, simulaciones)
    probabilidad_over = np.mean(resultados > (media_modelo - 4)) # Compara con la línea real
    return float(probabilidad_over)
