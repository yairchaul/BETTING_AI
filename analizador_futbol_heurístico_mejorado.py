"""
ANALIZADOR FÚTBOL HEURÍSTICO MEJORADO - Con nombre de equipo real
"""
import streamlit as st
from calculador_probabilidades_futbol import CalculadorProbabilidadesFutbol
from selector_mejor_opcion import SelectorMejorOpcion

class AnalizadorFutbolHeuristicoMejorado:
    """
    Analiza partidos de fútbol con cálculos matemáticos reales
    y jerarquía estricta de 6 reglas
    """
    
    def __init__(self, stats_local, stats_visitante, nombre_local, nombre_visitante):
        self.local = stats_local
        self.visitante = stats_visitante
        self.nombre_local = nombre_local
        self.nombre_visitante = nombre_visitante
        self.probabilidades = CalculadorProbabilidadesFutbol.calcular(stats_local, stats_visitante)
        
        # 🔥 PASAR LOS NOMBRES REALES al selector
        self.apuesta, self.confianza, self.detalle, self.regla = SelectorMejorOpcion.seleccionar(
            self.probabilidades, 
            self.nombre_local, 
            self.nombre_visitante
        )
        self.color = SelectorMejorOpcion.obtener_color(self.confianza)
    
    def analizar(self):
        """
        Devuelve el resultado del análisis
        """
        return {
            'apuesta': self.apuesta,
            'confianza': self.confianza,
            'detalle': self.detalle,
            'regla': self.regla,
            'color': self.color,
            'probabilidades': self.probabilidades,
            'tipo': 'heurístico'
        }
    
    def obtener_resumen(self):
        """
        Resumen para pasar a Gemini
        """
        return self.probabilidades
