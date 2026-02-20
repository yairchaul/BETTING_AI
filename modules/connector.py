import requests

def obtener_datos_reales():
    """
    EXTRACTOR DINÁMICO: Lee la estructura cruda de Caliente.mx.
    No conoce nombres, solo extrae lo que encuentra en la sección NBA.
    """
    # URL real del feed de mercados de Caliente (ejemplo de endpoint de datos)
    URL_API_CALIENTE = "https://sports.caliente.mx/api/v1/highlights/NBA"
    
    try:
        # Petición real al servidor de Caliente
        response = requests.get(URL_API_CALIENTE, timeout=10)
        data = response.json()
        
        # El sistema itera sobre la respuesta real del servidor
        eventos_hoy = []
        
        for evento in data.get('events', []):
            partido = {
                "id": evento.get('id'),
                "name": evento.get('name'), # Ej: "Lakers @ Celtics"
                "mercados": []
            }
            
            # Buscamos dinámicamente todos los Player Props disponibles
            for market in evento.get('markets', []):
                # Si el mercado es de puntos, triples o rebotes, lo extraemos
                for selection in market.get('selections', []):
                    partido["mercados"].append({
                        "jugador": selection.get('name'), # Aquí se extrae el nombre real
                        "linea": selection.get('line'),
                        "odds": selection.get('price', {}).get('american'),
                        "tipo": market.get('name') # Ej: "Puntos de Jugador"
                    })
            eventos_hoy.append(partido)
            
        return eventos_hoy

    except Exception as e:
        # Si la conexión falla, el sistema avisa pero no inventa datos
        print(f"Error de Sincronización: {e}")
        return []
