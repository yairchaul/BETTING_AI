# pages/3_Backtesting.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from modules.backtester import Backtester
from modules.betting_tracker import BettingTracker

st.set_page_config(page_title="Backtesting de Estrategias", layout="wide")

st.title("📊 Backtesting y Validación de Estrategias")
st.markdown("""
Esta herramienta permite validar si las recomendaciones del sistema hubieran sido rentables en el pasado.
""")

# Inicializar
if 'backtester' not in st.session_state:
    st.session_state.backtester = Backtester(initial_bankroll=1000)
if 'tracker' not in st.session_state:
    st.session_state.tracker = BettingTracker()

tab1, tab2, tab3 = st.tabs(["📈 Backtesting", "🎲 Simulación Monte Carlo", "⚖️ Comparar Estrategias"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Configuración")
        
        # Opción 1: Usar historial real del tracker
        use_tracker = st.checkbox("Usar historial real de apuestas", value=True)
        
        if use_tracker:
            if st.session_state.tracker.get_stats()['total_bets'] > 0:
                bets_data = []
                for bet in st.session_state.tracker.bets:
                    if bet['status'] == 'Resuelta':
                        bets_data.append({
                            'date': bet['date'][:10],
                            'match': bet['selections'][0][:50] if bet['selections'] else 'Desconocido',
                            'bet': bet['selections'][0] if bet['selections'] else 'Desconocida',
                            'odds': bet['total_odds'],
                            'stake': bet['stake'],
                            'result': 'win' if bet['result'] == 'Ganada' else 'loss'
                        })
                
                st.info(f"📊 Usando {len(bets_data)} apuestas del historial")
                
                if st.button("🚀 Ejecutar Backtesting"):
                    with st.spinner("Ejecutando backtesting..."):
                        results = st.session_state.backtester.run_backtest(bets_data)
                        st.session_state.backtest_results = results
            else:
                st.warning("No hay apuestas en el historial. Usa datos simulados.")
                use_tracker = False
        
        if not use_tracker:
            st.subheader("Datos simulados")
            num_bets = st.slider("Número de apuestas a simular", 50, 1000, 200)
            win_rate = st.slider("Win Rate esperado %", 30.0, 80.0, 55.0, 1.0)
            avg_odds = st.slider("Odds promedio", 1.5, 5.0, 2.2, 0.1)
            
            if st.button("🎲 Generar y Backtestear"):
                with st.spinner("Generando datos simulados..."):
                    np.random.seed(42)
                    simulated = []
                    for i in range(num_bets):
                        result = 'win' if np.random.random() < (win_rate/100) else 'loss'
                        simulated.append({
                            'date': (pd.Timestamp.now() - pd.Timedelta(days=num_bets-i)).strftime('%Y-%m-%d'),
                            'match': f'Partido Simulado {i+1}',
                            'bet': 'Apuesta de prueba',
                            'odds': avg_odds + np.random.normal(0, 0.1),
                            'stake': 50,
                            'result': result
                        })
                    results = st.session_state.backtester.run_backtest(simulated)
                    st.session_state.backtest_results = results
    
    with col2:
        if 'backtest_results' in st.session_state:
            results = st.session_state.backtest_results
            metrics = results['metrics']
            
            st.subheader("📊 Resultados del Backtesting")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("ROI %", f"{metrics.get('roi', 0):.2f}%")
            with col_m2:
                st.metric("Win Rate %", f"{metrics.get('win_rate', 0):.2f}%")
            with col_m3:
                st.metric("Profit Total", f"${results['total_profit']:.2f}")
            with col_m4:
                st.metric("Bankroll Final", f"${results['bankroll_final']:.2f}")
            
            # Gráfico de evolución
            df_results = pd.DataFrame(results['results'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_results['date'],
                y=df_results['bankroll'],
                mode='lines+markers',
                name='Bankroll',
                line=dict(color='#4CAF50', width=3),
                marker=dict(
                    color=['green' if r == 'GANADA' else 'red' for r in df_results['result']],
                    size=8
                )
            ))
            fig.add_hline(y=1000, line_dash="dash", line_color="gray", annotation_text="Bankroll Inicial")
            fig.update_layout(
                title="Evolución del Bankroll",
                xaxis_title="Fecha",
                yaxis_title="Bankroll ($)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_results[['date', 'match', 'bet', 'odds', 'result', 'profit', 'bankroll']].tail(10))

with tab2:
    st.subheader("🎲 Simulación Monte Carlo")
    
    col_mc1, col_mc2 = st.columns([1, 1])
    
    with col_mc1:
        win_rate_mc = st.slider("Win Rate %", 30.0, 80.0, 55.0, 1.0, key="mc_win")
        odds_mc = st.slider("Odds promedio", 1.5, 5.0, 2.2, 0.1, key="mc_odds")
        simulations_mc = st.slider("Número de simulaciones", 1000, 50000, 10000, 1000)
        bets_mc = st.slider("Apuestas por simulación", 100, 5000, 1000, 100)
        
        if st.button("🎲 Ejecutar Simulación"):
            with st.spinner(f"Ejecutando {simulations_mc} simulaciones..."):
                mc_results = st.session_state.backtester.monte_carlo_simulation(
                    win_rate=win_rate_mc/100,
                    avg_odds=odds_mc,
                    simulations=simulations_mc,
                    bets_per_sim=bets_mc
                )
                st.session_state.mc_results = mc_results
    
    with col_mc2:
        if 'mc_results' in st.session_state:
            mc = st.session_state.mc_results
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.metric("Bankroll Promedio", f"${mc['mean_final']:.2f}")
                st.metric("Mediana", f"${mc['median_final']:.2f}")
                st.metric("Percentil 5%", f"${mc['percentile_5']:.2f}")
            with col_r2:
                st.metric("Desviación Estándar", f"${mc['std_final']:.2f}")
                st.metric("Percentil 95%", f"${mc['percentile_95']:.2f}")
                st.metric("Probabilidad Ruina", f"{mc['prob_ruin']:.2f}%")

with tab3:
    st.subheader("⚖️ Comparación de Estrategias")
    
    if st.button("Generar Comparación de Ejemplo"):
        strategies = {
            'Solo Overs': {'roi': 8.5, 'win_rate': 58.2, 'profit': 425, 'sharpe': 1.2, 'drawdown': 15.3},
            'Solo Favoritos': {'roi': 5.2, 'win_rate': 72.1, 'profit': 260, 'sharpe': 0.9, 'drawdown': 8.7},
            'Mixta (Reglas)': {'roi': 12.3, 'win_rate': 63.5, 'profit': 615, 'sharpe': 1.8, 'drawdown': 12.1},
            'ML Predictivo': {'roi': 15.7, 'win_rate': 61.2, 'profit': 785, 'sharpe': 2.1, 'drawdown': 10.5}
        }
        
        df_comp = pd.DataFrame([
            {'Estrategia': k, 'ROI %': v['roi'], 'Win Rate %': v['win_rate'], 
             'Profit $': v['profit'], 'Sharpe': v['sharpe'], 'Drawdown %': v['drawdown']}
            for k, v in strategies.items()
        ]).sort_values('Sharpe', ascending=False)
        
        st.dataframe(df_comp, use_container_width=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_comp['Estrategia'],
            y=df_comp['Sharpe'],
            name='Sharpe Ratio',
            marker_color='#2196F3'
        ))
        fig.update_layout(title="Comparación por Sharpe Ratio", height=400)
        st.plotly_chart(fig, use_container_width=True)
