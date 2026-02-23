import streamlit as st
from modules.ev_engine import EVEngine

engine = EVEngine()

# Estilo para tarjetas compactas
st.markdown("""
    <style>
    .compact-card {
        padding: 10px;
        border-radius: 5px;
        background-color: #1e1e1e;
        margin-bottom: 5px;
        border-left: 5px solid #00ff00;
    }
    </style>
""", unsafe_allow_html=True)

# ... (código de carga de imagen)

if st.button("🚀 Análisis Dinámico"):
    # resultado_ia = analyze_betting_image(archivo)
    picks = engine.analyze_matches(resultado_ia)
    
    for p in picks:
        with st.container():
            st.markdown(f"<div class='compact-card'><b>🏟️ {p['partido']}</b></div>", unsafe_allow_html=True)
            cols = st.columns(4)
            for i, m in enumerate(p['metrics']):
                with cols[i]:
                    # Mostrar probabilidad real detectada para CADA equipo
                    st.caption(m['label'])
                    st.markdown(f"**{m.get('val', m.get('prob'))}**")
