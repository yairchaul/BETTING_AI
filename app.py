st.subheader("📸 Subir Screenshot Caliente")

uploaded = st.file_uploader(
    "Sube captura de apuestas",
    type=["png", "jpg", "jpeg"]
)

if uploaded:

    st.image(uploaded, use_container_width=True)

    with st.spinner("Gemini Vision analizando líneas..."):

        games = analyze_betting_image(uploaded)

    if games:
        st.success(f"{len(games)} juegos detectados")

        for g in games:
            st.json(g)

    else:
        st.warning("No se pudieron detectar juegos")
