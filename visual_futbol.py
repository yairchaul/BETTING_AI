import streamlit as st
import pandas as pd

class VisualFutbol:
    def render(self, evento, idx, tracker):
        """Renderiza fútbol con el formato que funcionaba"""
        with st.expander(f"**⚽ {evento.local} vs {evento.visitante}**", expanded=(idx == 0)):
            # Mostrar odds en 3 columnas (formato original)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label=f"�� **{evento.local}**",
                    value=evento.odds.get('local', 'N/A'),
                    delta=evento.odds.get('local_dec', '')
                )
            with col2:
                st.metric(
                    label="⚖️ **Empate**",
                    value=evento.odds.get('draw', 'N/A'),
                    delta=evento.odds.get('draw_dec', '')
                )
            with col3:
                st.metric(
                    label=f"🚀 **{evento.visitante}**",
                    value=evento.odds.get('visitante', 'N/A'),
                    delta=evento.odds.get('visitante_dec', '')
                )
            
            # GF estimados
            st.caption(f"📊 {evento.local}: {evento.stats.get('local_gf', 1.5):.2f} GF | {evento.visitante}: {evento.stats.get('visitante_gf', 1.3):.2f} GF")
            
            # Mercados adicionales (3 columnas)
            if evento.mercados:
                st.markdown("**📈 Mercados Adicionales:**")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("Over 1.5", f"{evento.mercados.get('over_1_5', 0):.1%}")
                with col_m2:
                    st.metric("BTTS Sí", f"{evento.mercados.get('btts_yes', 0):.1%}")
                with col_m3:
                    st.metric("Gana Local", f"{evento.mercados.get('prob_local', 0):.1%}")
                
                col_n1, col_n2, col_n3 = st.columns(3)
                with col_n1:
                    st.metric("Over 2.5", f"{evento.mercados.get('over_2_5', 0):.1%}")
                with col_n2:
                    st.metric("BTTS No", f"{evento.mercados.get('btts_no', 0):.1%}")
                with col_n3:
                    st.metric("Empate", f"{evento.mercados.get('prob_draw', 0):.1%}")
                
                col_o1, col_o2, col_o3 = st.columns(3)
                with col_o1:
                    st.metric("Over 3.5", f"{evento.mercados.get('over_3_5', 0):.1%}")
                with col_o2:
                    st.metric("Over 1.5 1T", f"{evento.mercados.get('over_1_5_1t', 0):.1%}")
                with col_o3:
                    st.metric("Gana Visitante", f"{evento.mercados.get('prob_visitante', 0):.1%}")
            
            # Picks según reglas
            from rule_engine import RuleEngine
            rule_engine = RuleEngine()
            picks = rule_engine.ejecutar(evento)
            
            if picks:
                st.markdown("**🎯 Picks según reglas:**")
                for pick in picks:
                    st.info(f"Nivel {pick['nivel']}: **{pick['mercado']}** ({pick['prob']:.1%})")
                    if st.button(f"➕ Agregar", key=f"add_futbol_{idx}_{pick['nivel']}"):
                        tracker.add_pick(
                            f"{evento.local} vs {evento.visitante}",
                            pick['mercado'],
                            pick['prob'],
                            pick['nivel'],
                            evento.deporte
                        )
                        st.rerun()
            else:
                st.warning("No se generaron picks para este evento")
