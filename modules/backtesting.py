# modules/backtesting.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Backtester:
    def __init__(self, initial_bankroll=1000):
        self.initial_bankroll = initial_bankroll
        self.results = []
    
    def run_backtest(self, bets_df, results_df):
        """
        Simula apuestas pasadas para ver efectividad
        bets_df: DataFrame con columnas [date, odds, stake, predicted_prob]
        results_df: DataFrame con columnas [date, match, result]
        """
        bankroll = self.initial_bankroll
        results = []
        
        for _, bet in bets_df.iterrows():
            # Buscar resultado real
            real_result = results_df[results_df['date'] == bet['date']]
            
            if not real_result.empty:
                if real_result.iloc[0]['result'] == 'won':
                    profit = bet['stake'] * (bet['odds'] - 1)
                else:
                    profit = -bet['stake']
                
                bankroll += profit
                results.append({
                    'date': bet['date'],
                    'odds': bet['odds'],
                    'stake': bet['stake'],
                    'predicted_prob': bet['predicted_prob'],
                    'result': real_result.iloc[0]['result'],
                    'profit': profit,
                    'bankroll': bankroll
                })
        
        df = pd.DataFrame(results)
        if df.empty:
            return {
                'total_bets': 0,
                'win_rate': 0,
                'total_profit': 0,
                'final_bankroll': self.initial_bankroll,
                'roi': 0,
                'sharpe_ratio': 0
            }
        
        total_bets = len(df)
        won = len(df[df['result'] == 'won'])
        total_profit = df['profit'].sum()
        
        returns = df['profit'] / self.initial_bankroll
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        return {
            'total_bets': total_bets,
            'win_rate': won / total_bets,
            'total_profit': total_profit,
            'final_bankroll': bankroll,
            'roi': (total_profit / self.initial_bankroll) * 100,
            'sharpe_ratio': sharpe
        }