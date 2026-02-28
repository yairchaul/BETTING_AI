import re
import streamlit as st

def procesar_texto_manual(texto):
    """Convierte 'Equipo A vs Equipo B' en un formato que el cerebro entienda."""
    partidos = []
    lineas = texto.split('\n')
    for linea in lineas:
        if " vs " in linea.lower():
            equipos = re.split(r'\s+vs\s+', linea, flags=re.IGNORECASE)
            if len(equipos) == 2:
                partidos.append({
                    "home": equipos[0].strip(),
                    "away": equipos[1].strip(),
                    "odds": ["+100", "+200", "+100"]  # Momios base si es manual
                })
    return partidos

# Mantén tu función read_ticket_image igual para que siga intentando leer imágenes
