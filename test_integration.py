from modules.vision_reader import read_ticket_image
from modules.cerebro import get_best_option_per_match

def test_full_pipeline(image_path):
    print("--- INICIANDO TEST DE INTEGRACIÓN ---")
    # Prueba OCR
    raw_data = read_ticket_image(image_path)
    print(f"OCR detectó {len(raw_data)} partidos.")
    
    for game in raw_data:
        print(f"\nAnalizando: {game['home']} vs {game['away']}")
        # Prueba Cerebro + APIs + Montecarlo
        pick = get_best_option_per_match(game['home'], game['away'], game['detected_odds'])
        if pick:
            print(f"ÉXITO: Mejor opción hallada -> {pick['selection']} (Prob: {pick['prob']})")
        else:
            print("FALLA: El motor no encontró una opción EV+ para este partido.")

if __name__ == "__main__":
    test_full_pipeline("tu_imagen_de_prueba.png")
