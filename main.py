import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración de Estilo "Valor IA"
st.set_page_config(page_title="Auditor de Valor 85%", layout="wide")
engine = EVEngine(threshold=0.85)

# Ruta del historial (Basada en tu tracker.py)
PATH_HISTORIAL = "data/historial_apuestas.csv" 

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .card-blue {
        background: #1a2c3d;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Auditoría Betting AI: Filtro 85%")

# Sección de Carga
archivo = st.file_uploader("Subir imagen de momios", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Procesando imagen real..."):
        matches, msg = analyze_betting_image(archivo)
    
    st.sidebar.info(msg)

    if matches:
        for m in matches:
            res = engine.get_raw_probabilities(m)
            if res['status'] == "APROBADO":
                st.markdown(f"""
                <div class="card-blue">
                    <h3>{res['home']} vs {res['away']}</h3>
                    <p style="color:#2ecc71; font-size:1.2rem;"><b>Pick: {res['pick_final']}</b></p>
                    <p>Probabilidad: {res['prob_final']}% | Cuota: {res['cuota_ref']} | EV: {res['ev']}</p>
                    <small style="color:#888;">λL: {res['lh']} | λV: {res['lv']} | Exp: {res['exp']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write(f"🚫 {res['home']} vs {res['away']} → Descartado (Debajo del 85%)")

# --- RECUPERACIÓN DEL HISTORIAL (Tus apuestas guardadas) ---
st.divider()
st.subheader("🏁 Historial de Apuestas Registradas")

if os.path.exists(PATH_HISTORIAL):
    df = pd.read_csv(PATH_HISTORIAL)
    
    # Limpieza de "Basura Decimal" y Estética
    if not df.empty:
        # Forzamos redondeo a 2 decimales para que se vea profesional
        st.dataframe(
            df.style.format(subset=["Cuota"], formatter="{:.2f}"),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("El archivo existe pero está vacío.")
else:
    # Si el archivo no aparece, intentamos buscarlo en carpetas alternativas
    st.warning("No se detectó el archivo en 'data/'. Por favor, verifica si tu 'tracker.py' usa otra ruta.")

