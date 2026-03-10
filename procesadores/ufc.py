import streamlit as st
import pandas as pd
import re

class ProcesadorUFC:
    def procesar(self, texto_crudo):
        """Procesa texto de UFC y devuelve peleas estructuradas"""
        peleas = []
        
        # Limpiar líneas
        lineas = []
        for item in texto_crudo:
            if isinstance(item, str):
                lineas.extend(item.split('\n'))
        
        lineas = [l.strip() for l in lineas if l.strip()]
        
        peleadores = []
        odds = []
        
        for linea in lineas:
            partes = linea.split()
            if len(partes) >= 2:
                # Verificar si el último es odds
                if partes[-1].startswith('+') or partes[-1].startswith('-'):
                    nombre = ' '.join(partes[:-1])
                    peleadores.append(nombre)
                    odds.append(partes[-1])
        
        # Agrupar en peleas
        for i in range(0, len(peleadores)-1, 2):
            if i + 1 < len(peleadores):
                pelea = {
                    'peleador1': peleadores[i],
                    'odds1': odds[i] if i < len(odds) else 'N/A',
                    'peleador2': peleadores[i+1],
                    'odds2': odds[i+1] if i+1 < len(odds) else 'N/A'
                }
                peleas.append(pelea)
        
        return peleas
