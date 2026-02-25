import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Betting AI Auditor - Pro", layout="wide")
engine = EVEngine(threshold=0.85)
PATH_HISTORIAL = "data/historial_parlays.csv"

# --- ESTILOS PERSONALIZADOS (Peticiones Visuales) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .card-aprobada {
        background-color: #1a2c3d;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2ecc71;
        margin-bottom: 20px;
    }
    .card-descartada {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #e74c3c;
        margin-bottom: 10px;
        color: #888;
    }
    .metric-box {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Auditoría Betting AI: Filtro de Élite 85%")

# --- SIDEBAR: HISTORIAL Y CONTROL ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    umbral = st.slider("Umbral de Seguridad (%)", 70, 95, 85)
    engine.threshold = umbral / 100
    
    st.divider()
    if st.button("Limpiar Historial (Cuidado)"):
        if os.path.exists(PATH_HISTORIAL):
            os.remove(PATH_HISTORIAL)
            st.rerun()

# --- CARGA DE IMAGEN ---
archivo = st.file_uploader("Subir captura de ticket para análisis global", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Analizando imagen con Vision AI..."):
        # Llamada al vision_reader real que procesa la imagen
        matches, msg = analyze_betting_image(archivo)
    
    st.success(msg)

    if matches:
        st.subheader("🎯 Resultados de la Cascada (Filtro 85%)")
        
        for m in matches:
            res = engine.get_raw_probabilities(m)
            
            if res['status'] == "APROBADO":
                st.markdown(f"""
                <div class="card-aprobada">
                    <h3 style="margin:0; color:white;">{res['home']} vs {res['away']}</h3>
                    <p style="color:#2ecc71; font-size:1.4rem; margin:10px 0;"><b>Pick Sugerido: {res['pick_final']}</b></p>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px; color:#BDC3C7;">
                        <div>Probabilidad Poisson: <b>{res['prob_final']}%</b></div>
                        <div>Momio Estimado: <b>{res['cuota_ref']}</b></div>
                        <div>EV: <b>{res['ev']}</b> | Edge: <b>+{res['edge']}%</b></div>
                        <div>Técnico: λL: {res['lh']} | λV: {res['lv']} | Exp: {res['exp']}</div>
                    </div>
                    <p style="margin-top:10px; color:#2ecc71; font-weight:bold;">Confianza: 🔥 EXCELENTE (supera {umbral}%)</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón para guardar en historial (Simulado para este ejemplo)
                if st.button(f"Registrar Pick: {res['home']}", key=f"btn_{res['home']}"):
                    nueva_fila = pd.DataFrame([{
                        "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                        "Partido": f"{res['home']} vs {res['away']}",
                        "Pick": res['pick_final'],
                        "Probabilidad": f"{res['prob_final']}%",
                        "Cuota": round(res['cuota_ref'], 2),
                        "Edge": f"{res['edge']}%"
                    }])
                    nueva_fila.to_csv(PATH_HISTORIAL, mode='a', header=not os.path.exists(PATH_HISTORIAL), index=False)
                    st.toast("✅ Apuesta guardada en el historial")

            else:
                st.markdown(f"""
                <div class="card-descartada">
                    Partido: {res['home']} vs {res['away']} → <b>Descartado</b> (No supera el {umbral}%)
                </div>
                """, unsafe_allow_html=True)

# --- VISUALIZACIÓN DEL HISTORIAL (Petición de redondeo y limpieza) ---
st.divider()
st.subheader("🏁 Historial de Apuestas Guardadas")

if os.path.exists(PATH_HISTORIAL):
    df_historial = pd.read_csv(PATH_HISTORIAL)
    
    # Aplicamos redondeo y limpieza visual para evitar los ceros basura (.000000)
    # Mostramos los datos financieros estrictamente a 2 decimales
    st.dataframe(
        df_historial.style.format({
            "Cuota": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Resumen rápido del historial
    total_guardado = len(df_historial)
    st.info(f"Tienes {total_guardado} apuestas registradas en tu historial.")
else:
    st.info("Aún no hay apuestas en el historial. Analiza una imagen y registra un pick.")
