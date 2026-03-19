"""
DEBUG UEFA CODES - Prueba diferentes códigos para UEFA Conference League
"""
import streamlit as st
import requests

st.set_page_config(page_title="Debug UEFA Codes", page_icon="🔍", layout="wide")

st.title("🔍 Debug: UEFA Conference League Codes")
st.markdown("### Probando diferentes códigos para encontrar el correcto")

codigos_a_probar = [
    "uefa.conferenceleague",
    "uefa.europaconference",
    "uefa.europacconference",
    "uefa.conference",
    "uefa.ecl",
    "uefa.uecl"
]

fecha = "20260319"
base_url = "https://site.web.api.espn.com/apis/site/v2/sports/soccer"

resultados = []

for codigo in codigos_a_probar:
    url = f"{base_url}/{codigo}/scoreboard"
    with st.spinner(f"Probando {codigo}..."):
        try:
            response = requests.get(url, timeout=5)
            resultados.append({
                "código": codigo,
                "status": response.status_code,
                "url": url
            })
        except:
            resultados.append({
                "código": codigo,
                "status": "Error",
                "url": url
            })

st.subheader("📊 Resultados")
for r in resultados:
    if r["status"] == 200:
        st.success(f"✅ {r['código']} → Status 200 (FUNCIONA)")
    elif r["status"] == 404:
        st.warning(f"⚠️ {r['código']} → Status 404 (No encontrado)")
    else:
        st.error(f"❌ {r['código']} → Status {r['status']}")
