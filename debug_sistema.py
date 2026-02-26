from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches

def test_objetivo_final():
    print("🚀 Probando integración total...")
    # 1. Simulamos la subida de tu imagen
    partidos_detectados = read_ticket_image("tu_captura.png")
    
    # 2. Verificamos que el motor analice cada uno
    picks = analyze_matches(partidos_detectados)
    
    for p in picks:
        res = p['pick']
        print(f"✅ Partido: {res.match}")
        print(f"   Decisión: {res.selection} | Cuota: {res.odd} | EV: {res.ev}")

if __name__ == "__main__":
    test_objetivo_final()
