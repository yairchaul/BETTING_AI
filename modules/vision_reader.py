import os
from google.cloud import vision
import io

# Asegúrate de tener tu archivo JSON de credenciales en la carpeta raíz
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets.json"

def analyze_betting_image(uploaded_file):
    client = vision.ImageAnnotatorClient()
    content = uploaded_file.getvalue()
    image = vision.Image(content=content)
    
    # OCR de alta precisión de Google Cloud
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts:
        return {"juegos": []}

    full_text = texts[0].description
    lineas = full_text.split('\n')
    
    juegos_detectados = []
    # Lógica para agrupar líneas en pares de equipos (Local vs Visitante)
    for i in range(0, len(lineas) - 1, 2):
        if len(lineas[i]) > 3: # Filtro básico de ruido
            juegos_detectados.append({
                "home": lineas[i].strip(),
                "away": lineas[i+1].strip() if i+1 < len(lineas) else "Visitante"
            })
            
    return {"juegos": juegos_detectados[:5]} # Limitamos a los primeros 5 para el Parlay
