import streamlit as st
import pandas as pd
from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches, build_smart_parlay
from modules.tracker import cargar_historial, limpiar_historial_corrupto

# Configuración de página
st.set_page_config(page_title="EV ELITE v4 — Sharp Money Detector", layout="wide")

# --- SIDEBAR: HISTORIAL Y CONTROL ---
with st.sidebar:
    st.title("📊 Panel de Control")
    if st.button("🗑️ Limpiar Historial (CSV)"):
        if limpiar_historial_corrupto():
            st.success("Historial borrado.")
        else:
            st.info("No hay archivo para borrar.")
    
    st.divider()
    st.subheader("📝 Últimos Registros")
    historial = cargar_historial()
    if not historial.empty:
        st.dataframe(historial.tail(10), use_container_width=True)
    else:
        st.write("Sin apuestas registradas.")

# --- CUERPO PRINCIPAL ---
st.title("🧠 EV ELITE v4 — Sharp Money Detector")
st.write("Sube tu ticket de apuestas para analizar valor real con todos los motores.")

uploaded_file = st.file_uploader("Sube tu ticket de apuestas", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    with st.status("Analizando imagen y consultando APIs...", expanded=True) as status:
        # 1. OCR y Detección de partidos
        st.write("Leyendo partidos del ticket...")
        games = read_ticket_image(uploaded_file)
        
        if not games:
            st.error("No se detectaron partidos en la imagen.")
            st.stop()
            
        st.write(f"Partidos detectados: {len(games)}")
        
        # 2. Análisis Multimotor
        st.write("Ejecutando motores de probabilidad y EV...")
        results = analyze_matches(games)
        
        status.update(label="Análisis Completo", state="complete", expanded=False)

    # --- RENDERIZADO DE RESULTADOS ---
    if results:
        st.divider()
        st.subheader("🔥 Picks Sharp Detectados")
        
        for r in results:
            with st.expander(f"📍 {r.match} | Sugerido: {r.selection}", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("Probabilidad", f"{int(r.probability * 100)}%")
                col2.metric("Cuota", f"{r.odd}")
                col3.metric("EV (Value)", f"{r.ev}", delta=f"{round(r.ev * 100, 1)}%")
        
        # --- SECCIÓN DE PARLAY ---
        st.divider()
        parlay = build_smart_parlay(results) 
        
        if parlay:
            st.subheader("🚀 Parlay Sugerido (High EV)")
            
            with st.container(border=True):
                st.warning(f"**Combinada Sugerida:** {' + '.join(parlay.matches)}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Cuota Total", f"{parlay.total_odd}x")
                c2.metric("Prob. Combinada", f"{round(parlay.combined_prob * 100, 2)}%")
                c3.metric("EV Total", f"{parlay.total_ev}")

                st.divider()
                
                col_m, col_b = st.columns([1, 1])
                with col_m:
                    # LÍNEA CORREGIDA:
                    monto_parlay = st.number_input("Monto para invertir ($)", min_value=1.0, value=100.0, step=10.0)
                
                with col_b:
                    st.write(" ")
                    st.write(" ")
                    if st.button("📥 Registrar Parlay en Historial", use_container_width=True):
                        from modules.tracker import registrar_parlay_automatico
                        success = registrar_parlay_automatico(parlay, monto_parlay)
                        if success:
                            st.success("✅ ¡Parlay guardado! Revisa el Sidebar.")
                            st.balloons()
    else:
        st.warning("No se encontraron oportunidades con Valor Esperado (EV+) positivo.")

else:
    st.info("Esperando ticket para procesar...")
