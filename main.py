import streamlit as st
import os
import sys
from datetime import datetime

# 1. Configuración de Rutas (Evita ImportError)
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Importaciones de Módulos
try:
    from modules.vision_reader import read_ticket_image
    from modules.cerebro import obtener_mejor_apuesta
    from modules.ev_engine import build_smart_parlay
    from modules.results_tracker import save_parlay, get_history
except ImportError as e:
    st.error(f"❌ Error de configuración: {e}")
    st.info("Asegúrate de que la carpeta 'modules' contenga un archivo '__init__.py' vacío.")
    st.stop()

# 3. Configuración de Página
st.set_page_config(
    page_title="BETTING AI EV+ PRO", 
    page_icon="🧠",
    layout="wide"
)

# Estilo CSS personalizado para métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #00ff00; }
    .stButton button { width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 BETTING AI — Sharp Money Detector")
st.caption("Análisis estadístico mediante Simulación Monte Carlo y OCR de Google Vision")

tab_analisis, tab_historial = st.tabs(["📊 Análisis de Imagen", "📜 Historial de Parlays"])

with tab_analisis:
    uploaded = st.file_uploader("Sube la captura de pantalla (Caliente, Bet365, etc.)", type=["png", "jpg", "jpeg"])

    if uploaded:
        # Gestión de Estado de Sesión
        if 'last_uploaded' in st.session_state and st.session_state.last_uploaded != uploaded.name:
            st.session_state.clear()
        st.session_state.last_uploaded = uploaded.name

        with st.status("Analizando momios con AI Vision...", expanded=True) as status:
            # Llamada al módulo de OCR
            games_data = read_ticket_image(uploaded)
            
            if not games_data:
                st.error("No se detectaron bloques de apuestas válidos en la imagen.")
                status.update(label="Error en OCR", state="error")
                st.stop()
                
            results = []
            for partido in games_data:
                # --- Rescate de nombres (Lógica de Limpieza) ---
                # Si el OCR falló en separar Local/Visita, usamos el 'context'
                if "vs" in partido.get("home", "") or not partido.get("away") or "Visitante" in partido.get("away", ""):
                    context = partido.get("context", "").replace(" vs ", " ").split()
                    if len(context) >= 2:
                        partido["home"] = context[0]
                        partido["away"] = context[-1]
                
                # --- Procesamiento en Cerebro (Simulaciones) ---
                mejor_pick = obtener_mejor_apuesta(partido)
                if mejor_pick:
                    results.append({"pick": mejor_pick})
            
            status.update(label="Análisis y Simulación completados", state="complete")

        # --- Visualización de Resultados ---
        if results:
            lista_picks = [res["pick"] for res in results]
            
            # Construcción del Parlay Sugerido
            parlay = build_smart_parlay(lista_picks)

            if parlay:
                st.subheader("🚀 SUGERENCIA DE INVERSIÓN (PARLAY EV+)")
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])
                    
                    with c1:
                        st.write("### 📝 Selecciones recomendadas:")
                        for m in parlay.get("matches", []):
                            st.write(f"✅ **{m}**")
                    
                    with c2:
                        st.write("### 📈 Análisis de Valor")
                        st.metric("Cuota Final", f"{parlay.get('total_odd', 1.0):.2f}x")
                        st.metric("Probabilidad Combinada", f"{round(parlay.get('combined_prob', 0) * 100, 1)}%")
                        st.metric("Ventaja (EV Total)", f"+{round(parlay.get('total_ev', 0) * 100, 2)}%")
                    
                    st.divider()
                    
                    monto = st.number_input("Cantidad a invertir ($)", min_value=10.0, value=100.0, step=10.0)
                    ganancia = monto * parlay.get("total_odd", 1.0)
                    st.success(f"💰 Retorno potencial: ${round(ganancia, 2)}")
                    
                    if st.button("📥 Registrar Apuesta en Historial", use_container_width=True):
                        save_parlay({
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "matches": parlay.get("matches", []),
                            "cuota": parlay.get("total_odd", 1.0),
                            "monto": monto,
                            "ganancia_potencial": round(ganancia, 2)
                        })
                        st.balloons()
                        st.toast("Parlay guardado correctamente.")
            else:
                st.info("La IA no encontró suficiente ventaja estadística para armar un Parlay hoy.")

            # --- Desglose Individual ---
            with st.expander("🔍 Ver desglose de picks individuales (EV por mercado)", expanded=False):
                for res in results:
                    r = res["pick"]
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**{r.get('match')}**")
                        st.caption(f"Mercado: {r.get('selection')}")
                    with col_b:
                        ev_val = r.get('ev', 0) * 100
                        st.write(f"**EV: {ev_val:.1f}%**")
                        st.write(f"Momio: {r.get('odd')}")
                    st.divider()
        else:
            st.warning("No se encontraron apuestas con Valor Esperado Positivo (EV+).")

with tab_historial:
    st.subheader("📋 Registro Histórico")
    historial = get_history()
    
    if not historial:
        st.info("No hay registros de apuestas previas.")
    else:
        # Invertir para ver el más reciente primero
        for entry in reversed(historial):
            with st.expander(f"📅 {entry['fecha']} | Inversión: ${entry['monto']} | {entry['cuota']}x"):
                st.write("**Partidos:**")
                for m in entry.get('matches', []):
                    st.write(f"- {m}")
                st.write(f"**Resultado potencial:** ${entry.get('ganancia_potencial', 0)}")
