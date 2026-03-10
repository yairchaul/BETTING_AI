import streamlit as st
import pandas as pd
import re

class ProcesadorFutbol:
    def procesar(self, texto_crudo):
        """Procesa texto de fútbol y devuelve partidos estructurados"""
        partidos = []
        
        # Unir todo el texto
        texto = ' '.join([str(t) for t in texto_crudo if t])
        
        # Buscar patrones como "Equipo +odd Empate +odd Equipo +odd"
        patron = r'([A-Za-zÀ-ÿ\s]+?)([+-]\d+)\s+Empate\s+([+-]\d+)\s+([A-Za-zÀ-ÿ\s]+?)([+-]\d+)'
        matches = re.findall(patron, texto)
        
        for match in matches:
            partido = {
                'local': match[0].strip(),
                'odds_local': match[1],
                'empate': 'Empate',
                'odds_empate': match[2],
                'visitante': match[3].strip(),
                'odds_visitante': match[4]
            }
            partidos.append(partido)
        
        return partidos
