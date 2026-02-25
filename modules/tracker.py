import pandas as pd
import os
from datetime import datetime

PATH_HISTORIAL = "data/parlay_history.csv"

def registrar_parlay_automatico(sim_data, resumen_picks):
    """Guarda el parlay con limpieza de datos y redondeo profesional."""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Unificamos nombres de llaves para evitar errores de 'monto' vs 'monto_invertido'
    monto = sim_data.get('monto_invertido') or sim_data.get('monto', 0)
    
    nuevo_registro = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Picks": resumen_picks,
        "Monto": round(float(monto), 2),
        "Cuota": round(float(sim_data['cuota_total']), 2),
        "Pago_Potencial": round(float(sim_data['pago_total']), 2),
        "Ganancia_Neta": round(float(sim_data['ganancia_neta']), 2),
        "Estado": "Pendiente"
    }
    
    if os.path.exists(PATH_HISTORIAL):
        df = pd.read_csv(PATH_HISTORIAL)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    df.to_csv(PATH_HISTORIAL, index=False, encoding='utf-8')

def calificar_resultados_auto():
    """
    Función maestra para marcar como Ganado/Perdido.
    Actualmente usa una simulación lógica. Para real, conectaría aquí con la API.
    """
    if not os.path.exists(PATH_HISTORIAL):
        return
    
    df = pd.read_csv(PATH_HISTORIAL)
    
    if "Estado" in df.columns:
        # Solo procesamos los que siguen 'Pendiente'
        pendientes = df[df['Estado'] == 'Pendiente'].index
        
        for idx in pendientes:
            # --- LÓGICA DE AUDITORÍA REAL ---
            # Aquí se compararía contra el marcador final. 
            # Como ejemplo, si la cuota era muy alta (>100), simulamos riesgo.
            if df.at[idx, 'Cuota'] > 50:
                # Simulación de auditoría para pruebas
                pass 
            
    df.to_csv(PATH_HISTORIAL, index=False)
