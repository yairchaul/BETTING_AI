"""
VISUAL NBA PROPS - Muestra análisis de triples con datos REALES
"""
import streamlit as st
import pandas as pd

class VisualNBAProps:
    """
    Renderiza análisis de triples para jugadores NBA
    """
    
    def render(self, analisis_jugadores, partido_info=None):
        """
        Muestra tabla de análisis de triples
        """
        st.markdown("## 🏀 PROPS DE TRIPLES - Jugadores Destacados")
        
        if partido_info:
            st.markdown(f"### 📍 {partido_info}")
        
        if not analisis_jugadores:
            st.info("No hay suficientes datos de jugadores para este partido")
            return
        
        # Crear DataFrame para visualización
        data = []
        valores_detectados = []
        
        for a in analisis_jugadores:
            prob = a['probabilidad']
            veces = a['veces']
            total = a['total']
            
            data.append({
                'Jugador': a['jugador'],
                'Prom. Puntos': a['promedio_puntos'],
                'Prom. Triples': a['promedio_triples'],
                'Línea': a['linea'],
                'Prob. Real': f"{prob}%",
                f'Superó {a["linea"]}': f"{veces}/{total}",
                'Multiplicador': f"x{a['multiplicador']:.2f}",
                'Recomendación': a['recomendacion']
            })
            
            if a.get('valor_detected'):
                valores_detectados.append(a)
        
        df = pd.DataFrame(data)
        
        # Aplicar colores a las recomendaciones
        def color_recomendacion(val):
            if "🔥" in val:
                return 'background-color: #4CAF50; color: white'
            elif "✅" in val:
                return 'background-color: #FF9800; color: white'
            else:
                return ''
        
        # Mostrar tabla con estilos
        st.dataframe(
            df.style.applymap(color_recomendacion, subset=['Recomendación']),
            use_container_width=True
        )
        
        # Mostrar tarjetas de valor detectado
        if valores_detectados:
            st.markdown("### 💰 VALUE DETECTED - Alta Probabilidad")
            
            cols = st.columns(min(3, len(valores_detectados)))
            for i, a in enumerate(valores_detectados[:3]):
                with cols[i]:
                    prob = a['probabilidad']
                    veces = a['veces']
                    total = a['total']
                    
                    st.markdown(f"""
                    <div style="background-color: #4CAF50; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px;">
                        <h3 style="color: white; margin: 0;">{a['jugador']}</h3>
                        <p style="color: white; font-size: 24px; margin: 5px 0;">OVER {a['linea']}</p>
                        <p style="color: white;">Probabilidad: {prob}%</p>
                        <p style="color: white;">{veces}/{total} partidos superaron</p>
                        <p style="color: white;">Rival: x{a['multiplicador']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("💰 No se detectaron valores destacados en este partido")
        
        # Mostrar historial de últimos 5 partidos
        with st.expander("📊 Ver historial simulado (últimos 5 partidos)"):
            for a in analisis_jugadores:
                if a.get('historial'):
                    prob = a['probabilidad']
                    veces = a['veces']
                    total = a['total']
                    
                    st.markdown(f"""
                    **{a['jugador']}**: {a['historial']} → Promedio triples: {a['promedio_triples']}  
                    📈 Probabilidad de OVER {a['linea']}: **{prob}%** ({veces}/{total} partidos)
                    """)
