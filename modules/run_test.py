import os
from modules.vision_reader import read_ticket_image
from modules.cerebro import obtener_mejor_apuesta

def validar_sistema_completo(nombre_imagen):
    print("🧪 --- INICIANDO AUTOMATIZACIÓN DE PRUEBA ---")
    
    # Mock de un archivo subido para simular Streamlit
    class MockFile:
        def getvalue(self):
            with open(nombre_imagen, "rb") as f: return f.read()
            
    try:
        datos_ocr = read_ticket_image(MockFile())
        print(f"📊 Partidos detectados en imagen: {len(datos_ocr)}")
        
        for i, partido in enumerate(datos_ocr):
            print(f"\n🔍 ANALIZANDO PARTIDO {i+1}: {partido['home']} vs {partido['away']}")
            print(f"   Momios detectados: {partido['all_odds']}")
            
            decision = obtener_mejor_apuesta(partido)
            
            if decision:
                print(f"   ✅ DECISIÓN SHARP ENCONTRADA:")
                print(f"      Mercado: {decision.selection}")
                print(f"      Probabilidad: {round(decision.probability*100, 2)}%")
                print(f"      EV+: {round(decision.ev, 4)}")
            else:
                print("   ❌ Sin ventaja estadística suficiente en este mercado.")
                
    except Exception as e:
        print(f"💥 ERROR EN EL PIPELINE: {str(e)}")

if __name__ == "__main__":
    # Asegúrate de tener una imagen llamada 'test.png' en la raíz
    if os.path.exists("test.png"):
        validar_sistema_completo("test.png")
    else:
        print("📁 Error: Sube una imagen llamada 'test.png' para iniciar.")
