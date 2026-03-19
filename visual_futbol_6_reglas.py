"""
VISUAL FÚTBOL 6 REGLAS - Interfaz premium con análisis
"""
import streamlit as st

class VisualFutbol6Reglas:
    def __init__(self):
        self.colores = {
            'green': '#4CAF50',
            'yellow': '#FFC107',
            'blue': '#2196F3',
            'purple': '#9C27B0',
            'red': '#f44336'
        }
    
    def render(self, partido, idx, tracker=None, stats_data=None, analisis=None):
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            liga = partido.get('liga', 'Liga')
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
            
            # Mostrar análisis si existe
            if analisis:
                color = self.colores.get(analisis.get('color', 'gray'), '#9E9E9E')
                
                st.markdown(f"""
                <div style="background-color: {color}20; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; margin: 20px 0;">
                    <span style="color: {color}; font-weight: bold; font-size: 24px;">🎯 RECOMENDACIÓN</span>
                    <h3 style="color: white; margin: 10px 0;">{analisis.get('apuesta', 'N/A')}</h3>
                    <p style="color: #888;">Confianza: {analisis.get('confianza', 0)}% | Regla {analisis.get('regla', 0)}</p>
                    <p style="color: #888;">{analisis.get('detalle', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar probabilidades
                st.markdown("### 📊 Probabilidades")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Over 1.5 HT", f"{self._get_prob(analisis, 'ht')}%")
                with col2:
                    st.metric("Over 2.5", f"{self._get_prob(analisis, 'over25')}%")
                with col3:
                    st.metric("BTTS", f"{self._get_prob(analisis, 'btts')}%")
            
            # Botones
            col_b1, col_b2, col_b3 = st.columns(3)
            
            with col_b1:
                if st.button(f"🔍 ANALIZAR", key=f"analizar_fut_{idx}"):
                    return "analizar"
            
            with col_b2:
                if st.button(f"➕ AGREGAR", key=f"add_fut_{idx}"):
                    if tracker:
                        tracker.agregar_pick({
                            'partido': f"{local} vs {visitante}",
                            'liga': liga,
                            'pick': analisis.get('apuesta', 'Partido') if analisis else 'Partido',
                            'cuota': 2.0,
                            'deporte': 'Fútbol'
                        })
                        st.success("✓ Agregado")
            
            with col_b3:
                if st.button(f"📊 ESTADÍSTICAS", key=f"stats_fut_{idx}"):
                    with st.expander("📋 Últimos 5 partidos"):
                        if stats_data:
                            st.json(stats_data)
                        else:
                            st.info("No hay estadísticas disponibles")
            
            st.markdown("---")
    
    def _get_prob(self, analisis, key):
        """Obtiene probabilidad específica del análisis"""
        # Placeholder - en producción vendría del analizador
        return 50
