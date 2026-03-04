import streamlit as st
import pandas as pd
import numpy as np
from modules.parser_tesseract_final import TesseractParser
from modules.pro_analyzer_simple import ProAnalyzerSimple
from modules.odds_api_integrator import OddsAPIIntegrator
import json
import os

st.set_page_config(page_title="Analizador de Apuestas con Tesseract", layout="wide")

# Inicializar estado de sesión para debug
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

@st.cache_resource
def init_components():
    """Inicializa los componentes de la aplicación"""
    return {
        'parser': TesseractParser(),
        'analyzer': ProAnalyzerSimple(),
        'odds_api': OddsAPIIntegrator()
    }

def american_to_decimal(american):
    """Convierte odds americanas a decimales"""
    if not american or american == 'N/A':
        return 2.0
    try:
        american = str(american).replace('+', '').strip()
        american = int(american)
        if american > 0:
            return round(1 + (american / 100), 2)
        else:
            return round(1 + (100 / abs(american)), 2)
    except:
        return 2.0

def main():
    st.title(" Analizador Profesional de Apuestas")
    st.markdown("**Basado en datos REALES de 2026 con OCR local**")

    # Sidebar
    with st.sidebar:
        st.header(" Configuración")
        bankroll = st.number_input("Bankroll ($)", min_value=100, max_value=10000, value=1000, step=100)
        min_ev = st.slider("EV mínimo para value bets", 0.0, 0.2, 0.05, 0.01)
        st.session_state.debug_mode = st.checkbox(" Modo debug", value=False)
        
        st.divider()
        st.subheader(" Estado del sistema")
        
        # Verificar Tesseract
        try:
            import pytesseract
            st.success(" Tesseract OK")
        except:
            st.error(" Tesseract no instalado")
        
        # Verificar Odds-API
        try:
            odds_api = OddsAPIIntegrator()
            if odds_api.api_key:
                st.success(" Odds-API OK")
            else:
                st.warning(" Odds-API sin key")
        except:
            st.warning(" Odds-API no disponible")

    # Área principal
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Sube tu captura de Caliente.mx")
        uploaded_file = st.file_uploader("Selecciona imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)

    if uploaded_file:
        with st.spinner(" Procesando imagen con Tesseract OCR..."):
            # Inicializar componentes
            components = init_components()
            
            # Procesar imagen
            matches = components['parser'].parse_image(uploaded_file)
            
            if matches:
                st.success(f" Partidos detectados: {len(matches)}")
            else:
                st.error(" No se detectaron partidos en la imagen")

        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                # Mostrar tabla de partidos
                df_view = []
                for m in matches:
                    df_view.append({
                        'LOCAL': m.get('local', 'N/A')[:15],
                        'CUOTA L': m.get('cuota_local', 'N/A'),
                        'EMPATE': m.get('empate', 'N/A'),
                        'CUOTA E': m.get('cuota_empate', 'N/A'),
                        'VISITANTE': m.get('visitante', 'N/A')[:15],
                        'CUOTA V': m.get('cuota_visitante', 'N/A')
                    })
                
                st.dataframe(
                    pd.DataFrame(df_view), 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={
                        'LOCAL': 'Local',
                        'CUOTA L': 'L',
                        'EMPATE': 'Emp',
                        'CUOTA E': 'E',
                        'VISITANTE': 'Visitante',
                        'CUOTA V': 'V'
                    }
                )

            st.divider()
            st.subheader("3. Análisis con datos REALES 2026")

            all_analisis = []
            
            for idx, match in enumerate(matches):
                home = match.get('local', '').strip()
                away = match.get('visitante', '').strip()
                
                # Convertir odds de la captura a decimal
                odds_captura = {
                    'local': american_to_decimal(match.get('cuota_local', '')),
                    'draw': american_to_decimal(match.get('cuota_empate', '')),
                    'away': american_to_decimal(match.get('cuota_visitante', ''))
                }
                
                with st.expander(f" {home} vs {away}", expanded=(idx == 0)):
                    # Analizar el partido
                    analisis = components['analyzer'].analyze_match(home, away, odds_captura)
                    all_analisis.append(analisis)
                    
                    # Mostrar odds del mercado
                    st.caption(
                        f" Odds mercado: Local **{analisis['odds_reales']['cuota_local']:.2f}** | "
                        f"Empate **{analisis['odds_reales']['cuota_empate']:.2f}** | "
                        f"Visitante **{analisis['odds_reales']['cuota_visitante']:.2f}**"
                    )
                    
                    # Mostrar probabilidades ELO
                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.metric("Gana Local", f"{analisis['elo_probs']['home']:.1%}")
                    with col_p2:
                        st.metric("Empate", f"{analisis['elo_probs']['draw']:.1%}")
                    with col_p3:
                        st.metric("Gana Visitante", f"{analisis['elo_probs']['away']:.1%}")
                    
                    # Mostrar mercados con VALUE
                    if analisis['value_bets']:
                        st.markdown("###  VALUE BETS DETECTADOS")
                        
                        # Crear tabla de value bets
                        vb_data = []
                        for vb in analisis['value_bets']:
                            vb_data.append({
                                'Mercado': vb['name'][:20],
                                'Prob': f"{vb['prob']:.1%}",
                                'Odds': f"{vb['odds']:.2f}",
                                'EV': f"+{vb['ev']:.1%}"
                            })
                        
                        st.dataframe(pd.DataFrame(vb_data), hide_index=True, use_container_width=True)
                    else:
                        st.info("ℹ No se detectaron value bets significativos (EV < 5%)")

            # Buscar mejor parlay
            if len(all_analisis) >= 2:
                st.divider()
                st.subheader(" MEJOR PARLAY RECOMENDADO")
                
                best_parlay = components['analyzer'].find_best_parlay(all_analisis, max_size=3)
                
                if best_parlay and best_parlay.get('picks'):
                    # Calcular probabilidad total
                    prob_total = np.prod([p['prob'] for p in best_parlay['picks']])
                    odds_total = np.prod([p['odds'] for p in best_parlay['picks']])
                    ev_total = (prob_total * odds_total) - 1
                    
                    # Métricas del parlay
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        st.metric("Probabilidad total", f"{prob_total:.1%}")
                    with col_r2:
                        st.metric("Cuota total", f"{odds_total:.2f}")
                    with col_r3:
                        delta_color = "normal" if ev_total > 0 else "inverse"
                        st.metric("EV total", f"{ev_total:.1%}", delta_color=delta_color)
                    
                    # Lista de selecciones
                    st.markdown("**Selecciones:**")
                    for pick in best_parlay['picks']:
                        st.markdown(f" {pick['match']}: **{pick['selection']}** ({pick['prob']:.1%}) [EV: {pick['ev']:.1%}]")
                    
                    # Stake sugerido (Kelly fraccionario)
                    if ev_total > 0:
                        stake = (ev_total / (odds_total - 1)) * 0.25 * bankroll
                        st.success(f" Stake sugerido:  (25% Kelly)")
                    else:
                        st.warning(" EV negativo - No se recomienda apostar")
                else:
                    st.info("No se encontró parlay con EV positivo > 5%")
            
            # Mostrar texto raw si está en modo debug
            if st.session_state.debug_mode and 'raw_text' in locals():
                with st.expander(" Texto raw detectado por OCR"):
                    st.code(raw_text)

if __name__ == "__main__":
    main()
