# modules/ranking.py
import streamlit as st

def ranking_edges(picks):
    """
    Ordena y muestra los picks con mayor ventaja (Edge) sobre la casa.
    """
    if not picks:
        return
    
    st.subheader("📊 Ranking de Ventaja (Edges)")
    # Ordenar de mayor a menor EV
    picks_ordenados = sorted(picks, key=lambda x: x['ev'], reverse=True)
    
    for i, p in enumerate(picks_ordenados, 1):
        st.write(f"{i}. **{p['game']}** — EV: {p['ev']*100:.2f}%")
