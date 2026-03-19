"""
VISUAL UFC KO - Muestra análisis de probabilidad de KO
"""
import streamlit as st

class VisualUFCKO:
    def __init__(self):
        self.colores = {
            'red': '#f44336',
            'orange': '#FF9800',
            'blue': '#2196F3',
            'green': '#4CAF50'
        }
    
    def render(self, analisis_ko, analisis_metodo, nombre1, nombre2):
        """
        Renderiza el análisis de KO
        """
        st.markdown("### 💥 ANÁLISIS DE KO PROFESIONAL")
        
        # Métrica principal
        color = self.colores.get(analisis_ko['color'], '#9E9E9E')
        
        st.markdown(f"""
        <div style="background-color: {color}20; padding: 20px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 20px;">
            <span style="color: {color}; font-weight: bold; font-size: 20px;">💥 PROBABILIDAD DE KO</span>
            <h2 style="color: white; margin: 10px 0; text-align: center;">{analisis_ko['prob_ko_general']}%</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Distribución por peleador
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🔴 {nombre1}**")
            st.metric("Probabilidad de KO", f"{analisis_ko['prob_ko_peleador1']}%")
            st.progress(analisis_ko['prob_ko_peleador1'] / 100)
            st.caption(f"KO rate histórico: {analisis_ko['ko_rate1']}%")
            st.caption(f"Eficiencia striking: {analisis_ko['striking_eff1']:.1f}")
        
        with col2:
            st.markdown(f"**🔵 {nombre2}**")
            st.metric("Probabilidad de KO", f"{analisis_ko['prob_ko_peleador2']}%")
            st.progress(analisis_ko['prob_ko_peleador2'] / 100)
            st.caption(f"KO rate histórico: {analisis_ko['ko_rate2']}%")
            st.caption(f"Eficiencia striking: {analisis_ko['striking_eff2']:.1f}")
        
        # Método de victoria
        st.markdown("### 🎯 MÉTODO DE VICTORIA MÁS PROBABLE")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.metric("KO/TKO", f"{analisis_metodo['prob_ko']}%")
        with col_m2:
            st.metric("Sumisión", f"{analisis_metodo['prob_sub']}%")
        with col_m3:
            st.metric("Decisión", f"{analisis_metodo['prob_dec']}%")
        
        st.info(f"📊 **Método más probable:** {analisis_metodo['metodo_mas_probable']} ({analisis_metodo['probabilidad']}%)")
        
        # Recomendaciones
        if analisis_ko['recomendaciones']:
            st.markdown("### 💡 RECOMENDACIONES")
            for rec in analisis_ko['recomendaciones']:
                st.markdown(f"- {rec}")
