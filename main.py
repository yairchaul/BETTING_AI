import streamlit as st
import os
import sys
import json
import pandas as pd

# 1. Configuración de rutas
current_dir = os.path.dirname(__file__)
modules_path = os.path.join(current_dir, 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

# 2. Importaciones de módulos
try:
    from vision_reader import analyze_betting_image
    from tracker import guardar_pick_automatico
except ImportError as e:
    st.error(f"Error crítico: {e}")

st.set_page_config(page_title="Ticket Pro IA", page_icon="🏀", layout="wide")

# --- UI SIDEBAR ---
st.sidebar.title("💰 Gestión de Capital")
bankroll = st.sidebar.number_input("Bankroll actual (MXN)", value=1000.0, step=100.0)

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["🔥 Scanner de IA", "📜 Historial de Apuestas"])

with tab1:
    st.title("🏀 Ticket Pro - Vision Terminal")
    # AQUÍ SE DEFINE 'archivo', esto corrige el NameError
    archivo = st.file_uploader("Sube captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

    if archivo:
        st.image(archivo, caption="Captura lista", width=500)
        
        if st.button("🚀 Analizar Mercados"):
            with st.spinner("🤖 IA extrayendo momios..."):
                resultado_raw = analyze_betting_image(archivo)
                
                try:
                    # Limpieza y conversión de JSON
                    json_limpio = resultado_raw.replace('```json', '').replace('```', '').strip()
                    juegos = json.loads(json_limpio)
                    
                    if juegos:
                        st.success(f"✅ Se detectaron {len(juegos)} juegos.")
                        for j in juegos:
                            # Variables seguras (evitan AttributeError)
                            home = j.get('home', 'Local')
                            away = j.get('away', 'Visitante')
                            linea = j.get('handicap', j.get('total', 'N/A'))
                            momio = j.get('moneyline', 'N/A')
                            
                            ev_detectado = 0.052 # Simulación
                            stake_sugerido = bankroll * 0.05
                            
                            with st.expander(f"📌 {away} @ {home}"):
                                col1, col2 = st.columns(2)
                                col1.write(f"**Línea:** {linea} | **Momio:** {momio}")
                                col2.metric("EV Detectado", f"{ev_detectado*100:.1f}%")
                                
                                # Guardado en tracker
                                if guardar_pick_automatico(j, ev_detectado, stake_sugerido):
                                    st.caption("✅ Guardado en historial")
                    else:
                        st.warning("No se encontraron juegos claros.")
                except Exception as e:
                    st.error(f"Error procesando datos: {e}")
                    st.code(resultado_raw)

with tab2:
    st.header("📜 Registro de Picks")
    path_csv = "data/picks.csv"
    if os.path.exists(path_csv):
        df_historial = pd.read_csv(path_csv)
        st.dataframe(df_historial.sort_index(ascending=False), use_container_width=True)
        
        col_down, col_del = st.columns(2)
        csv = df_historial.to_csv(index=False).encode('utf-8')
        col_down.download_button("📥 Descargar CSV", data=csv, file_name="picks_ia.csv")
        if col_del.button("🗑️ Borrar Historial"):
            os.remove(path_csv)
            st.rerun()
    else:
        st.info("El historial aparecerá aquí cuando realices tu primer análisis.")


