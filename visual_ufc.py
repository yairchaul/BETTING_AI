import streamlit as st

class VisualUFC:
    def render(self, evento, idx, tracker):
        """Renderiza UFC con formato de peleas"""
        with st.expander(f"**🥊 {evento.local} vs {evento.visitante}**", expanded=(idx == 0)):
            col1, col2 = st.columns(2)
            with col1:
                st.metric(evento.local, evento.odds.get('local', 'N/A'))
            with col2:
                st.metric(evento.visitante, evento.odds.get('visitante', 'N/A'))
            
            if evento.mercados:
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("Gana Local", f"{evento.mercados.get('prob_local', 0):.1%}")
                with col_m2:
                    st.metric("KO/TKO", f"{evento.mercados.get('ko_tko', 0):.1%}")
                with col_m3:
                    st.metric("Sumisión", f"{evento.mercados.get('submission', 0):.1%}")
