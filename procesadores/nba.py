import streamlit as st
import pandas as pd
import re

class ProcesadorNBA:
    def procesar(self, texto_crudo):
        """Procesa texto de NBA y devuelve juegos estructurados"""
        juegos = []
        texto = ' '.join([str(t) for t in texto_crudo if t])
        
        # Buscar patrones de equipos NBA
        # Formato: Equipo +odd O/U total odd spread odd
        patron = r'([A-Za-z\s]+?)([+-]\d+)([OU])(\d+\.?\d*)([+-]?\d+)([+-]\d+\.?\d*)([+-]?\d+)'
        equipos = re.findall(patron, texto)
        
        for i in range(0, len(equipos)-1, 2):
            if i + 1 < len(equipos):
                home = equipos[i]
                away = equipos[i+1]
                
                juego = {
                    'local': {
                        'equipo': home[0].strip(),
                        'moneyline': home[1],
                        'over_under': f"{home[2]} {home[3]}",
                        'odds_ou': home[4],
                        'handicap': home[5],
                        'odds_spread': home[6]
                    },
                    'visitante': {
                        'equipo': away[0].strip(),
                        'moneyline': away[1],
                        'over_under': f"{away[2]} {away[3]}",
                        'odds_ou': away[4],
                        'handicap': away[5],
                        'odds_spread': away[6]
                    }
                }
                juegos.append(juego)
        
        return juegos
