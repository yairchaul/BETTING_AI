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
    
    def get_live_odds_for_parlay(self, partidos):
        """
        Obtiene odds EN VIVO para todos los partidos del parlay
        """
        if not self.client:
            return None
        
        resultados = []
        
        for partido in partidos:
            # Buscar por nombres de equipos
            query = f"{partido['local']} {partido['visitante']}"
            events = self.client.search_events(query=query)
            
            if events and len(events) > 0:
                event_id = events[0]['id']
                odds = self.client.get_event_odds(
                    event_id, 
                    bookmakers="pinnacle,bet365,caliente"
                )
                
                if odds:
                    resultados.append({
                        'partido': f"{partido['local']} vs {partido['visitante']}",
                        'odds_reales': odds,
                        'cuota_local': odds.get('home_odd'),
                        'cuota_empate': odds.get('draw_odd'),
                        'cuota_visitante': odds.get('away_odd'),
                        'bookmaker': odds.get('bookmaker')
                    })
        
        return resultados
    
    def find_value_bets(self, nuestros_analisis, umbral_ev=0.05):
        """
        Compara nuestras probabilidades con odds reales del mercado
        """
        value_bets = []
        
        for analisis in nuestros_analisis:
            # Buscar odds reales
            odds_reales = self.get_live_odds_for_parlay([analisis])
            
            if odds_reales and len(odds_reales) > 0:
                odds = odds_reales[0]
                
                # Para cada mercado, calcular EV real
                mercados = [
                    ('Gana Local', analisis['prob_local'], odds['cuota_local']),
                    ('Empate', analisis['prob_empate'], odds['cuota_empate']),
                    ('Gana Visitante', analisis['prob_visit'], odds['cuota_visitante'])
                ]
                
                for mercado, prob, odd in mercados:
                    if odd and prob:
                        ev = (prob * odd) - 1
                        if ev > umbral_ev:
                            value_bets.append({
                                'partido': analisis['partido'],
                                'mercado': mercado,
                                'probabilidad': prob,
                                'odd_real': odd,
                                'ev': ev,
                                'confianza': 'ALTA' if ev > 0.10 else 'MEDIA'
                            })
        
        return sorted(value_bets, key=lambda x: x['ev'], reverse=True)