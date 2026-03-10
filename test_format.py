import streamlit as st

st.title('Prueba de formato')

# Datos de prueba
partido = {
    'visitante': 'Liverpool',
    'odds': {'visitante': '-139'}
}

# Formato correcto
st.metric(
    label=f"🚀 **{partido['visitante']}**",
    value=f"{partido['odds']['visitante']}",
    delta="1.72"
)

st.success('Si ves "Liverpool" en el label y "-139" en el value, está correcto')
