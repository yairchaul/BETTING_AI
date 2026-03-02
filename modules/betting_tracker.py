import streamlit as st
import pandas as pd
from datetime import datetime
import json

class BettingTracker:
    def __init__(self):
        if 'bets' not in st.session_state:
            st.session_state.bets = []
    
    def add_bet(self, parlay_data, stake=100):
        """Registra una nueva apuesta"""
        bet = {
            'id': len(st.session_state.bets) + 1,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'selections': parlay_data['matches'],
            'total_odds': parlay_data['total_odds'],
            'probability': parlay_data['total_prob'],
            'stake': stake,
            'potential_win': round(stake * parlay_data['total_odds'], 2),
            'status': 'Pendiente',
            'result': None,
            'profit': 0
        }
        st.session_state.bets.append(bet)
        return bet
    
    def update_bet_result(self, bet_id, result):
        """Actualiza el resultado de una apuesta (Ganada/Perdida)"""
        for bet in st.session_state.bets:
            if bet['id'] == bet_id:
                bet['status'] = 'Resuelta'
                bet['result'] = result
                if result == 'Ganada':
                    bet['profit'] = bet['potential_win'] - bet['stake']
                else:
                    bet['profit'] = -bet['stake']
                break
    
    def get_stats(self):
        """Obtiene estadísticas de rendimiento"""
        bets = st.session_state.bets
        total_bets = len(bets)
        if total_bets == 0:
            return {'total_bets': 0, 'win_rate': 0, 'profit': 0}
        
        won = sum(1 for b in bets if b.get('result') == 'Ganada')
        lost = sum(1 for b in bets if b.get('result') == 'Perdida')
        pending = total_bets - won - lost
        
        total_profit = sum(b.get('profit', 0) for b in bets)
        
        return {
            'total_bets': total_bets,
            'won': won,
            'lost': lost,
            'pending': pending,
            'win_rate': round(won / (won + lost) * 100, 1) if (won + lost) > 0 else 0,
            'total_profit': total_profit
        }
    
    def show_tracker_ui(self):
        """Muestra la interfaz del tracker"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Registro de Apuestas")
        
        stats = self.get_stats()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total", stats['total_bets'])
            st.metric("Ganadas", stats['won'])
        with col2:
            st.metric("Profit", f"${stats['total_profit']:,.0f}")
            st.metric("Win Rate", f"{stats['win_rate']}%")
        
        if stats['pending'] > 0:
            st.sidebar.info(f"⏳ {stats['pending']} pendientes")
        
        # Mostrar historial en expander
        if st.session_state.bets:
            with st.sidebar.expander("📜 Historial"):
                for bet in reversed(st.session_state.bets[-10:]):  # Últimas 10
                    status_emoji = "✅" if bet.get('result') == 'Ganada' else "❌" if bet.get('result') == 'Perdida' else "⏳"
                    st.markdown(f"{status_emoji} **{bet['date'][5:16]}**")
                    st.markdown(f"   Cuota: {bet['total_odds']} | ${bet['profit']:+,.0f}")
                    st.markdown("---")
