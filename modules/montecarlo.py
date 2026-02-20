import numpy as np

def simular_total(media, std=12, sims=5000):

    resultados = np.random.normal(media, std, sims)

    return resultados