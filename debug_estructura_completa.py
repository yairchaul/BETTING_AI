"""
DEBUG ESTRUCTURA COMPLETA - Verifica que extraemos TODAS las cuotas correctamente
"""
import streamlit as st
from espn_data_pipeline import ESPNDataPipeline

st.set_page_config(page_title="Debug Extracción NBA", page_icon="🔍", layout="wide")

st.title("🔍 Debug Extracción NBA")
st.markdown("### Verificando que extraemos todas las cuotas")

espn = ESPNDataPipeline()

if st.button("🏀 CARGAR NBA Y VERIFICAR"):
    with st.spinner("Cargando datos..."):
        partidos = espn.get_nba_games_with_odds()
        
        st.success(f"✅ {len(partidos)} partidos cargados")
        
        for i, p in enumerate(partidos):
            with st.expander(f"**{p['local']} vs {p['visitante']}**", expanded=(i==0)):
                st.subheader("📋 Datos extraídos:")
                st.json(p)
                
                # Verificar moneyline
                if p['odds']['moneyline']['local'] != 'N/A':
                    st.success(f"✅ Moneyline local: {p['odds']['moneyline']['local']}")
                else:
                    st.error("❌ Moneyline local no extraída")
                
                if p['odds']['moneyline']['visitante'] != 'N/A':
                    st.success(f"✅ Moneyline visitante: {p['odds']['moneyline']['visitante']}")
                else:
                    st.error("❌ Moneyline visitante no extraída")
                
                # Verificar spread odds
                if p['odds']['spread']['local_odds'] != 'N/A':
                    st.success(f"✅ Spread odds local: {p['odds']['spread']['local_odds']}")
                else:
                    st.error("❌ Spread odds local no extraída")
                
                if p['odds']['spread']['visitante_odds'] != 'N/A':
                    st.success(f"✅ Spread odds visitante: {p['odds']['spread']['visitante_odds']}")
                else:
                    st.error("❌ Spread odds visitante no extraída")
                
                # Verificar totales odds
                if p['odds']['totales']['over_odds'] != 'N/A':
                    st.success(f"✅ Over odds: {p['odds']['totales']['over_odds']}")
                else:
                    st.error("❌ Over odds no extraída")
                
                if p['odds']['totales']['under_odds'] != 'N/A':
                    st.success(f"✅ Under odds: {p['odds']['totales']['under_odds']}")
                else:
                    st.error("❌ Under odds no extraída")
