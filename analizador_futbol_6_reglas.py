"""
ANALIZADOR FÚTBOL - 6 Reglas jerárquicas
Basado en últimos 5 partidos de cada equipo
"""
import streamlit as st
import math

class AnalizadorFutbol6Reglas:
    """
    Analiza partidos de fútbol con jerarquía de 6 reglas
    """
    
    def __init__(self, stats_local, stats_visitante):
        """
        stats_local y stats_visitante deben contener:
        - ultimos_5: lista de partidos con goles_favor, goles_contra, goles_ht, resultado
        - lesionados: lista de jugadores lesionados
        """
        self.local = stats_local
        self.visitante = stats_visitante
        self._procesar_stats()
    
    def _procesar_stats(self):
        """Procesa estadísticas de últimos 5 partidos"""
        # Goles en primer tiempo
        self.goles_ht = []
        for p in self.local.get('ultimos_5', []):
            self.goles_ht.append(p.get('goles_ht', 0))
        for p in self.visitante.get('ultimos_5', []):
            self.goles_ht.append(p.get('goles_ht', 0))
        
        # Goles totales por partido
        self.goles_ft = []
        for i in range(5):
            if i < len(self.local.get('ultimos_5', [])) and i < len(self.visitante.get('ultimos_5', [])):
                goles = (self.local['ultimos_5'][i].get('goles_favor', 0) + 
                        self.visitante['ultimos_5'][i].get('goles_favor', 0))
                self.goles_ft.append(goles)
        
        # BTTS
        self.btts_count = 0
        for p in self.local.get('ultimos_5', []):
            if p.get('btts', False) or (p.get('goles_favor', 0) > 0 and p.get('goles_contra', 0) > 0):
                self.btts_count += 1
        for p in self.visitante.get('ultimos_5', []):
            if p.get('btts', False) or (p.get('goles_favor', 0) > 0 and p.get('goles_contra', 0) > 0):
                self.btts_count += 1
        
        # Victorias
        self.victorias_local = 0
        for p in self.local.get('ultimos_5', []):
            if p.get('resultado') in ['GANÓ', 'VICTORIA', 'WIN']:
                self.victorias_local += 1
        
        self.victorias_visit = 0
        for p in self.visitante.get('ultimos_5', []):
            if p.get('resultado') in ['GANÓ', 'VICTORIA', 'WIN']:
                self.victorias_visit += 1
        
        # Lesiones
        self.lesiones_local = len(self.local.get('lesionados', []))
        self.lesiones_visit = len(self.visitante.get('lesionados', []))
        
        self.total_partidos = len(self.goles_ht)
    
    def _probabilidad_over_ht(self, linea=1.5):
        """Probabilidad de Over X goles en primer tiempo"""
        if not self.goles_ht or self.total_partidos == 0:
            return 0
        exitos = sum(1 for g in self.goles_ht if g >= linea)
        return (exitos / self.total_partidos) * 100
    
    def _probabilidad_over_ft(self, linea):
        """Probabilidad de Over X goles en el partido"""
        if not self.goles_ft or len(self.goles_ft) == 0:
            return 0
        exitos = sum(1 for g in self.goles_ft if g >= linea)
        return (exitos / len(self.goles_ft)) * 100
    
    def _probabilidad_btts(self):
        """Probabilidad de que ambos anoten"""
        if self.total_partidos == 0:
            return 0
        return (self.btts_count / self.total_partidos) * 100
    
    def _probabilidad_victoria_local(self):
        """Probabilidad de victoria local basada en últimos 5"""
        return (self.victorias_local / 5) * 100
    
    def _probabilidad_victoria_visit(self):
        """Probabilidad de victoria visitante"""
        return (self.victorias_visit / 5) * 100
    
    def _factor_lesiones(self):
        """Factor de ajuste por lesiones"""
        if self.lesiones_local > 2:
            return 0.85
        if self.lesiones_visit > 2:
            return 0.85
        return 1.0
    
    def analizar(self):
        """
        Ejecuta la jerarquía de 6 reglas y devuelve la mejor apuesta
        """
        # ============================================
        # REGLA 1: Over 1.5 goles en primer tiempo (≥60%)
        # ============================================
        prob_ht = self._probabilidad_over_ht(1.5)
        if prob_ht >= 60:
            return {
                'apuesta': '⚽ OVER 1.5 GOLES 1er TIEMPO',
                'confianza': round(prob_ht, 1),
                'probabilidad': prob_ht,
                'regla': 1,
                'color': 'green',
                'detalle': f"{sum(1 for g in self.goles_ht if g>=1.5)}/{self.total_partidos} partidos con ≥2 goles HT"
            }
        
        # ============================================
        # REGLA 2: Over 3.5 goles final (≥60%)
        # ============================================
        prob_ft35 = self._probabilidad_over_ft(3.5)
        if prob_ft35 >= 60:
            return {
                'apuesta': '⚽ OVER 3.5 GOLES',
                'confianza': round(prob_ft35, 1),
                'probabilidad': prob_ft35,
                'regla': 2,
                'color': 'green',
                'detalle': f"{sum(1 for g in self.goles_ft if g>=3.5)}/{len(self.goles_ft)} partidos con ≥4 goles"
            }
        
        # ============================================
        # REGLA 3: BTTS - Ambos anotan (≥60%)
        # ============================================
        prob_btts = self._probabilidad_btts()
        if prob_btts >= 60:
            return {
                'apuesta': '⚽ AMBOS ANOTAN (BTTS)',
                'confianza': round(prob_btts, 1),
                'probabilidad': prob_btts,
                'regla': 3,
                'color': 'green',
                'detalle': f"{self.btts_count}/{self.total_partidos} partidos con BTTS"
            }
        
        # ============================================
        # REGLA 4: Mejor Over (más cercano a 55%)
        # ============================================
        overs = [
            (1.5, self._probabilidad_over_ft(1.5)),
            (2.5, self._probabilidad_over_ft(2.5)),
            (3.5, self._probabilidad_over_ft(3.5))
        ]
        
        mejor_over = min(overs, key=lambda x: abs(x[1] - 55))
        if mejor_over[1] >= 40:
            return {
                'apuesta': f"⚽ OVER {mejor_over[0]}",
                'confianza': round(mejor_over[1], 1),
                'probabilidad': mejor_over[1],
                'regla': 4,
                'color': 'yellow',
                'detalle': f"Más cercano a 55% (diferencia: {abs(mejor_over[1]-55):.1f}%)"
            }
        
        # ============================================
        # REGLA 5: Local o Visitante (≥55%)
        # ============================================
        prob_local = self._probabilidad_victoria_local() * self._factor_lesiones()
        prob_visit = self._probabilidad_victoria_visit() * self._factor_lesiones()
        
        if prob_local >= 55:
            return {
                'apuesta': f"⚽ GANA LOCAL",
                'confianza': round(prob_local, 1),
                'probabilidad': prob_local,
                'regla': 5,
                'color': 'blue',
                'detalle': f"{self.victorias_local}/5 victorias recientes"
            }
        
        if prob_visit >= 55:
            return {
                'apuesta': f"⚽ GANA VISITANTE",
                'confianza': round(prob_visit, 1),
                'probabilidad': prob_visit,
                'regla': 5,
                'color': 'blue',
                'detalle': f"{self.victorias_visit}/5 victorias recientes"
            }
        
        # ============================================
        # REGLA 6: Combo (Victoria + Mejor Over)
        # ============================================
        if mejor_over[1] >= 50:
            if prob_local > prob_visit:
                return {
                    'apuesta': f"⚽ GANA LOCAL + OVER {mejor_over[0]}",
                    'confianza': round((prob_local + mejor_over[1]) / 2, 1),
                    'probabilidad': (prob_local + mejor_over[1]) / 2,
                    'regla': 6,
                    'color': 'purple',
                    'detalle': f"Combinación de victoria local y over"
                }
            else:
                return {
                    'apuesta': f"⚽ GANA VISITANTE + OVER {mejor_over[0]}",
                    'confianza': round((prob_visit + mejor_over[1]) / 2, 1),
                    'probabilidad': (prob_visit + mejor_over[1]) / 2,
                    'regla': 6,
                    'color': 'purple',
                    'detalle': f"Combinación de victoria visitante y over"
                }
        
        # ============================================
        # Si ninguna regla se cumple
        # ============================================
        return {
            'apuesta': '❌ NO OPERABLE',
            'confianza': 0,
            'probabilidad': 0,
            'regla': 0,
            'color': 'red',
            'detalle': 'No cumple ningún filtro de seguridad'
        }
