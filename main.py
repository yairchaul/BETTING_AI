import streamlit as st
import pandas as pd
import os
from modules.ev_engine import EVEngine
from modules.cerebro import CerebroAuditor
from modules.tracker import registrar_parlay_automatico, PATH_HISTORIAL
from modules.bankroll import obtener_stake_sugerido

# Configuración UI Inamovible
st.set_page_config(page_title="Betting AI Pro", layout="wide")
st.markdown("""
    <style>
    .valor-card {
        background-color: #1a2c3d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #1E88E5;
    }
    .badge-alta { background-color: #2ecc71; padding: 4px 12px; border-radius: 15px; }
    .badge-media { background-color: #f1c40f; color: black; padding: 4px 12px; border-radius: 15px; }
    .badge-riesgo { background-color: #e74c3c; padding: 4px 12px; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

engine = EVEngine()
auditor = CerebroAuditor()

st.title("🛡️ Sistema de Auditoría Total")

# Supongamos que ya procesaste el ticket (reutilizando tu lógica de carga)
# Aquí simulo el flujo para asegurar que la visual se mantenga
if 'matches' in st.session_state:
    picks_finales = []
    cols = st.columns(2)
    
    for i, game in enumerate(st.session_state.matches):
        raw = engine.get_raw_probabilities(game)
        veredicto = auditor.decidir_mejor_apuesta(raw, {}, {}) # Contexto vacío por ahora
        picks_finales.append(veredicto)
        
        with cols[i % 2]:
            estatus = veredicto['estatus'].lower()
            st.markdown(f"""
            <div class="valor-card">
                <div style="display: flex; justify-content: space-between;">
                    <h3 style="margin:0;">{game['home']}</h3>
                    <span class="badge-{estatus}">{veredicto['estatus']}</span>
                </div>
                <p style="color: #42A5F5; font-size: 1.2rem; margin-top: 10px;">🎯 {veredicto['pick_final']}</p>
                <p>Confianza: {veredicto['confianza_final']}% | Cuota: {veredicto['cuota_ref']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    # METRICAS FINANCIERAS (GRANDES Y LIMPIAS)
    monto_inv = st.number_input("Inversión Parlay (MXN)", value=100.0, step=10.0)
    res = engine.simulate_parlay_profit(picks_finales, monto_inv)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Cuota Final", f"{res['cuota_total']}x")
    m2.metric("Pago Potencial", f"${res['pago_total']}")
    m3.metric("Ganancia Neta", f"${res['ganancia_neta']}")

    if st.button("🚀 REGISTRAR EN TRACKER DE VALOR"):
        txt_picks = " | ".join([p['pick_final'] for p in picks_finales])
        registrar_parlay_automatico(res, txt_picks)
        st.success("Guardado.")
        st.rerun()

# TABLA HISTORIAL LIMPIA
if os.path.exists(PATH_HISTORIAL):
    st.markdown("### 🏁 Estatus y Seguimiento")
    df = pd.read_csv(PATH_HISTORIAL)
    # FORZAR REDONDEO EN LA VISTA PARA QUITAR LOS .0000000
    df['Monto'] = df['Monto'].map('{:,.2f}'.format)
    df['Cuota'] = df['Cuota'].map('{:,.2f}'.format)
    df['Pago_Potencial'] = df['Pago_Potencial'].map('{:,.2f}'.format)
    st.dataframe(df, use_container_width=True)

