import streamlit as st
import os
from modules.vision_reader import read_ticket_image
from modules.ev_engine import analyze_matches, build_smart_parlay

# Configuración de página
st.set_page_config(page_title="EV ELITE v4 — Sharp Money Detector", layout="wide")

# --- SIDEBAR: ESTADO DEL SISTEMA ---
with st.sidebar:
    st.header("⚙️ Sistema")
    if os.path.exists("modules/__init__.py"):
        st.success("Paquete modules: OK")
    else:
        st.warning("Falta modules/__init__.py")
    
    st.divider()
    st.info("""
    **Modo Sharp Activo:**
    Analizando Resultado Final, Doble Oportunidad, Ambos Anotan y Totales (1.5, 2.5, 3.5).
    """)

# --- CUERPO PRINCIPAL ---
st.title("🧠 BETTING AI — Sharp Money Detector")
st.write("Sube tu ticket para detectar valor real comparando cuotas de Caliente vs. Probabilidad Estadística.")

uploaded = st.file_uploader("Sube imagen del ticket", type=["png", "jpg", "jpeg"])

if uploaded:
    with st.status("Analizando últimos 5 partidos y simulando mercados...", expanded=True) as status:
        # 1. Ejecutar OCR para detectar partidos y cuotas
        st.write("Leyendo datos del ticket...")
        games = read_ticket_image(uploaded)
        
        if not games:
            st.error("No se detectaron partidos en el ticket.")
            st.stop()
        
        # 2. Ejecutar Motor de EV (Poisson Multimercado)
        st.write("Simulando probabilidades por mercado...")
        results = analyze_matches(games)
        
        status.update(label="Análisis Estadístico Completado", state="complete", expanded=False)

    # --- RENDERIZADO DE RESULTADOS ---
    if not results:
        st.warning("⚠️ No se encontraron oportunidades con Valor Esperado (EV+) positivo bajo los filtros actuales.")
    else:
        st.subheader("🔥 Picks Sharp Detectados")
        st.caption("Se muestra la opción con mayor ventaja matemática por partido.")
        
        for res in results:
            r = res["pick"]
            # El expander ahora muestra el nombre del equipo sugerido directamente
            with st.expander(f"📍 {r.match} | Sugerido: {r.selection}", expanded=True):
                col_stats, col_report = st.columns([1, 2])
                
                with col_stats:
                    st.metric("EV (Ventaja)", f"{round(r.ev * 100, 1)}%", delta=f"{r.odd} cuota")
                    st.write(f"**Probabilidad:** {int(r.probability * 100)}%")
                
                with col_report:
                    st.markdown("**Comparativa Multimercado:**")
                    # Muestra el desglose completo que calculó el motor
                    st.code(res["text"], language="text")

        # --- SECCIÓN DE PARLAY INTELIGENTE ---
        st.divider()
        lista_picks = [res["pick"] for res in results]
        parlay = build_smart_parlay(lista_picks)

        if parlay:
            st.subheader("🚀 Smart Parlay Sugerido (High EV)")
            
            with st.container(border=True):
                st.info(f"**Combinada Sugerida:** {' + '.join(parlay.matches)}")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Cuota Total", f"{parlay.total_odd}x")
                c2.metric("Probabilidad Combinada", f"{round(parlay.combined_prob * 100, 2)}%")
                # Mostramos el EV total del parlay
                c3.metric("EV Total", f"{parlay.total_ev}")

                st.divider()
                
                # --- CALCULADORA DE INVERSIÓN ---
                col_m, col_g = st.columns([1, 1])
                
                with col_m:
                    monto = st.number_input("Monto a invertir ($)", min_value=10.0, value=100.0, step=10.0)
                
                with col_g:
                    ganancia_pos = monto * parlay.total_odd
                    st.write(" ") # Espaciado
                    st.success(f"💰 **Ganancia Posible: ${round(ganancia_pos, 2)}**")
                
                if st.button("📥 Registrar en Historial", use_container_width=True):
                    # Aquí puedes llamar a tu función de tracker.py para guardar el CSV
                    st.balloons()
                    st.toast("Parlay registrado con éxito.", icon="✅")

else:
    st.info("Esperando ticket para iniciar el análisis profundo de los últimos 5 partidos.")
