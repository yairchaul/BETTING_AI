"""
ANALIZADOR NBA MEJORADO - Con props de jugadores
"""
import streamlit as st

class AnalizadorNBAMejorado:
    def __init__(self, partido):
        self.partido = partido
        self.local = partido.get('local', '')
        self.visitante = partido.get('visitante', '')
        self.records = partido.get('records', {})
        self.odds = partido.get('odds', {})
        
        self.wr_local = self._calcular_wr(self.records.get('local', '0-0'))
        self.wr_visit = self._calcular_wr(self.records.get('visitante', '0-0'))
    
    def _calcular_wr(self, record_str):
        try:
            parts = record_str.split('-')
            wins = int(parts[0])
            losses = int(parts[1])
            total = wins + losses
            return (wins / total * 100) if total > 0 else 50
        except:
            return 50
    
    def _get_star_player_stats(self):
        """Simula estadísticas del jugador estrella"""
        # En producción, esto vendría de una API
        return {
            'nombre': 'Jayson Tatum' if 'Boston' in self.local else 'Stephen Curry',
            'promedio_3pt': 3.5,  # triples por partido
            'porcentaje_3pt': 38.5,
            'prob_over_3_5': 65  # probabilidad de anotar 4+ triples
        }
    
    def analizar(self):
        """Analiza el partido incluyendo props de jugador"""
        
        # Análisis tradicional
        if self.wr_local > self.wr_visit + 10:
            ganador = self.local
            confianza = 65
        elif self.wr_visit > self.wr_local + 10:
            ganador = self.visitante
            confianza = 65
        else:
            ganador = self.local if self.wr_local > self.wr_visit else self.visitante
            confianza = 55
        
        # Props de jugador
        star = self._get_star_player_stats()
        
        return {
            'ganador': ganador,
            'confianza': confianza,
            'wr_local': round(self.wr_local, 1),
            'wr_visit': round(self.wr_visit, 1),
            'apuesta': f"GANA {ganador}",
            'props': {
                'jugador': star['nombre'],
                'over_3_pt': star['prob_over_3_5'],
                'promedio_3pt': star['promedio_3pt']
            },
            'color': 'green' if confianza > 60 else 'orange'
        }
