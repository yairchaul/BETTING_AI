# En main.py - sección de carga de ticket
st.subheader("Analizar ticket (sube imagen o pega texto)")
col1, col2 = st.columns(2)

with col1:
    archivo = st.file_uploader("Sube captura del ticket", type=["png", "jpg", "jpeg"])

with col2:
    texto_manual = st.text_area("O pega el texto del ticket aquí", height=150)

if archivo or texto_manual:
    matches, mensaje = analizar_ticket(archivo=archivo, texto_manual=texto_manual)
    st.write(mensaje)
    
    if matches:
        for partido in matches:
            resultado = engine.analizar_partido(partido)  # tu ev_engine
            if resultado:
                st.markdown(f"""
                <div class="card">
                    <h3>{resultado['home']} vs {resultado['away']}</h3>
                    <p><strong>Mejor opción:</strong> {resultado['mejor_pick']}</p>
                    <p>Probabilidad: {resultado['prob']}% | EV: {resultado['ev']}</p>
                    <small>λ Home: {resultado['λ_home']} | λ Away: {resultado['λ_away']} | Edge: {resultado['edge']}%</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No se detectaron partidos válidos.")

