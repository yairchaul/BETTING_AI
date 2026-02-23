# app.py - Dashboard con Mejor Parlay
# ... (imports y sidebar mismo)

individual_picks, best_parlay = engine.analyze_matches()

if not individual_picks:
    st.warning("No mercados.")
else:
    tab1, tab2, tab3 = st.tabs(["Sencillos", "Parlay Manual", "Mejor Parlay"])

    with tab1:
        # ... (mismo que antes)

    with tab2:
        # ... (parlay manual como antes)

    with tab3:
        if best_parlay:
            st.subheader(f"Mejor Parlay ({len(best_parlay['legs'])}) @ +{best_parlay['odds']} (Prob: {best_parlay['prob']*100:.1f}%)")
            for leg in best_parlay['legs']:
                st.markdown(f"- {leg['type']} ({leg['line']}) - {leg['player'] or leg['team']} (Odds: {leg['odds']})")
            stake = st.number_input("Stake para Mejor Parlay ($)", value=0.0)
            if stake > 0:
                decimal = (best_parlay['odds'] / 100 + 1) if best_parlay['odds'] > 0 else (100 / abs(best_parlay['odds']) + 1)
                payout = stake * decimal
                st.success(f"¡Apuesta de ${stake:.2f} paga ${payout:,.2f}! (EV medio: {best_parlay['ev']:.2f})")
                st.info(f"Conveniencia: Alta prob chain ({best_parlay['prob']:.2f}), pero riesgo multiplica losses. Apostar si prob > breakeven {1 / decimal:.2f}.")
            log_pick(best_parlay, best_parlay['prob'])  # Track
        else:
            st.info("No parlay viable con alta prob.")
