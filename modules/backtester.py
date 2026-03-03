# modules/backtester.py
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

class Backtester:
    """
    Sistema de backtesting para validar estrategias de apuestas
    Basado en frameworks profesionales [citation:1][citation:4]
    """
    
    def __init__(self, initial_bankroll=1000):
        self.initial_bankroll = initial_bankroll
        self.results = []
        self.bankroll_history = []
    
    def run_backtest(self, bets_history, strategy_name="Mi Estrategia"):
        """
        Ejecuta backtesting sobre un historial de apuestas
        
        Args:
            bets_history: Lista de diccionarios con cada apuesta
                         [{'date': '2024-01-01', 'odds': 2.5, 'stake': 50, 'result': 'win'}]
        """
        bankroll = self.initial_bankroll
        results = []
        
        for bet in bets_history:
            bet_amount = bet.get('stake', 50)
            
            # Calcular resultado
            if bet['result'] == 'win':
                profit = bet_amount * (bet['odds'] - 1)
                bankroll += profit
                result_text = 'GANADA'
            else:
                profit = -bet_amount
                bankroll -= bet_amount
                result_text = 'PERDIDA'
            
            # Registrar
            results.append({
                'date': bet['date'],
                'match': bet.get('match', 'Desconocido'),
                'bet': bet.get('bet', 'Desconocida'),
                'odds': bet['odds'],
                'stake': bet_amount,
                'result': result_text,
                'profit': profit,
                'bankroll': bankroll
            })
        
        # Calcular métricas
        df = pd.DataFrame(results)
        metrics = self._calculate_metrics(df)
        
        return {
            'results': results,
            'metrics': metrics,
            'bankroll_final': bankroll,
            'total_profit': bankroll - self.initial_bankroll
        }
    
    def _calculate_metrics(self, df):
        """Calcula métricas de rendimiento"""
        if df.empty:
            return {}
        
        total_bets = len(df)
        won = len(df[df['result'] == 'GANADA'])
        lost = total_bets - won
        
        # ROI (Return on Investment)
        total_staked = df['stake'].sum()
        total_profit = df['profit'].sum()
        roi = (total_profit / total_staked) * 100 if total_staked > 0 else 0
        
        # Yield
        yield_pct = (total_profit / self.initial_bankroll) * 100
        
        # Sharpe Ratio (simplificado)
        returns = df['profit'].values / self.initial_bankroll
        sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Drawdown máximo
        cumulative = self.initial_bankroll + df['profit'].cumsum()
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max * 100
        max_drawdown = abs(drawdown.min())
        
        return {
            'total_bets': total_bets,
            'won': won,
            'lost': lost,
            'win_rate': (won / total_bets) * 100 if total_bets > 0 else 0,
            'total_staked': total_staked,
            'total_profit': total_profit,
            'roi': roi,
            'yield_pct': yield_pct,
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(max_drawdown, 2)
        }
    
    def monte_carlo_simulation(self, win_rate, avg_odds, simulations=10000, bets_per_sim=1000):
        """
        Simulación Monte Carlo para estimar riesgos [citation:1]
        """
        results = []
        
        for _ in range(simulations):
            bankroll = self.initial_bankroll
            for _ in range(bets_per_sim):
                # Simular resultado
                if np.random.random() < win_rate:
                    bankroll += 50 * (avg_odds - 1)  # stake fijo de 50
                else:
                    bankroll -= 50
            
            results.append(bankroll)
        
        results = np.array(results)
        return {
            'mean_final': np.mean(results),
            'median_final': np.median(results),
            'std_final': np.std(results),
            'percentile_5': np.percentile(results, 5),
            'percentile_95': np.percentile(results, 95),
            'prob_ruin': np.mean(results < 0) * 100
        }
    
    def compare_strategies(self, strategies_results):
        """
        Compara múltiples estrategias [citation:6]
        """
        comparison = []
        for name, data in strategies_results.items():
            metrics = data['metrics']
            comparison.append({
                'Estrategia': name,
                'ROI %': round(metrics.get('roi', 0), 2),
                'Win Rate %': round(metrics.get('win_rate', 0), 2),
                'Profit $': round(data.get('total_profit', 0), 2),
                'Sharpe': metrics.get('sharpe_ratio', 0),
                'Drawdown %': metrics.get('max_drawdown', 0)
            })
        
        return pd.DataFrame(comparison).sort_values('Sharpe', ascending=False)