class Evento:
    """
    Clase universal para estandarizar todos los eventos deportivos.
    El diccionario 'mercados' es flexible y se adapta a cada deporte.
    """
    def __init__(self, local, visitante, deporte, datos_crudos=None):
        self.local = local
        self.visitante = visitante
        self.deporte = deporte
        self.datos_crudos = datos_crudos
        self.stats = {}      # Estadísticas base (GF, GA, PPG, etc.)
        self.mercados = {}    # Probabilidades calculadas (dinámicas por deporte)
        self.odds = {}         # Cuotas originales

    def __repr__(self):
        return f"Evento({self.local} vs {self.visitante} [{self.deporte}])"
