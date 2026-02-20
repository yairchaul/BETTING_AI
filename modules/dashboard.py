import streamlit as st
import ev_engine
import connector

# --- CONFIGURACIÓN DE INTERFAZ ---
st.title("🏀 NBA ELITE PARLAY BUILDER")

if st.button("🔥 GENERAR PARLAY DE 3 PARTIDOS"):
    datos = connector.obtener_datos_caliente_limpios()
    pool_excelentes = []

    for p in datos:
        analisis = ev_engine.analizar_profundidad(p['home'], p['away'], p['linea'])
        
        # Categorización visual original
        if analisis['prob'] >= 0.70:
            status, color = "🔥 EXCELENTE", "#00FF00"
            pool_excelentes.append({"pick": f"{analisis['seleccion']}", "game": f"{p['away']} @ {p['home']}"})
        elif analisis['prob'] >= 0.60:
            status, color = "⚡ BUENA", "#FFFF00"
        else:
            status, color = "⚠️ BAJA", "#FF4B4B"

        # Mostrar el análisis en tiempo real como en la v3.0
        with st.expander(f"🔍 Analizando {p['away']} vs {p['home']}"):
            st.write(analisis['nota'])
            st.markdown(f"<p style='color:{color}'>{status} - Probabilidad: {analisis['prob']*100}%</p>", unsafe_allow_html=True)

    # --- ARMADO DEL PARLAY ---
    if len(pool_excelentes) >= 3:
        st.success("🚀 PARLAY ÉLITE DETECTADO")
        parlay_picks = pool_excelentes[:3]
        
        # Diseño de Ticket sugerido
        st.markdown(f"""
        <div style="background-color:#1e1e1e; border: 2px gold solid; border-radius:15px; padding:20px">
            <h2 style="text-align:center; color:gold">🎫 TICKET SUGERIDO (3-WAY)</h2>
            <hr>
            <p>1. {parlay_picks[0]['game']} -> <b>{parlay_picks[0]['pick']}</b></p>
            <p>2. {parlay_picks[1]['game']} -> <b>{parlay_picks[1]['pick']}</b></p>
            <p>3. {parlay_picks[2]['game']} -> <b>{parlay_picks[2]['pick']}</b></p>
            <h3 style="text-align:right; color:#00FF00">Inversión sugerida: $100 MXN</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Buscando más partidos... Necesitamos 3 picks 'Excelente' para el Parlay.")





