"""
MAIN VISION FINAL - Con TODAS las ligas en el filtro
"""
import streamlit as st
from datetime import datetime
import os

from api_client import OddsAPIClient
from visual_futbol import VisualFutbol
from visual_nba_jerarquico import VisualNBA
from visual_ufc_mejorado import VisualUFC

st.set_page_config(
    page_title="BETTING_AI - Análisis Profesional",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 BETTING_AI - Análisis Deportivo Profesional")
st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ========================================
# LISTA COMPLETA DE LIGAS (TODAS)
# ========================================
TODAS_LAS_LIGAS = [
    "MEXICO LIGA MX",
    "MEXICO LIGA DE EXPANSION MX",
    "UEFA CHAMPIONS LEAGUE",
    "UEFA EUROPA LEAGUE",
    "SPAIN LA LIGA",
    "ENGLAND PREMIER LEAGUE",
    "GERMANY BUNDESLIGA",
    "ITALY SERIE A",
    "FRANCE LIGUE 1",
    "NETHERLANDS EREDIVISIE",
    "PORTUGAL PRIMEIRA LIGA",
    "BELGIUM FIRST DIV",
    "TURKEY SUPER LEAGUE"
]

if 'api_client' not in st.session_state:
    st.session_state.api_client = OddsAPIClient()
    st.session_state.visual_futbol = VisualFutbol()
    st.session_state.visual_nba = VisualNBA()
    st.session_state.visual_ufc = VisualUFC()
    st.session_state.partidos_futbol = []
    st.session_state.partidos_nba = []
    st.session_state.combates_ufc = []
    st.session_state.liga_seleccionada = "TODAS"

with st.sidebar:
    st.header("🎯 CONTROLES")
    
    if st.button("🔄 ACTUALIZAR DATOS", use_container_width=True):
        with st.spinner("📡 Extrayendo datos de todas las ligas..."):
            st.session_state.partidos_futbol = st.session_state.api_client.get_partidos_futbol() or []
            st.session_state.partidos_nba = st.session_state.api_client.get_partidos_nba() or []
            st.session_state.combates_ufc = st.session_state.api_client.get_combates_ufc() or []
            
            # Contar partidos por liga
            ligas_con_partidos = set([p['liga'] for p in st.session_state.partidos_futbol if 'liga' in p])
            st.success(f"✅ Fútbol: {len(st.session_state.partidos_futbol)} partidos en {len(ligas_con_partidos)} ligas | NBA: {len(st.session_state.partidos_nba)} | UFC: {len(st.session_state.combates_ufc)}")
    
    st.markdown("---")
    st.markdown("""
    ### 📊 VALUE BETTING
    - **🔥 Verde**: Value >10%
    - **⚡ Amarillo**: Value 5-10%
    - **📈 Naranja**: Value 0-5%
    - **❌ Rojo**: Sin valor
    """)

tab1, tab2, tab3 = st.tabs(["⚽ FÚTBOL (TODAS LAS LIGAS)", "🏀 NBA", "🥊 UFC"])

with tab1:
    # Selector de liga con TODAS las opciones
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        # Usar TODAS_LAS_LIGAS para el filtro, no solo las que tienen partidos
        liga_seleccionada = st.selectbox(
            "🔍 Filtrar por liga:", 
            ["TODAS"] + TODAS_LAS_LIGAS,
            index=0
        )
    
    with col_f2:
        st.metric("Total partidos hoy", len(st.session_state.partidos_futbol))
    
    # Mostrar partidos
    if st.session_state.partidos_futbol and len(st.session_state.partidos_futbol) > 0:
        partidos_mostrados = 0
        for i, partido in enumerate(st.session_state.partidos_futbol):
            liga_partido = partido.get('liga', '')
            
            # Filtrar por liga seleccionada
            if liga_seleccionada != "TODAS" and liga_partido != liga_seleccionada:
                continue
            
            partidos_mostrados += 1
            st.session_state.visual_futbol.render(partido, i)
        
        if partidos_mostrados == 0:
            st.info(f"ℹ️ No hay partidos en {liga_seleccionada} para hoy")
    else:
        st.info("👈 Actualiza para ver partidos de todas las ligas")

with tab2:
    if st.session_state.partidos_nba and len(st.session_state.partidos_nba) > 0:
        for i, partido in enumerate(st.session_state.partidos_nba):
            st.session_state.visual_nba.render(partido, i)
    else:
        st.info("No hay partidos NBA hoy")

with tab3:
    if st.session_state.combates_ufc and len(st.session_state.combates_ufc) > 0:
        st.info(f"📅 Próximo evento UFC: {len(st.session_state.combates_ufc)} combates")
        for i, combate in enumerate(st.session_state.combates_ufc):
            st.session_state.visual_ufc.render(combate, i)
    else:
        st.info("No hay eventos UFC programados")

st.markdown("---")
st.caption(f"⚡ {len(TODAS_LAS_LIGAS)} ligas monitoreadas | Datos: The Odds API + ESPN")
