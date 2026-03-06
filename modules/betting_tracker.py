# modules/betting_tracker.py
import json
import os
from datetime import datetime
import pandas as pd

class BettingTracker:
    def __init__(self, filepath='data/betting_history.json'):
        self.filepath = filepath
        self.history = self._load_history()
    
    def _load_history(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_bet(self, bet_data):
        bet = {
            'id': len(self.history) + 1,
            'date': datetime.now().isoformat(),
            'matches': bet_data.get('matches', []),
            'odds': bet_data.get('odds', 0),
            'stake': bet_data.get('stake', 0),
            'result': 'pending',  # 'won', 'lost', 'pending'
            'profit': 0
        }
        self.history.append(bet)
        self._save_history()
        return bet
    
    def update_result(self, bet_id, result):
        """result: 'won' o 'lost'"""
        for bet in self.history:
            if bet['id'] == bet_id:
                bet['result'] = result
                if result == 'won':
                    bet['profit'] = bet['stake'] * (bet['odds'] - 1)
                else:
                    bet['profit'] = -bet['stake']
                break
        self._save_history()
    
    def get_stats(self):
        df = pd.DataFrame(self.history)
        if df.empty:
            return {
                'total_bets': 0,
                'won': 0,
                'lost': 0,
                'win_rate': 0,
                'total_profit': 0,
                'roi': 0
            }
        
        completed = df[df['result'] != 'pending']
        if completed.empty:
            return {
                'total_bets': len(df),
                'won': 0,
                'lost': 0,
                'win_rate': 0,
                'total_profit': 0,
                'roi': 0
            }
        
        won = len(completed[completed['result'] == 'won'])
        lost = len(completed[completed['result'] == 'lost'])
        total_profit = completed['profit'].sum()
        total_stake = completed['stake'].sum()
        
        return {
            'total_bets': len(df),
            'won': won,
            'lost': lost,
            'win_rate': won / (won + lost) if (won + lost) > 0 else 0,
            'total_profit': total_profit,
            'roi': (total_profit / total_stake) * 100 if total_stake > 0 else 0
        }
    
    def get_history_df(self):
        return pd.DataFrame(self.history)