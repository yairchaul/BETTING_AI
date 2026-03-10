import streamlit as st

class UFCProcessor:
    def process(self, lines):
        """Procesa líneas de UFC y estructura peleas"""
        peleas = []
        for line in lines:
            # Aquí la lógica: divide la línea a la mitad
            mid = len(line) // 2
            if mid >= 2:
                peleas.append({
                    "peleador_1": " ".join(line[:mid-1]),
                    "cuota_1": line[mid-1],
                    "peleador_2": " ".join(line[mid:-1]),
                    "cuota_2": line[-1]
                })
        return peleas
        
    def render(self, peleas):
        """Muestra las peleas en la interfaz"""
        if not peleas:
            st.error("❌ No se detectaron peleas")
            return
        
        st.success(f"✅ {len(peleas)} peleas detectadas")
        for i, p in enumerate(peleas):
            with st.expander(f"**🥊 {p['peleador_1']} vs {p['peleador_2']}**", expanded=(i == 0)):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Peleador 1", p['peleador_1'], p['cuota_1'])
                with col2:
                    st.metric("Peleador 2", p['peleador_2'], p['cuota_2'])
