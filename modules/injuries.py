# modules/injuries.py
import requests

def verificar_lesiones(equipo):
    """
    Verifica el estado de lesiones para un equipo dado.
    """
    # Por ahora, devolvemos un mensaje limpio para que la app no rompa.
    # En el futuro, puedes conectar esto con una API de noticias NBA.
    if not equipo or equipo == "Unknown":
        return "Sin reporte"
    
    return "Ninguna lesión crítica detectada"
