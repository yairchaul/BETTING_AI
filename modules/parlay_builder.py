import streamlit as st
from itertools import combinations

def build_parlay(picks):
    """Construye un parlay a partir de picks"""
    if len(picks) < 2:
        return None
    
    total_prob = 1.0
    for p in picks:
        total_prob *= p['prob']
    
    # Cuota estimada (inversa de probabilidad con margen)
    total_odds = 1.0
    for p in picks:
        total_odds *= (1 / p['prob']) * 0.95
    
    ev = (total_prob * total_odds) - 1
    
    return {
        'picks': picks,
        'total_prob': total_prob,
        'total_odds': round(total_odds, 2),
        'ev': round(ev, 4)
    }

def show_parlay_options(all_picks):
    """Muestra interfaz de parlays"""
    st.divider()
    st.subheader("🎯 Parlays Recomendados")
    
    # Mostrar picks disponibles
    st.markdown("**Selecciones disponibles:**")
    cols = st.columns(3)
    for i, pick in enumerate(all_picks[:6]):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{pick['match']}**")
                st.markdown(f"📌 {pick['selection']}")
                st.metric("Probabilidad", f"{pick['prob']:.1%}")
    
    if st.button("🔄 Generar combinaciones"):
        parlays = []
        for combo in combinations(all_picks, 2):
            parlay = build_parlay(list(combo))
            if parlay and parlay['ev'] > 0:
                parlays.append(parlay)
        
        if parlays:
            st.markdown("**Top parlays encontrados:**")
            for i, p in enumerate(parlays[:5]):
                with st.container(border=True):
                    st.markdown(f"**Parlay #{i+1}**")
                    st.markdown(f"Cuota: {p['total_odds']} | Prob: {p['total_prob']:.1%} | EV: {p['ev']:.2%}")
                    for pick in p['picks']:
                        st.markdown(f"• {pick['match']}: {pick['selection']}")
        else:
            st.info("No se encontraron parlays con EV positivo")
