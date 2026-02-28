import streamlit as st
from modules.cerebro import buscar_posibles_equipos, obtener_forma_reciente, obtener_mejor_apuesta

st.set_page_config(page_title="Buscador de Equipos Pro", layout="wide")

st.title("🎯 Selector Inteligente de Equipos")
st.info("Escribe el nombre del equipo y selecciónalo del menú desplegable para analizar.")

col1, col2 = st.columns(2)

# --- SELECCIÓN DE EQUIPO LOCAL ---
with col1:
    st.subheader("🏠 Equipo Local")
    search_h = st.text_input("Buscar Local...", key="sh", placeholder="Ej: Monchen")
    opciones_h = buscar_posibles_equipos(search_h)
    
    equipo_h = None
    if opciones_h:
        equipo_h = st.selectbox("Selecciona el equipo exacto:", opciones_h, format_func=lambda x: x['display'], key="sbh")
        st.image(equipo_h['logo'], width=60)
    elif search_h:
        st.warning("No se encontraron resultados. Intenta con otra palabra.")

# --- SELECCIÓN DE EQUIPO VISITANTE ---
with col2:
    st.subheader("🚀 Equipo Visitante")
    search_a = st.text_input("Buscar Visitante...", key="sa", placeholder="Ej: Union Ber")
    opciones_a = buscar_posibles_equipos(search_a)
    
    equipo_a = None
    if opciones_a:
        equipo_a = st.selectbox("Selecciona el equipo exacto:", opciones_a, format_func=lambda x: x['display'], key="sba")
        st.image(equipo_a['logo'], width=60)
    elif search_a:
        st.warning("No se encontraron resultados.")

# --- BOTÓN DE ANÁLISIS ---
st.divider()
if equipo_h and equipo_a:
    if st.button("🔥 ANALIZAR PARTIDO"):
        with st.spinner("Calculando probabilidades con datos reales..."):
            sh = obtener_forma_reciente(equipo_h['id'])
            sa = obtener_forma_reciente(equipo_a['id'])
            pick = obtener_mejor_apuesta(sh, sa)
            
            st.balloons()
            
            # Mostrar Resultado Final
            st.markdown(f"""
            <div style="background-color: #0d1117; padding: 25px; border-radius: 15px; border: 2px solid #4cd964; text-align: center;">
                <h2 style="color: white;">{equipo_h['name']} vs {equipo_a['name']}</h2>
                <h3 style="color: #4cd964;">Sugerencia: {pick['selection']}</h3>
                <p style="font-size: 1.2em; color: #8b949e;">Probabilidad de éxito: <b>{round(pick['probability']*100, 1)}%</b></p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.write("Selecciona ambos equipos para desbloquear el análisis.")
