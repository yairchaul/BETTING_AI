import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def verificar_lesiones(equipo):

    model = genai.GenerativeModel("gemini-pro")

    prompt = f"Lista jugadores lesionados hoy del equipo NBA {equipo}"

    try:
        r = model.generate_content(prompt)
        return r.text
    except:
        return "No disponible"