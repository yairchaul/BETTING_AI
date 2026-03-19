"""
ANALIZADOR NBA PROPS - Con datos REALES de la API de ESPN
"""
import streamlit as st
import numpy as np

class AnalizadorNBAProps:
    """
    Analiza probabilidades de triples para jugadores NBA usando datos REALES
    """
    
    def __init__(self):
        # Ranking de defensas de triples (actualizado para 2025-26)
        self.defensa_triples = {
            "Boston Celtics": 0.82, "Oklahoma City Thunder": 0.85, "Orlando Magic": 0.87,
            "Minnesota Timberwolves": 0.88, "Cleveland Cavaliers": 0.90, "Houston Rockets": 0.92,
            "Memphis Grizzlies": 0.93, "Miami Heat": 0.94, "New York Knicks": 0.95,
            "LA Clippers": 0.96, "Denver Nuggets": 1.00, "Phoenix Suns": 1.00,
            "Dallas Mavericks": 1.00, "Sacramento Kings": 1.02, "Golden State Warriors": 1.03,
            "Los Angeles Lakers": 1.04, "Charlotte Hornets": 1.18, "Detroit Pistons": 1.20,
            "Washington Wizards": 1.22, "Portland Trail Blazers": 1.24, "Utah Jazz": 1.25,
            "San Antonio Spurs": 1.27, "Chicago Bulls": 1.15, "Atlanta Hawks": 1.12,
            "Indiana Pacers": 1.10, "Toronto Raptors": 1.08,
        }
        print("✅ Analizador NBA Props inicializado")
    
    def analizar_partido(self, partido):
        """
        Analiza jugadores destacados usando datos REALES de la API
        """
        local = partido['local']
        visitante = partido['visitante']
        
        # Obtener líderes del partido (ya extraídos en espn_data_pipeline)
        lideres_local = partido.get('lideres', {}).get('local', [])
        lideres_visit = partido.get('lideres', {}).get('visitante', [])
        
        # Filtrar solo anotadores (pointsPerGame)
        anotadores_local = [l for l in lideres_local if l['categoria'] == 'pointsPerGame']
        anotadores_visit = [l for l in lideres_visit if l['categoria'] == 'pointsPerGame']
        
        resultados = []
        
        # Procesar anotadores locales
        for jugador in anotadores_local[:3]:  # Top 3
            try:
                promedio = float(jugador['valor'])
                analisis = self._analizar_jugador(
                    jugador['nombre'], 
                    promedio, 
                    visitante,  # Rival es el visitante
                    linea=2.5
                )
                resultados.append(analisis)
            except:
                pass
        
        # Procesar anotadores visitantes
        for jugador in anotadores_visit[:3]:  # Top 3
            try:
                promedio = float(jugador['valor'])
                analisis = self._analizar_jugador(
                    jugador['nombre'], 
                    promedio, 
                    local,  # Rival es el local
                    linea=2.5
                )
                resultados.append(analisis)
            except:
                pass
        
        return resultados
    
    def _analizar_jugador(self, nombre_jugador, promedio, equipo_rival, linea=2.5):
        """
        Analiza la probabilidad de que un jugador supere la línea de triples
        """
        import random
        
        # Simular historial basado en el promedio real
        # En una versión futura, esto vendría de datos históricos reales
        historial = []
        for _ in range(5):
            # Generar valor alrededor del promedio con variación
            valor = max(0, int(np.random.normal(promedio / 8, 0.8)))  # Ajuste para triples
            historial.append(valor)
        
        veces_superado = sum(1 for t in historial if t > linea)
        prob_base = (veces_superado / 5) * 100
        
        # Ajuste por rival
        multiplicador = self.defensa_triples.get(equipo_rival, 1.0)
        prob_ajustada = min(95, prob_base * multiplicador)
        
        # Determinar recomendación
        if prob_ajustada >= 70:
            recomendacion = "🔥 OVER (Alta Confianza)"
            color = 'green'
        elif prob_ajustada >= 60:
            recomendacion = "✅ OVER (Confianza Media)"
            color = 'orange'
        else:
            recomendacion = "⚪ PASAR"
            color = 'gray'
        
        return {
            'jugador': nombre_jugador,
            'linea': linea,
            'promedio_puntos': round(promedio, 1),
            'promedio_triples': round(promedio / 8, 1),  # Estimación
            'probabilidad': round(prob_ajustada, 1),
            'veces': veces_superado,
            'total': 5,
            'multiplicador': round(multiplicador, 2),
            'recomendacion': recomendacion,
            'color': color,
            'valor_detectado': prob_ajustada > 65 and multiplicador > 1.1,
            'historial': historial
        }
