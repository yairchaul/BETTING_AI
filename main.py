import streamlit as st
from modules.vision_reader import analyze_betting_image
from modules.ev_engine import EVEngine

st.set_page_config(page_title="Ticket Pro IA", layout="wide")
engine = EVEngine()

# CSS para diseño ultra-compacto
st.markdown("<style> .stMetric { background: #1e1e1e; padding: 5px; border-radius: 5px;} </style>", unsafe_allow_html=True)

st.title("🏆 Generador de Parlay Dinámico")

archivo = st.file_uploader("Sube tu captura de Caliente", type=['png', 'jpg', 'jpeg'])

if archivo:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(archivo, width=250) # Imagen pequeña, no desplaza hacia abajo
    
    with col2:
        if st.button("🚀 ANALIZAR ÚLTIMOS 5 Y CREAR PARLAY", use_container_width=True):
            datos = analyze_betting_image(archivo)
            todos, parlay = engine.analyze_matches(datos)
            
            if parlay:
                st.success("🔥 MEJOR PARLAY DETECTADO")
                # Mostrar el Parlay en una caja destacada
                with st.container(border=True):
                    for p in parlay:
                        st.write(f"✅ **{p['partido']}** ➔ `{p['pick']}` ({int(p['prob']*100)}%)")
                
                # Detalle compacto de todos los juegos
                with st.expander("Ver análisis individual (Cascada)"):
                    for j in todos:
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.write(f"🏟️ {j['partido']}")
                        c2.metric("Win", j['victoria']['val'])
                        c3.metric("HT Goles", j['ht']['val'])


