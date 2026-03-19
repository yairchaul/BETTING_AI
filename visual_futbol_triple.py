"""
VISUAL FÚTBOL TRIPLE - Muestra los 3 análisis con regla
"""
import streamlit as st

class VisualFutbolTriple:
    def __init__(self):
        self.colores = {
            'green': '#4CAF50',
            'yellow': '#FFC107',
            'blue': '#2196F3',
            'purple': '#9C27B0',
            'red': '#f44336',
            'orange': '#FF9800'
        }
    
    def render(self, partido, idx, liga, tracker=None, 
               stats_data=None,
               analisis_heurístico=None,
               analisis_gemini=None,
               analisis_premium=None):
        
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            local = partido.get('local', 'Local')
            visitante = partido.get('visitante', 'Visitante')
            fecha = partido.get('fecha', 'Hoy')
            estadio = partido.get('estadio', 'N/A')
            
            # Encabezado
            st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #4CAF50; font-weight: bold; font-size: 20px;">⚽ {liga}</span>
                    <span style="color: #888;">{fecha}</span>
                </div>
                <h2 style="color: white; text-align: center; margin: 10px 0; font-size: 28px;">
                    {local} <span style="color: #666;">VS</span> {visitante}
                </h2>
                <p style="color: #888; text-align: center;">🏟️ {estadio}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tres columnas de análisis
            col_a1, col_a2, col_a3 = st.columns(3)
            
            # HEURÍSTICO (6 REGLAS)
            with col_a1:
                st.markdown("<h4 style='color: #FFD700;'>📊 HEURÍSTICO (6 REGLAS)</h4>", unsafe_allow_html=True)
                if analisis_heurístico:
                    color = self.colores.get(analisis_heurístico.get('color', 'gray'), '#9E9E9E')
                    st.markdown(f"**{analisis_heurístico.get('apuesta', 'N/A')}**")
                    st.markdown(f"Confianza: {analisis_heurístico.get('confianza', 0)}%")
                    if analisis_heurístico.get('regla', 0) > 0:
                        st.markdown(f"Regla: {analisis_heurístico.get('regla', 0)}")
                    st.markdown(f"<span style='color: #888;'>{analisis_heurístico.get('detalle', '')}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("Pendiente")
            
            # GEMINI IA
            with col_a2:
                st.markdown("<h4 style='color: #FFD700;'>🤖 GEMINI IA</h4>", unsafe_allow_html=True)
                if analisis_gemini:
                    color = self.colores.get(analisis_gemini.get('color', 'gray'), '#9E9E9E')
                    st.markdown(f"**{analisis_gemini.get('apuesta', 'N/A')}**")
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
            
            # Botones
            col_b1, col_b2, col_b3 = st.columns(3)
            
            with col_b1:
                analizar_key = f"analizar_{liga}_{idx}_{local}_{visitante}"
                if st.button(f"🔍 ANALIZAR", key=analizar_key):
                    return "analizar"
            
            with col_b2:
                agregar_key = f"add_{liga}_{idx}_{local}_{visitante}"
                if st.button(f"➕ AGREGAR", key=agregar_key):
                    if tracker:
                        apuesta = analisis_heurístico.get('apuesta', 'Partido') if analisis_heurístico else 'Partido'
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'liga': liga,
                            'pick': apuesta,
                            'cuota': 2.0,
                            'deporte': 'Fútbol'
                        })
                        st.success("✓ Agregado")
            
            with col_b3:
                stats_key = f"stats_{liga}_{idx}_{local}_{visitante}"
                if st.button(f"📊 ESTADÍSTICAS", key=stats_key):
                    with st.expander("📋 Últimos 5 partidos"):
                        if stats_data:
                            st.json(stats_data)
                        else:
                            st.info("No hay estadísticas disponibles")
            
            st.markdown("---")
