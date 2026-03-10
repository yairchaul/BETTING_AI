# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import math
from modules.vision_reader import ImageParser
from modules.elo_system import ELOSystem
from modules.odds_api_integrator import OddsAPIIntegrator
from modules.football_api_client import FootballAPIClient
from modules.parlay_reasoning_engine import ParlayReasoningEngine

st.set_page_config(page_title="Analizador Profesional de Apuestas", layout="wide")

# =============================================================================
# FUNCIONES DE CÁLCULO DE MERCADOS ADICIONALES
# =============================================================================
def calculate_additional_markets(home_stats, away_stats):
    """Calcula probabilidades para Over/Under, BTTS, Hándicap"""
    
    # Over/Under basado en goles promedio
    avg_total_goals = home_stats['avg_goals_scored'] + away_stats['avg_goals_scored']
    
    # Distribución Poisson para Over/Under
    def poisson_prob(k, lam):
        return (math.exp(-lam) * lam**k) / math.factorial(k)
    
    # Over 1.5
    over_1_5 = 1 - poisson_prob(0, avg_total_goals) - poisson_prob(1, avg_total_goals)
    
    # Over 2.5
    over_2_5 = 1 - sum(poisson_prob(i, avg_total_goals) for i in range(3))
    
    # Over 3.5
    over_3_5 = 1 - sum(poisson_prob(i, avg_total_goals) for i in range(4))
    
    # BTTS (Both Teams To Score)
    prob_home_score = 1 - poisson_prob(0, home_stats['avg_goals_scored'])
    prob_away_score = 1 - poisson_prob(0, away_stats['avg_goals_scored'])
    btts_prob = prob_home_score * prob_away_score
    
    # Hándicap Asiático (simplificado)
    goal_diff = home_stats['avg_goals_scored'] - away_stats['avg_goals_scored']
    if goal_diff > 0.5:
        handicap_minus_1_prob = 0.65
    else:
        handicap_minus_1_prob = 0.35
    
    return {
        'over_1_5': over_1_5,
        'over_2_5': over_2_5,
        'over_3_5': over_3_5,
        'btts_yes': btts_prob,
        'btts_no': 1 - btts_prob,
        'handicap_home_-1': handicap_minus_1_prob
    }

# =============================================================================
# INICIALIZACIÓN DE COMPONENTES
# =============================================================================
@st.cache_resource
def init_components():
    return {
        'vision': ImageParser(),
        'elo': ELOSystem(),
        'odds_api': OddsAPIIntegrator(),
        'stats_api': FootballAPIClient(),
        'reasoning': ParlayReasoningEngine(
            prob_threshold_high=0.60,
            prob_threshold_medium=0.50,
            prob_threshold_low=0.30
        )
    }

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def american_to_decimal(american):
    if not american or american == 'N/A':
        return 2.0
    try:
        american = str(american).replace('+', '')
        american = int(american)
        if american > 0:
            return round(1 + (american / 100), 2)
        else:
            return round(1 + (100 / abs(american)), 2)
    except:
        return 2.0

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    st.title("🎯 Analizador Profesional de Apuestas")
    st.markdown("**Google Vision + ELO + Estadísticas Reales + Jerarquía de Probabilidades**")

    components = init_components()

    # Sidebar con configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        bankroll = st.number_input("Bankroll ($)", 100, 10000, 1000)
        min_ev = st.slider("EV mínimo", 0.0, 0.2, 0.05, 0.01)
        include_stats = st.checkbox("Incluir estadísticas actuales", True)
        include_odds_api = st.checkbox("Comparar con Odds-API", True)

    uploaded_file = st.file_uploader("Sube tu captura de Caliente.mx", type=['png', 'jpg', 'jpeg'])

    if uploaded_file:
        img_bytes = uploaded_file.getvalue()
        st.image(img_bytes, use_container_width=True)

        with st.spinner("🔍 Analizando imagen con Google Vision..."):
            matches = components['vision'].process_image(img_bytes)

        if matches:
            st.success(f"✅ Partidos detectados: {len(matches)}")

            # Mostrar tabla de partidos
            df_data = []
            for match in matches:
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                df_data.append({
                    'Local': match.get('home', 'N/A'),
                    'L': odds[0],
                    'Empate': 'Empate',
                    'E': odds[1],
                    'Visitante': match.get('away', 'N/A'),
                    'V': odds[2]
                })
            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

            st.subheader("📊 Análisis por partido")
            all_analysis = []

            for i, match in enumerate(matches):
                home = match.get('home', '')
                away = match.get('away', '')
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])

                # Convertir a decimales
                dec_local = american_to_decimal(odds[0])
                dec_empate = american_to_decimal(odds[1])
                dec_visit = american_to_decimal(odds[2])

                with st.expander(f"**{home} vs {away}**", expanded=(i==0)):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Local", odds[0], f"{dec_local:.2f}")
                    with col2:
                        st.metric("Empate", odds[1], f"{dec_empate:.2f}")
                    with col3:
                        st.metric("Visitante", odds[2], f"{dec_visit:.2f}")

                    # Obtener estadísticas actuales
                    home_stats = None
                    away_stats = None
                    additional_markets = {}
                    
                    if include_stats:
                        home_stats = components['stats_api'].get_team_stats(home)
                        away_stats = components['stats_api'].get_team_stats(away)
                        
                        if home_stats and away_stats:
                            st.caption(f"📈 {home}: {home_stats['avg_goals_scored']:.2f} GF | {away}: {away_stats['avg_goals_scored']:.2f} GF")
                            
                            # Calcular mercados adicionales
                            additional_markets = calculate_additional_markets(home_stats, away_stats)
                            
                            # Mostrar en columnas
                            st.markdown("**📈 Mercados Adicionales:**")
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                st.metric("Over 1.5", f"{additional_markets['over_1_5']:.1%}")
                                st.metric("Over 2.5", f"{additional_markets['over_2_5']:.1%}")
                            with col_m2:
                                st.metric("Over 3.5", f"{additional_markets['over_3_5']:.1%}")
                                st.metric("BTTS Sí", f"{additional_markets['btts_yes']:.1%}")
                            with col_m3:
                                st.metric("BTTS No", f"{additional_markets['btts_no']:.1%}")
                                st.metric("Hándicap -1", f"{additional_markets['handicap_home_-1']:.1%}")

                    # Probabilidades ELO mejoradas
                    probs = components['elo'].get_win_probability(home, away, home_stats, away_stats)

                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.metric("Gana Local", f"{probs['home']:.1%}")
                    with col_p2:
                        st.metric("Empate", f"{probs['draw']:.1%}")
                    with col_p3:
                        st.metric("Gana Visitante", f"{probs['away']:.1%}")

                    # Obtener odds en vivo
                    odds_en_vivo = None
                    if include_odds_api:
                        odds_en_vivo = components['odds_api'].get_live_odds(home, away)
                        if odds_en_vivo:
                            st.caption(f"🌐 Odds en vivo: Local {odds_en_vivo['cuota_local']:.2f} | Empate {odds_en_vivo['cuota_empate']:.2f} | Visitante {odds_en_vivo['cuota_visitante']:.2f}")

                    odds_para_ev = odds_en_vivo if odds_en_vivo else {
                        'cuota_local': dec_local,
                        'cuota_empate': dec_empate,
                        'cuota_visitante': dec_visit
                    }

                    # Calcular Value Bets para mercados 1X2
                    ev_local = (probs['home'] * odds_para_ev['cuota_local']) - 1
                    ev_draw = (probs['draw'] * odds_para_ev['cuota_empate']) - 1
                    ev_away = (probs['away'] * odds_para_ev['cuota_visitante']) - 1

                    value_bets = []
                    
                    # 1X2 Value Bets
                    if ev_local > min_ev:
                        value_bets.append({
                            'market': f"Gana {home}",
                            'prob': probs['home'],
                            'odds': odds_para_ev['cuota_local'],
                            'ev': ev_local,
                            'category': '1X2'
                        })
                        st.success(f"🔥 Local: EV +{ev_local:.1%}")
                    
                    if ev_draw > min_ev:
                        value_bets.append({
                            'market': 'Empate',
                            'prob': probs['draw'],
                            'odds': odds_para_ev['cuota_empate'],
                            'ev': ev_draw,
                            'category': '1X2'
                        })
                        st.success(f"🔥 Empate: EV +{ev_draw:.1%}")
                    
                    if ev_away > min_ev:
                        value_bets.append({
                            'market': f"Gana {away}",
                            'prob': probs['away'],
                            'odds': odds_para_ev['cuota_visitante'],
                            'ev': ev_away,
                            'category': '1X2'
                        })
                        st.success(f"🔥 Visitante: EV +{ev_away:.1%}")

                    # Guardar análisis completo
                    match_analysis = {
                        'home_team': home,
                        'away_team': away,
                        'value_bets': value_bets,
                        'additional_markets': additional_markets,
                        'probs_1x2': probs,
                        'odds_decimal': {
                            'local': dec_local,
                            'empate': dec_empate,
                            'visitante': dec_visit
                        }
                    }
                    all_analysis.append(match_analysis)

            # =========================================================================
            # SECCIÓN DE PARLAY CON JERARQUÍA (TU LÓGICA)
            # =========================================================================
            if len(all_analysis) >= 2:
                st.divider()
                st.subheader("🎯 SELECCIÓN DE APUESTAS POR JERARQUÍA")
                
                # Seleccionar mejores apuestas según tu lógica
                selected_bets = components['reasoning'].select_best_bets_by_hierarchy(all_analysis)
                
                # Mostrar las selecciones
                st.markdown("**📋 Mejores opciones por partido:**")
                for bet in selected_bets:
                    st.markdown(f"• {bet['match']}: **{bet['market']}** ({bet['prob']:.1%}) [EV: +{bet['ev']:.1%}]")
                
                st.divider()
                st.subheader("🎯 PARLAYS RECOMENDADOS")
                
                # Crear pestañas para diferentes estrategias
                tab1, tab2, tab3 = st.tabs(["🛡️ Conservador", "⚖️ Balanceado", "🚀 Agresivo"])
                
                with tab1:
                    st.markdown("**Solo apuestas con probabilidad > 60%**")
                    conservative = components['reasoning'].generate_parlay_by_strategy(
                        selected_bets, 'conservative', max_size=3
                    )
                    if conservative:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Probabilidad", f"{conservative['prob_total']:.1%}")
                        with col2:
                            st.metric("Cuota total", f"{conservative['odds_total']:.2f}")
                        with col3:
                            st.metric("EV total", f"{conservative['ev_total']:.1%}")
                        
                        st.markdown("**Selecciones:**")
                        for bet in conservative['bets']:
                            st.markdown(f"• {bet['match']}: **{bet['market']}** ({bet['prob']:.1%})")
                        
                        if conservative['ev_total'] > 0:
                            stake = conservative['stake_suggested'] * (bankroll / 1000)
                            st.success(f"💰 Stake sugerido: ${stake:.2f}")
                    else:
                        st.info("No hay suficientes apuestas con >60% de probabilidad")
                
                with tab2:
                    st.markdown("**Top 5 mejores opciones (tu estrategia original)**")
                    balanced = components['reasoning'].generate_parlay_by_strategy(
                        selected_bets, 'balanced', max_size=5
                    )
                    if balanced:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Probabilidad", f"{balanced['prob_total']:.1%}")
                        with col2:
                            st.metric("Cuota total", f"{balanced['odds_total']:.2f}")
                        with col3:
                            st.metric("EV total", f"{balanced['ev_total']:.1%}")
                        
                        st.markdown("**Selecciones:**")
                        for bet in balanced['bets']:
                            st.markdown(f"• {bet['match']}: **{bet['market']}** ({bet['prob']:.1%})")
                        
                        if balanced['ev_total'] > 0:
                            stake = balanced['stake_suggested'] * (bankroll / 1000)
                            st.success(f"💰 Stake sugerido: ${stake:.2f}")
                    else:
                        st.info("No hay suficientes selecciones")
                
                with tab3:
                    st.markdown("**Todas las apuestas con prob > 30%**")
                    aggressive = components['reasoning'].generate_parlay_by_strategy(
                        selected_bets, 'aggressive', max_size=5
                    )
                    if aggressive:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Probabilidad", f"{aggressive['prob_total']:.1%}")
                        with col2:
                            st.metric("Cuota total", f"{aggressive['odds_total']:.2f}")
                        with col3:
                            st.metric("EV total", f"{aggressive['ev_total']:.1%}")
                        
                        st.markdown("**Selecciones:**")
                        for bet in aggressive['bets']:
                            st.markdown(f"• {bet['match']}: **{bet['market']}** ({bet['prob']:.1%})")
                        
                        if aggressive['ev_total'] > 0:
                            stake = aggressive['stake_suggested'] * (bankroll / 1000)
                            st.success(f"💰 Stake sugerido: ${stake:.2f}")
                    else:
                        st.info("No hay suficientes apuestas con >30%")
        else:
            st.error("❌ No se detectaron partidos en la imagen")

if __name__ == "__main__":
    main()