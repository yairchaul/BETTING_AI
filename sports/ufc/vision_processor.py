import streamlit as st
import pandas as pd

class UFCVisionProcessor:
    def process_ufc(self, raw_lines):
        """Procesa líneas de UFC y estructura peleas"""
        peleas = []
        for line in raw_lines:
            # Si la línea tiene al menos 4 elementos (2 nombres + 2 cuotas)
            if len(line) >= 4:
                # Buscamos el punto medio de la línea para separar oponentes
                mid = len(line) // 2
                peleas.append({
                    'p1': " ".join(line[:mid-1]),
                    'c1': line[mid-1],
                    'p2': " ".join(line[mid:-1]),
                    'c2': line[-1]
                })
        return peleas

    def render_ufc_fights(self, peleas):
        if not peleas:
            st.error("❌ No se detectaron peleas")
            return
        
        st.success(f"✅ {len(peleas)} peleas detectadas")
        for i, p in enumerate(peleas):
            with st.expander(f"**🥊 {p['p1']} vs {p['p2']}**", expanded=(i == 0)):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Peleador", p['p1'], p['c1'])
                with col2:
                    st.metric("Peleador", p['p2'], p['c2'])
