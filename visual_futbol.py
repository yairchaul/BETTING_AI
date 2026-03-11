"""
Visual de fútbol - Con cálculo de VALUE y colores
"""
import streamlit as st
from rule_engine import RuleEngine
from stats_engine_renyi import RényiPredictor

class VisualFutbol:
    def __init__(self):
        self.predictor = RényiPredictor()
        self.rule_engine = RuleEngine()
    
    def render(self, partido, idx, tracker=None):
        """Renderiza un partido con cálculo de VALUE"""
        
        probs = self.predictor.predecir_partido_futbol(partido)
        
        with st.container():
            if idx > 0:
                st.markdown("---")
            
            # Cabecera con liga
            st.markdown(f"### 📍 {partido['local']} vs {partido['visitante']}")
            st.caption(f"🏆 {partido['liga']}")
            
            # Tres columnas con estilo oscuro
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background-color: #1A1A1A; border-left: 4px solid #FF6B35; border-radius: 5px;">
                    <h4 style="color: #FF6B35;">🏠 LOCAL</h4>
                    <h3 style="color: #FFFFFF;">{partido['local']}</h3>
                    <h2 style="color: #FF6B35;">{probs['odds_local_americano']}</h2>
                    <p style="color: #888;">({partido['odds_local']:.2f})</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background-color: #1A1A1A; border-left: 4px solid #888888; border-radius: 5px;">
                    <h4 style="color: #AAAAAA;">⚖️ EMPATE</h4>
                    <h3 style="color: #FFFFFF;">Empate</h3>
                    <h2 style="color: #AAAAAA;">{probs['odds_empate_americano']}</h2>
                    <p style="color: #888;">({partido['odds_empate']:.2f})</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background-color: #1A1A1A; border-left: 4px solid #0066CC; border-radius: 5px;">
                    <h4 style="color: #0066CC;">🚀 VISITANTE</h4>
                    <h3 style="color: #FFFFFF;">{partido['visitante']}</h3>
                    <h2 style="color: #0066CC;">{probs['odds_visit_americano']}</h2>
                    <p style="color: #888;">({partido['odds_visitante']:.2f})</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Estadísticas GF
            st.markdown(f"**📊 Goles Esperados:** {partido['local']}: {probs['gf_local']:.2f} GF | {partido['visitante']}: {probs['gf_visit']:.2f} GF")
            
            # ========================================
            # 🎯 CÁLCULO DE VALUE (EDGE)
            # ========================================
            # Probabilidad del modelo vs cuota de la casa
            prob_modelo_local = probs['prob_local']
            cuota_casa_local = partido['odds_local']
            
            # EDGE = (probabilidad_real * cuota) - 1
            edge_local = (prob_modelo_local * cuota_casa_local) - 1
            
            # Determinar color según value
            if edge_local > 0.10:
                color_value = "#00FF00"  # Verde - Excelente
                emoji = "🔥🔥🔥"
                mensaje = f"VALUE EXCEPCIONAL: {edge_local*100:.1f}%"
            elif edge_local > 0.05:
                color_value = "#FFFF00"  # Amarillo - Bueno
                emoji = "⚡⚡"
                mensaje = f"VALUE POSITIVO: {edge_local*100:.1f}%"
            elif edge_local > 0:
                color_value = "#FFA500"  # Naranja - Mínimo
                emoji = "📈"
                mensaje = f"VALUE BAJO: {edge_local*100:.1f}%"
            else:
                color_value = "#FF0000"  # Rojo - Sin valor
                emoji = "❌"
                mensaje = f"SIN VALOR: {edge_local*100:.1f}%"
            
            # Mostrar value destacado
            st.markdown(f"""
            <div style="background-color: #1A1A1A; padding: 10px; border-radius: 5px; border-left: 5px solid {color_value}; margin: 10px 0;">
                <h3 style="color: {color_value}; margin: 0;">{emoji} {mensaje}</h3>
                <p style="color: #CCCCCC;">Probabilidad modelo: {prob_modelo_local*100:.1f}% | Cuota casa: {cuota_casa_local:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mercados adicionales
            st.markdown("**📈 Mercados Adicionales:**")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Over 1.5", f"{probs['over_1_5']*100:.1f}%")
                st.metric("Over 2.5", f"{probs['over_2_5']*100:.1f}%")
                st.metric("Over 3.5", f"{probs['over_3_5']*100:.1f}%")
            with col_m2:
                st.metric("BTTS Sí", f"{probs['btts_si']*100:.1f}%")
                st.metric("BTTS No", f"{probs['btts_no']*100:.1f}%")
                st.metric("Over 1.5 1T", f"{probs['over_1_5_1t']*100:.1f}%")
            with col_m3:
                st.metric(f"Gana {partido['local']}", f"{probs['prob_local']*100:.1f}%")
                st.metric("Empate", f"{probs['prob_empate']*100:.1f}%")
                st.metric(f"Gana {partido['visitante']}", f"{probs['prob_visit']*100:.1f}%")
            
            # 7 Reglas
            recomendacion = self.rule_engine.aplicar_reglas(probs, partido)
            
            st.markdown("---")
            st.markdown("### 🎯 RECOMENDACIÓN SEGÚN 7 REGLAS")
            
            if recomendacion['value'] > 0.1:
                color = "#00FF00"
            elif recomendacion['value'] > 0:
                color = "#FFFF00"
            else:
                color = "#FF0000"
            
            st.markdown(f"""
            <div style="border-left:5px solid {color}; padding:15px; background-color:#1A1A1A; border-radius:5px;">
                <h4 style="color:#FFFFFF;">REGLA {recomendacion['regla']}: {recomendacion['descripcion']}</h4>
                <p style="color:#CCCCCC;">Probabilidad: {recomendacion['probabilidad']*100:.1f}%</p>
                <p style="color:#CCCCCC;">Cuota: {recomendacion['cuota_americana']} ({recomendacion['cuota_decimal']:.2f})</p>
                <p style="color:{color};">VALUE: {recomendacion['value']*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
