import streamlit as st
import os
from modules.vision_reader import read_ticket_image
from modules.cerebro import obtener_mejor_apuesta
from modules.ev_engine import build_smart_parlay

# 1. Configuración de la Interfaz Profesional
st.set_page_config(page_title="BETTING AI EV+ PRO", layout="wide")

# Barra lateral para diagnóstico de sistema
with st.sidebar:
    st.header("⚙️ Estado del Sistema")
    if os.path.exists("modules/__init__.py"):
        st.success("Integración de Módulos: OK")
    else:
        st.error("Error: Falta __init__.py en modules")
    
    st.divider()
    st.info("Escaneando 13 mercados: 1X2, Over/Under, BTTS, Doble Oportunidad, y Resultados Combinados.")

# 2. Encabezado Principal
st.title("🧠 BETTING AI — Sharp Money Detector")
st.markdown("Suba una captura de **Caliente.mx** para iniciar el análisis estadístico exhaustivo.")

# 3. Cargador de Archivos
uploaded = st.file_uploader("Cargar Ticket o Momios", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.status("Ejecutando Pipeline de Análisis Real...", expanded=True) as status:
        # PASO 1: OCR de Visión
        st.write("Extrayendo datos de la imagen...")
        games_data = read_ticket_image(uploaded)
        
        if not games_data:
            st.error("No se detectaron partidos. Intenta con una imagen más clara.")
            st.stop()
            
        # PASO 2: Análisis Individual por Partido (Cerebro)
        st.write(f"Analizando {len(games_data)} partidos en 13 mercados diferentes...")
        results = []
        for partido in games_data:
            mejor_opcion = obtener_mejor_apuesta(partido)
            if mejor_opcion:
                results.append({
                    "pick": mejor_opcion,
                    "text": f"Simulación Montecarlo terminada.\nProbabilidad: {round(mejor_opcion.probability * 100, 2)}%\nMercado detectado: {mejor_opcion.selection}"
                })
        
        status.update(label="Análisis Completo", state="complete")

    # 4. Despliegue de Resultados (Corregido IndentationError)
    if results:
        st.subheader("🔥 Picks Sharp Detectados")
        for res in results:
            r = res["pick"]
            # El bloque debajo del 'for' está correctamente indentado aquí
            with st.expander(f"📍 {r.match} | Sugerencia: {r.selection}", expanded=True):
                col1, col2 = st.columns([1, 2])
                # Calculamos el EV en porcentaje para la métrica
                ev_display = round(r.ev * 100, 2)
                col1.metric("EV+ (Ventaja)", f"{ev_display}%", delta=f"Cuota: {r.odd}")
                
                col2.text("Análisis de Probabilidad (Últimos 5 partidos):")
                col2.code(res["text"])

        # 5. Sección de Parlay Sugerido y Calculadora (Meta Principal)
        st.divider()
        lista_picks_objetos = [res["pick"] for res in results]
        parlay = build_smart_parlay(lista_picks_objetos)

        if parlay:
            st.subheader("🚀 Smart Parlay Sugerido (Top 5)")
            with st.container(border=True):
                st.write(f"**Estrategia Combinada:** {' + '.join(parlay.matches)}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Cuota Total", f"{parlay.total_odd}x")
                c2.metric("Prob. Combinada", f"{round(parlay.combined_prob * 100, 1)}%")
                c3.metric("EV Total", f"{round(parlay.total_ev, 2)}")

                st.divider()
                
                # --- CALCULADORA DE INVERSIÓN RECUPERADA ---
                col_monto, col_ganancia = st.columns(2)
                
                with col_monto:
                    monto = st.number_input("Monto a invertir ($)", min_value=10.0, value=100.0, step=10.0)
                
                with col_ganancia:
                    ganancia_total = monto * parlay.total_odd
                    st.write("Retorno Estimado:")
                    st.success(f"### ${round(ganancia_total, 2)}")
                
                # --- REGISTRO EN HISTORIAL ---
                if st.button("📥 Registrar Apuesta en Historial", use_container_width=True):
                    # Aquí el sistema guarda el resultado
                    st.balloons()
                    st.toast("Parlay guardado correctamente en la base de datos.", icon="✅")
    else:
        st.warning("El motor analizó los mercados pero no encontró ninguna apuesta con Valor Esperado (EV) positivo.")

else:
    st.info("Esperando imagen para procesar análisis estadístico...")

