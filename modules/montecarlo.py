# modules/montecarlo.py - Simulación Monte Carlo para NBA props
import numpy as np

def simular_total(media_modelo, num_simulaciones=10000, desv_est=10):
    """
    Simula total de puntos (o triples) con Monte Carlo.
    - Usa distribución normal (para totales) o Poisson (para conteos).
    - Devuelve prob de over (supera línea implícita).
    - Para qué sirve: Estima probs reales con incertidumbre.
    """
    # Asume Poisson para conteos (triples/puntos jugador) o normal para totales equipo
    simulaciones = np.random.poisson(media_modelo, num_simulaciones)  # Poisson para discreto
    # Alternativa: normal para continuos
    # simulaciones = np.random.normal(media_modelo, desv_est, num_simulaciones)
    
    # Línea implícita (ajusta si tienes línea real)
    linea = media_modelo - 4  # Tu ajuste inverso
    
    # Prob over
    prob_over = np.mean(simulaciones > linea)
    
    return prob_over
