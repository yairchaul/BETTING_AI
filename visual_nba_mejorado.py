"""
VISUAL NBA MEJORADO - Muestra TODAS las cuotas correctamente
"""
import streamlit as st

class VisualNBAMejorado:
    def __init__(self):
        self.colores = {
            'local': '#FF6B35',
            'visitante': '#0066CC',
            'over': '#4CAF50',
            'under': '#f44336',
            'green': '#4CAF50',
            'yellow': '#FFC107',
            'blue': '#2196F3',
            'red': '#f44336',
            'orange': '#FF9800'
        }
    
    def render(self, partido, idx, tracker=None, 
               analisis_heurístico=None, 
               analisis_gemini=None, 
               analisis_premium=None):
        
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            local = partido.get('local', 'Local')
            visitante = partido.get('visitante', 'Visitante')
            hora = partido.get('hora', '20:00')
            odds = partido.get('odds', {})
            records = partido.get('records', {})
            
            # Extraer valores de spread
            spread_local = odds.get('spread', {}).get('valor', 0)
            spread_visit = -spread_local  # El visitante es el opuesto
            
            # Extraer odds del spread y totales
            spread_odds_local = odds.get('spread', {}).get('local_odds', 'N/A')
            spread_odds_visit = odds.get('spread', {}).get('visitante_odds', 'N/A')
            over_odds = odds.get('totales', {}).get('over_odds', 'N/A')
            under_odds = odds.get('totales', {}).get('under_odds', 'N/A')
            total_linea = odds.get('totales', {}).get('linea', 0)
            
            # Encabezado
            st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 15px; border-radius: 10px 10px 0 0; border-left: 5px solid #FF6B35;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #FF6B35; font-weight: bold;">🏀 NBA</span>
                    <span style="color: #888;">{hora}</span>
                </div>
                <h3 style="color: white; text-align: center; margin: 10px 0;">
                    {local} <span style="color: #FFA500;">({records.get('local', '0-0')})</span> 
                    <span style="color: #666;">VS</span> 
                    {visitante} <span style="color: #FFA500;">({records.get('visitante', '0-0')})</span>
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # 🔥 CUOTAS COMPLETAS - ahora con todos los valores
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**💰 MONEYLINE**")
                st.markdown(f"{local}: {odds.get('moneyline', {}).get('local', 'N/A')}")
                st.markdown(f"{visitante}: {odds.get('moneyline', {}).get('visitante', 'N/A')}")
            
            with col2:
                st.markdown("**📊 SPREAD**")
                st.markdown(f"{local}: {spread_local:+g}")
                st.markdown(f"{visitante}: {spread_visit:+g}")
                st.markdown(f"Odds: {spread_odds_local} / {spread_odds_visit}")
            
            with col3:
                st.markdown("**🎯 OVER/UNDER**")
                st.markdown(f"OVER {total_linea} ({over_odds})")
                st.markdown(f"UNDER {total_linea} ({under_odds})")
            
            st.markdown("---")
            
            # Tres columnas de análisis
            col_a1, col_a2, col_a3 = st.columns(3)
            
            # HEURÍSTICO
            with col_a1:
                st.markdown("<h4 style='color: #FFD700;'>📊 HEURÍSTICO</h4>", unsafe_allow_html=True)
                if analisis_heurístico:
                    color = self.colores.get(analisis_heurístico.get('color', 'gray'), '#9E9E9E')
                    st.markdown(f"**{analisis_heurístico.get('apuesta', 'N/A')}**")
                    st.markdown(f"Confianza: {analisis_heurístico.get('confianza', 0)}%")
                else:
                    st.markdown("Pendiente")
            
            # GEMINI IA
            with col_a2:
                st.markdown("<h4 style='color: #FFD700;'>🤖 GEMINI IA</h4>", unsafe_allow_html=True)
                if analisis_gemini:
                    color = self.colores.get(analisis_gemini.get('color', 'gray'), '#9E9E9E')
                    apuesta = analisis_gemini.get('apuesta', analisis_gemini.get('ganador', 'N/A'))
                    st.markdown(f"**{apuesta}**")
                    st.markdown(f"Confianza: {analisis_gemini.get('confianza', 0)}%")
                    razones = analisis_gemini.get('razones', [])
                    if razones:
                        for r in razones[:2]:
                            st.markdown(f"• {r}")
                else:
                    st.markdown("Pendiente")
            
            # PREMIUM ANALYTICS
            with col_a3:
                st.markdown("<h4 style='color: #FFD700;'>🔬 PREMIUM ANALYTICS</h4>", unsafe_allow_html=True)
                if analisis_premium:
                    edge = analisis_premium.get('edge_rating', 0)
                    public = analisis_premium.get('public_money', 0)
                    sharps = analisis_premium.get('sharps_action', 'N/A')
                    
                    st.markdown(f"**Edge Rating:** {edge}")
                    estrellas = "★" * int(edge) + "☆" * (10 - int(edge))
                    st.markdown(f"{estrellas}")
                    
                    st.markdown(f"**Public Money:** {public}% {analisis_premium.get('public_team', '')}")
                    st.markdown(f"**Sharps Action:** {sharps}")
                    
                    if analisis_premium.get('value_detected'):
                        st.markdown("💰 **VALUE DETECTED**")
                else:
                    st.markdown("Pendiente")
            
            st.markdown("---")
            
            # Botones
            col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
            
            with col_b1:
                if st.button(f"🔍 ANALIZAR", key=f"nba_analizar_{idx}"):
                    return "analizar"
            with col_b2:
                if st.button(f"➕ HANDICAP", key=f"nba_h_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"HANDICAP {local} {spread_local:+g}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓ Agregado")
            with col_b3:
                if st.button(f"➕ OVER", key=f"nba_o_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"OVER {total_linea}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓ OVER")
            with col_b4:
                if st.button(f"➕ UNDER", key=f"nba_u_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"UNDER {total_linea}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓ UNDER")
            with col_b5:
                if st.button(f"➕ ML", key=f"nba_ml_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'pick': f"GANA {local}",
                            'cuota': 1.91,
                            'deporte': 'NBA'
                        })
                        st.success("✓ ML")
            
            st.markdown("---")
