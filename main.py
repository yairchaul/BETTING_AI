import streamlit as st
import pandas as pd
import datetime
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="BETTING AI — PARLAY MAESTRO", layout="wide")
st.title("🤖 BETTING AI — PARLAY MAESTRO")

# --- CARGA DE DATOS ---
history_file = "parlay_history.csv"

def save_parlay(new_row):
    df = pd.read_csv(history_file) if os.path.exists(history_file) else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(history_file, index=False)

def update_status(index, status):
    df = pd.read_csv(history_file)
    df.at[index, 'status'] = status
    # Si pierde, la ganancia neta es el monto en negativo
    if status == "Perdida":
        df.at[index, 'ganancia_neta'] = -df.at[index, 'monto']
    df.to_csv(history_file, index=False)

# --- SIDEBAR MÉTRICAS ---
with st.sidebar:
    st.header("📊 Resumen de Testeo")
    if os.path.exists(history_file):
        df_h = pd.read_csv(history_file)
        ganadas = df_h[df_h['status'] == 'Ganada']
        total_profit = df_h[df_h['status'] != 'Pendiente']['ganancia_neta'].sum()
        st.metric("Profit Total", f"${total_profit:.2f}")
        st.metric("Parlays Ganados", f"{len(ganadas)}")
    else:
        st.info("Sin datos")

# --- FLUJO PRINCIPAL ---
archivo = st.file_uploader("Sube captura de pantalla", type=["png", "jpg", "jpeg"])

if archivo:
    with st.spinner("Procesando..."):
        games = analyze_betting_image(archivo)
    
    if games:
        with st.expander("🏟️ Verificación de Partidos", expanded=False):
            st.dataframe(games, use_container_width=True)

        engine = EVEngine()
        resultados, parlay = engine.build_parlay(games)

        if parlay:
            st.header("🔥 Simulación de Parlay")
            monto = st.number_input("💰 Monto (MXN)", value=10.0, step=10.0)
            sim = engine.simulate_parlay_profit(parlay, monto)

            # Ticket visual limpio (Sin Sí ->)
            for p in parlay:
                st.markdown(f"""
                <div style="background:#1e1e1e; padding:12px; border-radius:10px; border-left: 5px solid #00ff9d; margin-bottom:8px;">
                    <span style="color:#00ff9d; font-weight:bold; font-size:16px;">{p['pick']}</span><br>
                    <small style="color:#888;">{p['partido']} | Cuota: {p['cuota']}</small>
                </div>
                """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Cuota Total", f"{sim['cuota_total']}")
            c2.metric("Pago Potencial", f"${sim['pago_total']}")
            c3.metric("Ganancia Neta", f"${sim['ganancia_neta']}")

            if st.button("💾 Registrar para Seguimiento"):
                new_row = {
                    "id": datetime.datetime.now().strftime("%H%M%S"),
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "monto": monto,
                    "cuota_total": sim['cuota_total'],
                    "ganancia_neta": sim['ganancia_neta'],
                    "status": "Pendiente",
                    "picks": " | ".join([p['pick'] for p in parlay])
                }
                save_parlay(new_row)
                st.success("Registrado. Revisa la tabla de abajo.")

# --- GESTIÓN DE PENDIENTES ---
st.markdown("---")
st.subheader("⏳ Control de Apuestas Pendientes")

if os.path.exists(history_file):
    df_p = pd.read_csv(history_file)
    for index, row in df_p.iterrows():
        if row['status'] == "Pendiente":
            with st.container():
                col_a, col_b, col_c = st.columns([3, 1, 1])
                col_a.write(f"**{row['fecha']}** - {row['picks']} (Total: ${row['cuota_total']})")
                if col_b.button("✅ Ganada", key=f"win_{index}"):
                    update_status(index, "Ganada")
                    st.rerun()
                if col_c.button("❌ Perdida", key=f"loss_{index}"):
                    update_status(index, "Perdida")
                    st.rerun()
    
    with st.expander("📂 Ver Todo el Historial"):
        st.dataframe(df_p, use_container_width=True)
