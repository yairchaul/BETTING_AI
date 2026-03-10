class Evento:
    """
    Clase universal para estandarizar todos los eventos deportivos.
    Independientemente del deporte, todos los eventos tendrán esta estructura.
    """
    def __init__(self, local, visitante, deporte, datos_crudos=None):
        self.local = local                # Nombre del equipo/peleador local
        self.visitante = visitante        # Nombre del equipo/peleador visitante
        self.deporte = deporte             # 'FUTBOL', 'NBA', 'UFC'
        self.datos_crudos = datos_crudos   # Datos originales de la captura
        self.stats = {}                    # Estadísticas base (GF, GA, etc.)
        self.mercados = {}                  # Probabilidades calculadas
        self.odds = {}                      # Cuotas originales
        
    def __repr__(self):
        return f"Evento({self.local} vs {self.visitante} - {self.deporte})"
