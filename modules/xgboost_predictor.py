# modules/xgboost_predictor.py
import numpy as np
import pandas as pd
import streamlit as st
import xgboost as xgb
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class XGBoostPredictor:
    """
    Predictor basado en XGBoost que aprende de datos históricos
    """
    
    def __init__(self, model_path='models/xgboost_model.json'):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        self.model_path = model_path
        
        # Cargar modelo si existe
        self._load_model()
    
    def _load_model(self):
        """Carga modelo previamente entrenado"""
        try:
            if os.path.exists(self.model_path):
                self.model = xgb.XGBClassifier()
                self.model.load_model(self.model_path)
                self.is_trained = True
                # Intentar cargar scaler
                scaler_path = self.model_path.replace('.json', '_scaler.pkl')
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
        except Exception as e:
            st.warning(f"No se pudo cargar modelo existente: {e}")
    
    def _save_model(self):
        """Guarda el modelo entrenado"""
        try:
            os.makedirs('models', exist_ok=True)
            self.model.save_model(self.model_path)
            scaler_path = self.model_path.replace('.json', '_scaler.pkl')
            joblib.dump(self.scaler, scaler_path)
        except Exception as e:
            st.error(f"Error guardando modelo: {e}")
    
    def prepare_features(self, home_team, away_team, home_rating, away_rating, 
                         home_stats, away_stats, liga_data):
        """
        Prepara features para el modelo XGBoost
        """
        features = []
        
        # Features de rating ELO
        features.append(home_rating)
        features.append(away_rating)
        features.append(home_rating - away_rating)  # Diferencia
        
        # Features de estadísticas (normalizadas)
        features.append(home_stats.get('avg_goals_for', 1.5))
        features.append(home_stats.get('avg_goals_against', 1.2))
        features.append(away_stats.get('avg_goals_for', 1.3))
        features.append(away_stats.get('avg_goals_against', 1.4))
        
        # Features de forma reciente (últimos 5)
        features.append(home_stats.get('form_recent', 0.5))
        features.append(away_stats.get('form_recent', 0.5))
        
        # Features de liga
        features.append(liga_data.get('goles_promedio', 2.5))
        features.append(liga_data.get('local_ventaja', 55) / 100)
        features.append(liga_data.get('btts_pct', 50) / 100)
        
        # Features de mercado (si están disponibles)
        features.append(home_stats.get('odds_implied_prob', 0.4))
        features.append(away_stats.get('odds_implied_prob', 0.35))
        
        return np.array(features).reshape(1, -1)
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Entrena el modelo XGBoost
        """
        # Escalar features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Configurar parámetros óptimos
        params = {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'objective': 'multi:softprob',
            'num_class': 3,
            'eval_metric': ['mlogloss', 'merror'],
            'random_state': 42
        }
        
        self.model = xgb.XGBClassifier(**params)
        
        # Entrenar con early stopping si hay validación
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            self.model.fit(
                X_scaled, y_train,
                eval_set=[(X_val_scaled, y_val)],
                early_stopping_rounds=20,
                verbose=False
            )
        else:
            self.model.fit(X_scaled, y_train)
        
        self.is_trained = True
        self.feature_names = [
            'elo_home', 'elo_away', 'elo_diff',
            'home_goals_for', 'home_goals_against',
            'away_goals_for', 'away_goals_against',
            'home_form', 'away_form',
            'league_goals', 'home_advantage', 'league_btts',
            'market_home_prob', 'market_away_prob'
        ]
        
        self._save_model()
        
        return self.model
    
    def predict(self, features):
        """
        Predice probabilidades para [local, empate, visitante]
        """
        if not self.is_trained or self.model is None:
            return None
        
        try:
            features_scaled = self.scaler.transform(features)
            probs = self.model.predict_proba(features_scaled)[0]
            return {
                'home': probs[0],
                'draw': probs[1],
                'away': probs[2]
            }
        except Exception as e:
            st.error(f"Error en predicción XGBoost: {e}")
            return None
    
    def get_feature_importance(self):
        """
        Devuelve importancia de features para interpretabilidad
        """
        if not self.is_trained or self.model is None:
            return None
        
        importance = self.model.feature_importances_
        if self.feature_names:
            return sorted(zip(self.feature_names, importance), 
                         key=lambda x: x[1], reverse=True)
        return None
