# modules/odds_api_integrator.py
from odds_api import OddsAPIClient
import streamlit as st
import pandas as pd
from datetime import datetime

class OddsAPIIntegrator:
    """
    Integración profesional con Odds-API.io para datos reales
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("ODDS_API_KEY", "")
        self.client = None
        if self.api_key:
            self.client = OddsAPIClient(api_key=self.api_key)
    
    def get_live_odds(self, home_team, away_team):
        """
        Obtiene odds EN VIVO para un partido específico
        """
        if not self.client:
            return None
        
        try:
            # Buscar por nombres de equipos
            query = f"{home_team} {away_team}"
            events = self.client.search_events(query=query)
            
            if events and len(events) > 0:
                event_id = events[0]['id']
                
                # Obtener odds de múltiples bookmakers [citation:3]
                odds = self.client.get_event_odds(
                    event_id, 
                    bookmakers="pinnacle,bet365,caliente"
                )
                
                if odds:
                    return {
                        'partido': f"{home_team} vs {away_team}",
                        'cuota_local': self._extract_odds(odds, 'home'),
                        'cuota_empate': self._extract_odds(odds, 'draw'),
                        'cuota_visitante': self._extract_odds(odds, 'away'),
                        'bookmaker': odds.get('bookmaker', 'Desconocido')
                    }
        except Exception as e:
            st.error(f"Error obteniendo odds: {e}")
        
        return None
    
    def _extract_odds(self, odds_data, market_type):
        """Extrae odds específicas del mercado"""
        try:
            for market in odds_data.get('markets', []):
                if market.get('name') == 'ML':  # Money Line
                    for odd in market.get('odds', []):
                        if market_type in odd:
                            return float(odd[market_type])
        except:
            pass
        return None
    
    def find_value_bets(self, partidos_analizados, umbral_ev=0.05):
        """
        Compara nuestras probabilidades con odds reales del mercado
        """
        value_bets = []
        
        for analisis in partidos_analizados:
            odds_reales = self.get_live_odds(
                analisis['home_team'], 
                analisis['away_team']
            )
            
            if odds_reales:
                mercados = [
                    ('Gana Local', analisis['final_probs'][0], odds_reales['cuota_local']),
                    ('Empate', analisis['final_probs'][1], odds_reales['cuota_empate']),
                    ('Gana Visitante', analisis['final_probs'][2], odds_reales['cuota_visitante'])
                ]
                
                for mercado, prob, odd in mercados:
                    if odd and prob:
                        ev = (prob * odd) - 1
                        if ev > umbral_ev:
                            value_bets.append({
                                'partido': f"{analisis['home_team']} vs {analisis['away_team']}",
                                'mercado': mercado,
                                'probabilidad': prob,
                                'odd_real': odd,
                                'ev': ev,
                                'confianza': 'ALTA' if ev > 0.10 else 'MEDIA'
                            })
        
        return sorted(value_bets, key=lambda x: x['ev'], reverse=True)
