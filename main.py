import streamlit as st
import pandas as pd
import datetime
import os

# Importación de tus módulos personalizados
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

# Configuración de la página
st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")
st.markdown("---")

# --- SIDEBAR: HISTORIAL Y MÉTRICAS ---
with st.sidebar:
    st.header("📊 Historial")
    if os.path.exists("parlay_history.csv"):
        hist = pd.read_csv("parlay_history.csv")
        total_apostado = hist["monto"].sum()
        total_ganancia = hist["ganancia_neta"].sum()
        roi = (total_ganancia / total_apostado * 100) if total_apostado > 0 else 0
        
        st.metric("ROI Total", f"{roi:.1f}%", f"${total_ganancia:.2f}")
        st.metric("Apostado", f"${total_apostado:.2f}")
    else:
        st.info("Aún no hay parlays registrados")

# --- CARGA DE ARCHIVO ---
archivo = st.file_uploader("Sube captura de Caliente o cualquier liga", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Procesando imagen con IA..."):
        # Análisis OCR y extracción de datos
        games = analyze_betting_image(archivo)
    
    if games:
        # SECCIÓN CORREGIDA: Verificación de Partidos (Ocultable)
        with st.expander("🏟️ Verificación de Partidos (Click para ver/ocultar)", expanded=False):
            st.dataframe(games, use_container_width=True)

        # Inicializar motor de análisis y ejecutar cascada
        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        # --- MOSTRAR ANÁLISIS INDIVIDUAL ---
        st.header("📊 Análisis de Valor IA")
        col1, col2 = st.columns(2)
        for idx, r in enumerate(resultados):
            with (col1 if idx % 2 == 0 else col2):
                st.caption(f"**{r['partido']}**")
                # Indicador visual de probabilidad
                color = "#00ff9d" if r['probabilidad'] >= 70 else "#ffcc00"
                st.markdown(f"""
                <div style="border:1px solid #333; padding:10px; border-radius:8px; margin-bottom:10px;">
                    <span style="color:{color};">●</span> Pick: <b>{r['pick']}</b><br>
                    <small>Prob: {r['probabilidad']}% | Cuota: {r['cuota']} | EV: {r['ev']}</small>
                </div>
                """, unsafe_allow_html=True)

        # --- GENERACIÓN DEL TICKET PROFESIONAL ---
        if parlay:
            st.markdown("---")
            st.header("🔥 Tu Ticket Profesional")

            monto = st.number_input("💰 Monto a apostar (MXN)", value=10.0, step=5.0, min_value=5.0, format="%.2f")
            sim = engine.simulate_parlay_profit(parlay, monto)

            # Contenedor del Ticket Visual
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:18px; border-radius:12px; margin:10px 0; border-left: 5px solid #00ff9d;">
                    <div style="font-size: 14px; color: #888;">{p['partido']}</div>
                    <div style="color:#00ff9d; font-size:20px; font-weight: bold; margin-top: 5px;">
                        Sí → {p['pick']}
                    </div>
                    <div style="margin-top: 8px;">
                        <span style="background: #333; padding: 3px 8px; border-radius: 5px; font-size: 12px;">
                            Cuota: <b>{p['cuota']}</b>
                        </span>
                        <span style="margin-left: 10px; font-size: 12px; color: #aaa;">
                            Probabilidad: {p['probabilidad']}%
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Resumen de Ganancias
            m1, m2, m3 = st.columns(3)
            m1.metric("Cuota Total", f"{sim['cuota_total']:.2f}")
            m2.metric("Pago Total", f"${sim['pago_total']:.2f}", delta=f"${sim['ganancia_neta']:.2f} neta")
            m3.metric("Num. Picks", f"{len(parlay)}")

            # --- REGISTRO EN HISTORIAL ---
            if st.button("💾 Registrar Parlay como Apostado", type="primary", use_container_width=True):
                history_file = "parlay_history.csv"
                new_row = {
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "monto": monto,
                    "cuota_total": sim['cuota_total'],
                    "pago_total": sim['pago_total'],
                    "ganancia_neta": sim['ganancia_neta'],
                    "num_legs": len(parlay),
                    "picks": " | ".join([f"{p['partido']} → {p['pick']}" for p in parlay]),
                    "status": "Pendiente"
                }
                
                if os.path.exists(history_file):
                    df = pd.read_csv(history_file)
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    df = pd.DataFrame([new_row])
                
                df.to_csv(history_file, index=False)
                st.success("✅ Parlay guardado exitosamente en el historial.")
                st.rerun()

else:
    st.info("Sube una captura de pantalla para comenzar el análisis en cascada.")

# --- SECCIÓN DE HISTORIAL ---
st.markdown("---")
with st.expander("📜 Ver Historial Completo de Parlays", expanded=False):
    if os.path.exists("parlay_history.csv"):
        st.dataframe(pd.read_csv("parlay_history.csv"), use_container_width=True)
    else:
        st.info("Aún no hay registros en el historial.")

