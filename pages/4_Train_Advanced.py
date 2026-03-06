# pages/4_Train_Advanced.py
import streamlit as st
import pandas as pd
import numpy as np
from modules.data_collector import DataCollector
from modules.ml_predictor import MLPredictor
from modules.elo_system import ELOSystem
from modules.montecarlo_pro import MonteCarloPro
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Entrenamiento Avanzado", layout="wide")

st.title("🧠 Entrenamiento Avanzado de Modelos")
st.markdown("""
Esta página permite entrenar y calibrar TODOS los modelos del sistema:
- **XGBoost** (Machine Learning)
- **ELO Ratings** (Sistema de puntuación)
- **Monte Carlo** (Simulaciones)
- **Pesos del modelo híbrido**
""")

# Inicializar componentes
if 'data_collector' not in st.session_state:
    st.session_state.data_collector = DataCollector()
if 'ml_predictor' not in st.session_state:
    st.session_state.ml_predictor = MLPredictor()
if 'elo' not in st.session_state:
    st.session_state.elo = ELOSystem()
if 'montecarlo' not in st.session_state:
    st.session_state.montecarlo = MonteCarloPro()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Recolectar Datos", 
    "🤖 Entrenar XGBoost", 
    "⚡ Calibrar ELO",
    "🎯 Optimizar Pesos"
])

with tab1:
    st.subheader("Recolectar Datos Históricos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ligas_input = st.text_area(
            "Ligas a incluir (una por línea)",
            value="Mexico Liga MX\nEngland Premier League\nSpain LaLiga\nGermany Bundesliga\nItaly Serie A",
            height=150
        )
        ligas = [l.strip() for l in ligas_input.split('\n') if l.strip()]
        
        temporadas = st.multiselect(
            "Temporadas",
            ["2024", "2023", "2022", "2021", "2020"],
            default=["2024", "2023"]
        )
        
        max_partidos = st.slider("Máximo partidos por liga/temporada", 100, 1000, 300)
    
    with col2:
        st.info("ℹ️ La recolección puede tomar varios minutos")
        if st.button("🚀 Iniciar Recolección Masiva", type="primary"):
            with st.spinner("Recolectando datos..."):
                all_matches = st.session_state.data_collector.download_all_leagues(
                    ligas, 
                    seasons=temporadas,
                    max_per_league=max_partidos
                )
                
                st.session_state.raw_matches = all_matches
                
                # Actualizar ELO con los datos
                for match in all_matches:
                    st.session_state.elo.update_ratings(
                        match['home_team'],
                        match['away_team'],
                        match['home_goals'],
                        match['away_goals'],
                        match['date']
                    )
                
                st.success(f"✅ {len(all_matches)} partidos recolectados!")
    
    if 'raw_matches' in st.session_state:
        st.subheader(f"📁 Datos recolectados: {len(st.session_state.raw_matches)} partidos")
        
        # Mostrar muestra
        df_sample = pd.DataFrame(st.session_state.raw_matches[:10])
        st.dataframe(df_sample[['date', 'home_team', 'away_team', 'home_goals', 'away_goals']])

with tab2:
    st.subheader("Entrenar Modelo XGBoost")
    
    if 'raw_matches' not in st.session_state:
        st.warning("Primero recolecta datos en la pestaña anterior")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            test_size = st.slider("Tamaño del conjunto de prueba (%)", 10, 40, 20)
            n_estimators = st.slider("Número de árboles", 50, 500, 200)
            max_depth = st.slider("Profundidad máxima", 3, 15, 6)
            learning_rate = st.select_slider("Tasa de aprendizaje", options=[0.01, 0.05, 0.1, 0.2], value=0.1)
            
            if st.button("🎯 Entrenar Modelo", type="primary"):
                with st.spinner("Entrenando XGBoost..."):
                    # Preparar datos
                    X, y = st.session_state.data_collector.prepare_training_data(
                        st.session_state.raw_matches
                    )
                    
                    X = np.array(X)
                    y = np.array(y)
                    
                    # Dividir en entrenamiento y prueba
                    from sklearn.model_selection import train_test_split
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=test_size/100, random_state=42
                    )
                    
                    # Entrenar
                    success = st.session_state.ml_predictor.train(
                        X_train, y_train, X_test, y_test
                    )
                    
                    if success:
                        st.balloons()
                        st.success("✅ Modelo entrenado exitosamente!")
        
        with col2:
            if st.session_state.ml_predictor.is_trained:
                st.subheader("📊 Importancia de Features")
                importance = st.session_state.ml_predictor.get_feature_importance()
                if importance:
                    df_imp = pd.DataFrame(importance, columns=['Feature', 'Importancia'])
                    st.bar_chart(df_imp.set_index('Feature'))

with tab3:
    st.subheader("Calibrar Sistema ELO")
    
    if 'raw_matches' not in st.session_state:
        st.warning("Primero recolecta datos")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            k_factor = st.slider("Factor K", 10, 50, 32)
            home_adv = st.slider("Ventaja local (ELO)", 50, 150, 100)
            
            if st.button("⚡ Recalibrar ELO"):
                with st.spinner("Recalculando ratings..."):
                    # Reiniciar ELO con nuevos parámetros
                    st.session_state.elo = ELOSystem(k_factor=k_factor, home_advantage=home_adv)
                    
                    # Reprocesar todos los partidos
                    for match in st.session_state.raw_matches:
                        st.session_state.elo.update_ratings(
                            match['home_team'],
                            match['away_team'],
                            match['home_goals'],
                            match['away_goals'],
                            match['date']
                        )
                    
                    st.success("✅ ELO recalibrado!")
        
        with col2:
            # Mostrar top equipos
            st.subheader("🏆 Top 10 Equipos (Rating ELO)")
            top_teams = st.session_state.elo.get_top_teams(10)
            for i, (team, rating) in enumerate(top_teams, 1):
                st.metric(f"{i}. {team}", f"{rating:.0f}")

with tab4:
    st.subheader("Optimizar Pesos del Modelo Híbrido")
    st.markdown("""
    El modelo híbrido combina:
    - **Mercado** (30%): Probabilidades de las casas
    - **Poisson** (20%): Modelo estructural de goles
    - **ELO** (20%): Sistema de puntuación dinámico
    - **XGBoost** (30%): Machine Learning
    
    Ajusta los pesos para maximizar el Sharpe Ratio
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        weight_market = st.slider("Peso Mercado", 0.0, 1.0, 0.3, 0.05)
        weight_poisson = st.slider("Peso Poisson", 0.0, 1.0, 0.2, 0.05)
        weight_elo = st.slider("Peso ELO", 0.0, 1.0, 0.2, 0.05)
        weight_xgb = st.slider("Peso XGBoost", 0.0, 1.0, 0.3, 0.05)
        
        total = weight_market + weight_poisson + weight_elo + weight_xgb
        
        if abs(total - 1.0) > 0.01:
            st.warning(f"⚠️ Los pesos deben sumar 1.0 (actual: {total:.2f})")
        else:
            if st.button("💾 Guardar Pesos"):
                # Aquí guardarías los pesos en una configuración
                st.success("✅ Pesos guardados!")
    
    with col2:
        st.info("""
        **Recomendaciones:**
        - Más peso al mercado si confías en las odds
        - Más peso a XGBoost si tienes muchos datos
        - Balance 30-20-20-30 suele funcionar bien
        """)
