"""
ANALIZADOR NBA MEJORADO - Heurístico con más factores
"""
import streamlit as st
from datetime import datetime
import random

class AnalizadorNBAMejorado:
    """
    Analizador NBA con múltiples factores:
    - Win rate histórico
    - Forma reciente (últimos 5 partidos)
    - Ventaja de localía
    - Diferencia de puntos promedio
    - Factor sorpresa (para equipos con WR similar)
    """
    
    def __init__(self, partido):
        self.partido = partido
        self.local = partido.get('local', '')
        self.visitante = partido.get('visitante', '')
        self.records = partido.get('records', {})
        self.odds = partido.get('odds', {})
        
        # Parsear records
        self.wr_local = self._calcular_win_rate(self.records.get('local', '0-0'))
        self.wr_visit = self._calcular_win_rate(self.records.get('visitante', '0-0'))
    
    def _calcular_win_rate(self, record_str):
        """Calcula win rate de un record '45-23'"""
        try:
            parts = record_str.split('-')
            wins = int(parts[0])
            losses = int(parts[1])
            total = wins + losses
            return (wins / total * 100) if total > 0 else 50
        except:
            return 50
    
    def _get_recent_form(self, team_name):
        """
        Simula forma reciente (últimos 5 partidos)
        En producción, esto vendría de datos reales
        """
        # Basado en win rate general con variación
        if team_name == self.local:
            base = self.wr_local
        else:
            base = self.wr_visit
        
        # Añadir variación aleatoria pero realista
        variacion = random.uniform(-5, 5)
        return base + variacion
    
    def _get_home_advantage(self):
        """Ventaja de localía (3-5 puntos)"""
        return 3.0
    
    def _get_point_differential(self, team_name):
        """
        Diferencia de puntos promedio
        Simulado basado en win rate
        """
        if team_name == self.local:
            wr = self.wr_local
        else:
            wr = self.wr_visit
        
        # Equipos con mejor WR tienen mejor diferencial
        return (wr - 50) * 0.5
    
    def analizar(self):
        """
        Análisis mejorado con 5 factores
        """
        # Factor 1: Win rate histórico (peso 30%)
        score1_local = self.wr_local * 0.3
        score1_visit = self.wr_visit * 0.3
        
        # Factor 2: Forma reciente (peso 25%)
        forma_local = self._get_recent_form(self.local)
        forma_visit = self._get_recent_form(self.visitante)
        score2_local = forma_local * 0.25
        score2_visit = forma_visit * 0.25
        
        # Factor 3: Ventaja localía (peso 15%)
        home_adv = self._get_home_advantage()
        score3_local = home_adv * 15
        score3_visit = 0
        
        # Factor 4: Diferencial de puntos (peso 20%)
        diff_local = self._get_point_differential(self.local)
        diff_visit = self._get_point_differential(self.visitante)
        score4_local = diff_local * 10
        score4_visit = diff_visit * 10
        
        # Factor 5: Factor sorpresa (para WR similares)
        score5_local = 0
        score5_visit = 0
        if abs(self.wr_local - self.wr_visit) < 5:
            # Cuando están muy parejos, dar ventaja al local
            score5_local = 5
            score5_visit = 0
        
        # Score total
        score_local = score1_local + score2_local + score3_local + score4_local + score5_local
        score_visit = score1_visit + score2_visit + score3_visit + score4_visit + score5_visit
        
        total = score_local + score_visit
        prob_local = (score_local / total) * 100 if total > 0 else 50
        prob_visit = (score_visit / total) * 100 if total > 0 else 50
        
        # Determinar ganador
        if prob_local > prob_visit + 8:
            ganador = self.local
            confianza = 70
            color = 'green'
        elif prob_visit > prob_local + 8:
            ganador = self.visitante
            confianza = 70
            color = 'green'
        elif prob_local > prob_visit + 3:
            ganador = self.local
            confianza = 60
            color = 'orange'
        elif prob_visit > prob_local + 3:
            ganador = self.visitante
            confianza = 60
            color = 'orange'
        else:
            ganador = self.local if prob_local > prob_visit else self.visitante
            confianza = 55
            color = 'yellow'
        
        # Construir explicación
        razones = []
        if self.wr_local > self.wr_visit + 5:
            razones.append(f"Mejor win rate histórico ({self.wr_local:.1f}% vs {self.wr_visit:.1f}%)")
        if forma_local > forma_visit + 5:
            razones.append(f"Mejor forma reciente")
        if home_adv > 0:
            razones.append("Ventaja de localía")
        
        return {
            'ganador': ganador,
            'confianza': confianza,
            'prob_local': round(prob_local, 1),
            'prob_visit': round(prob_visit, 1),
            'razones': razones,
            'color': color,
            'detalle': {
                'wr_local': round(self.wr_local, 1),
                'wr_visit': round(self.wr_visit, 1),
                'forma_local': round(forma_local, 1),
                'forma_visit': round(forma_visit, 1),
                'home_adv': home_adv
            }
        }
