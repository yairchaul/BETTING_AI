from modules.connector import get_real_time_odds

# ... (después de que la IA detecta los juegos)
if datos_ia and "juegos" in datos_ia:
    st.markdown("### 📈 Análisis de Valor en Tiempo Real")
    
    # 1. Obtenemos los momios reales del mercado (The Odds API)
    market_data = get_real_time_odds()
    
    for j in datos_ia["juegos"]:
        # 2. Buscamos el "Match" entre la foto y la API
        equipo_foto = j.get('away')
        odds_real = None
        
        if market_data:
            # Lógica simple de búsqueda por nombre
            match = next((item for item in market_data if equipo_foto in item['away_team']), None)
            if match:
                # Extraemos el momio promedio del mercado para comparar
                # (Aquí es donde ocurre la magia del +EV)
                odds_real = match['bookmakers'][0]['markets'][0]['outcomes']

        # 3. Visualización de la comparativa
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"**{j.get('away')} vs {j.get('home')}**")
            
            # Mostramos el momio de la captura
            momio_captura = j.get('moneyline')
            col2.metric("Momio Foto", momio_captura)
            
            # Si hay datos de API, comparamos
            if odds_real:
                # Supongamos que buscamos el momio del equipo visitante
                api_val = next((o['price'] for o in odds_real if o['name'] == equipo_foto), "N/A")
                
                # Cálculo de diferencia
                delta = int(momio_captura) - int(api_val) if api_val != "N/A" else 0
                col3.metric("Mercado Real", api_val, delta=f"{delta} pts")
                
                if delta > 10: # Si Caliente paga mucho más que el promedio
                    st.success("🔥 ¡OPORTUNIDAD +EV DETECTADA!")
