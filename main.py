import streamlit as st
import pandas as pd
import os
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine
from modules.cerebro import CerebroAuditor
from modules.tracker import registrar_parlay_automatico, PATH_HISTORIAL
from modules.bankroll import obtener_stake_sugerido

# 1. Configuración de Interfaz Inamovible
st.set_page_config(page_title="Betting AI - Auditoría Total", layout="wide")

st.markdown("""
    <style>
    .valor-card {
        background-color: #1a2c3d;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        border-left: 6px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .badge-alta { background-color: #2ecc71; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    .badge-media { background-color: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    .badge-riesgo { background-color: #e74c3c; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    .metric-box { text-align: center; background: #0e1117; padding: 15px; border-radius: 10px; border: 1px solid #1a2c3d; }
    </style>
""", unsafe_allow_html=True)

# Instanciar motores
engine = EVEngine()
auditor = CerebroAuditor()

st.title("🧠 Betting AI: Sistema de Auditoría Total")

# 2. SECCIÓN DE CARGA (RESTAURADA)
archivo = st.file_uploader("Cargar Ticket de Apuestas", type=["jpg", "png", "jpeg"])

if archivo:
    # Mostrar vista previa pequeña
    st.image(archivo, width=250, caption="Ticket cargado")
    
    # Procesar imagen con el lector de visión
    with st.spinner("Leyendo datos del ticket..."):
        matches, _ = analyze_betting_image(archivo)
    
    if matches:
        st.subheader("📋 Auditoría de Partidos Detectados")
        picks_auditados = []
        cols = st.columns(2)
        
        for i, game in enumerate(matches):
            # Obtener Edge Matemático (Cascada de Valor)
            poisson_raw = engine.get_raw_probabilities(game)
            
            # Auditoría del Cerebro (Fusión de datos)
            veredicto = auditor.decidir_mejor_apuesta(poisson_raw, {}, {})
            picks_auditados.append(veredicto)
            
            # Renderizado de Tarjeta Visual (Imagen 3)
            with cols[i % 2]:
                badge = veredicto['estatus'].lower()
                st.markdown(f"""
                <div class="valor-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem; font-weight: bold;">{game.get('home')} vs {game.get('away')}</span>
                        <span class="badge-{badge}">{veredicto['estatus']}</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <p style="color: #42A5F5; font-size: 1.1rem; margin-bottom: 5px;">🎯 Pick: <b>{veredicto['pick_final']}</b></p>
                        <p style="font-size: 0.9rem; color: #BDC3C7; margin: 0;">
                            Confianza: <b>{veredicto['confianza_final']}%</b> | EV: {veredicto['ev_final']} | Cuota: {veredicto['cuota_ref']}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 3. SECCIÓN FINANCIERA (LIMPIEZA DE CEROS)
        st.markdown("---")
        c1, c2 = st.columns(2)
        bankroll = c1.number_input("Bankroll Total (MXN)", value=1000.0, step=100.0)
        
        # Sugerencia automática de inversión
        conf_promedio = sum([p['confianza_final'] for p in picks_auditados]) / len(picks_auditados)
        stake_sugerido = obtener_stake_sugerido(bankroll, conf_promedio)
        
        monto_final = c2.number_input("Inversión para este Parlay", value=float(stake_sugerido))
        
        # Simulación final
        sim = engine.simulate_parlay_profit(picks_auditados, monto_final)
        
        # Métricas de pago con formato limpio
        f1, f2, f3 = st.columns(3)
        f1.metric("Cuota Final", f"{sim['cuota_total']:.2f}x")
        f2.metric("Pago Potencial", f"${sim['pago_total']:.2f}")
        f3.metric("Ganancia Neta", f"${sim['ganancia_neta']:.2f}")

        if st.button("🚀 REGISTRAR EN EL TRACKER DE VALOR", use_container_width=True):
            resumen = " | ".join([p['pick_final'] for p in picks_auditados])
            registrar_parlay_automatico(sim, resumen)
            st.success("✅ Parlay guardado en el historial.")
            st.rerun()
    else:
        st.error("No se detectaron mercados válidos en la imagen. Intenta con una captura más clara.")

# 4. HISTORIAL VISUAL (FORMATO TABLA LIMPIA)
st.markdown("---")
st.subheader("🏁 Estatus y Seguimiento de Parlays")
if os.path.exists(PATH_HISTORIAL):
    df_h = pd.read_csv(PATH_HISTORIAL)
    if not df_h.empty:
        # Formatear columnas para eliminar ceros innecesarios en la vista
        df_display = df_h.copy()
        df_display['Monto'] = df_display['Monto'].map('${:,.2f}'.format)
        df_display['Cuota'] = df_display['Cuota'].map('{:,.2f}x'.format)
        df_display['Pago_Potencial'] = df_display['Pago_Potencial'].map('${:,.2f}'.format)
        df_display['Ganancia_Neta'] = df_display['Ganancia_Neta'].map('${:,.2f}'.format)
        
        st.dataframe(df_display.sort_index(ascending=False), use_container_width=True)

