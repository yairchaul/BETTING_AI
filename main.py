import streamlit as st
import os
from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches, build_smart_parlay

# 1. Configuración inicial de la App
st.set_page_config(page_title="BETTING AI EV+", layout="wide")

# 2. Sidebar para estado del sistema y diagnóstico
with st.sidebar:
    st.header("⚙️ Sistema")
    if os.path.exists("modules/__init__.py"):
        st.success("Paquete modules: OK")
    else:
        st.warning("Falta modules/__init__.py")
    
    st.divider()
    st.info("El sistema está configurado para buscar el máximo EV+ analizando mercados de Resultado, Goles y Ambos Anotan.")

# 3. Interfaz Principal
st.title("🧠 BETTING AI — Sharp Money Detector")

uploaded = st.file_uploader("Sube imagen del ticket", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.spinner("Analizando y procesando últimos 5 partidos..."):
        # --- PASO 1: OCR ---
        # Extrae los nombres de equipos y cuotas de la imagen
        games = read_ticket_image(uploaded)
        
        if not games:
            st.error("No se detectaron partidos en el ticket.")
        else:
            # --- PASO 2: MOTOR DE EV ---
            # Realiza la simulación de Poisson y elige la mejor opción por partido
            results = analyze_matches(games)

            if not results:
                st.warning("No se encontraron oportunidades con Valor Esperado (EV+) positivo.")
            else:
                st.subheader("🔥 Picks Sharp Detectados")
                
                # Despliegue de cada apuesta encontrada
                for res in results:
                    r = res["pick"]
                    with st.expander(f"📍 {r.match} | Sugerido: {r.selection}", expanded=True):
                        c1, c2 = st.columns([1, 2])
                        c1.metric("EV (Ventaja)", f"{round(r.ev * 100, 1)}%", delta=f"{r.odd} cuota")
                        
                        c2.text("Análisis Estadístico (Probabilidad vs Cuota):")
                        c2.code(res["text"])

                # --- PASO 3: CONSTRUCCIÓN DE PARLAY (HASTA 5 PICKS) ---
                st.divider()
                lista_picks = [res["pick"] for res in results]
                parlay = build_smart_parlay(lista_picks)

                if parlay:
                    st.subheader("🚀 Smart Parlay Sugerido")
                    with st.container(border=True):
                        st.write(f"**Combinada:** {' + '.join(parlay.matches)}")
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Cuota Total", f"{parlay.total_odd}x")
                        col2.metric("Probabilidad", f"{round(parlay.combined_prob * 100, 1)}%")
                        col3.metric("EV Total", f"{round(parlay.total_ev * 100, 1)}%")

                        st.divider()
                        
                        # --- CALCULADORA DE INVERSIÓN ---
                        col_monto, col_ganancia = st.columns(2)
                        
                        with col_monto:
                            monto = st.number_input("Monto a invertir ($)", min_value=10.0, value=100.0, step=10.0)
                        
                        with col_ganancia:
                            ganancia = monto * parlay.total_odd
                            st.write("") # Espaciador visual
                            st.success(f"💰 **Ganancia Posible: ${round(ganancia, 2)}**")
                        
                        # --- BOTÓN DE REGISTRO ---
                        if st.button("📥 Registrar en Historial", use_container_width=True):
                            # Aquí se disparará la lógica de guardado en CSV/Base de datos
                            st.balloons()
                            st.toast("Parlay guardado correctamente", icon="✅")

else:
    st.info("Por favor, sube una captura de pantalla de los momios de Caliente para comenzar el análisis.")
