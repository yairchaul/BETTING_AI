# ... después de llamar al engine de análisis ...
st.subheader("📊 Análisis Probabilístico")
for p in todos:
    confianza = p['probabilidad']
    
    # Lógica de colores según éxito estadístico
    if confianza >= 75: color, emo = "#28a745", "🔥" # Verde
    elif confianza >= 55: color, emo = "#ffc107", "⚖️" # Naranja
    else: color, emo = "#dc3545", "⚠️" # Rojo

    st.markdown(f"""
        <div style="border-left: 5px solid {color}; padding: 10px; margin: 5px; background-color: #1e1e1e; border-radius: 5px;">
            <span style="font-size: 18px;">{emo}</span> 
            <b>{p['partido']}</b> | Sugerencia: <span style="color:{color};">{p['pick']}</span> 
            (Confianza: {confianza}%)
        </div>
    """, unsafe_allow_html=True)

