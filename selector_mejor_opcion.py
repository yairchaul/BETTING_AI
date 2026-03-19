"""
SELECTOR MEJOR OPCIÓN - Jerarquía estricta de 6 reglas
CORREGIDO: Maneja correctamente las probabilidades normalizadas
"""
import streamlit as st

class SelectorMejorOpcion:
    """
    Elige la mejor apuesta siguiendo la jerarquía estricta de reglas
    """
    
    @staticmethod
    def seleccionar(probabilidades, nombre_local, nombre_visitante):
        """
        Aplica la jerarquía de reglas para elegir la mejor apuesta
        
        Args:
            probabilidades: Diccionario con todas las probabilidades calculadas
            nombre_local: Nombre real del equipo local
            nombre_visitante: Nombre real del equipo visitante
            
        Returns:
            Tupla (apuesta, confianza, detalle, regla)
        """
        h = probabilidades
        
        # Determinar qué equipo tiene mayor probabilidad de ganar
        if h.get('prob_local', 0) > h.get('prob_visitante', 0):
            equipo_favorito = nombre_local
            prob_ganador = h.get('prob_local', 0)
        else:
            equipo_favorito = nombre_visitante
            prob_ganador = h.get('prob_visitante', 0)
        
        # 1. Regla Especial: BTTS > 70%
        if h.get('prob_btts', 0) >= 70:
            return ("⚽ AMBOS ANOTAN (BTTS) - Prioridad Alta", 
                    h['prob_btts'], 
                    f"BTTS al {h['prob_btts']}% supera umbral de 70%",
                    1)
        
        # 2. Regla 1: Over 1.5 HT > 60%
        if h.get('prob_ht', 0) >= 60:
            return ("⚽ OVER 1.5 GOLES 1er TIEMPO", 
                    h['prob_ht'], 
                    f"{h['prob_ht']}% de probabilidad ≥60%",
                    1)

        # 3. Regla 2: Over 3.5 FT > 60%
        if h.get('prob_over35', 0) >= 60:
            return ("⚽ OVER 3.5 GOLES", 
                    h['prob_over35'], 
                    f"{h['prob_over35']}% de probabilidad ≥60%",
                    2)

        # 4. Regla 3: BTTS > 60%
        if h.get('prob_btts', 0) >= 60:
            return ("⚽ AMBOS ANOTAN (BTTS)", 
                    h['prob_btts'], 
                    f"{h['prob_btts']}% de probabilidad ≥60%",
                    3)

        # 5. Regla 4: El Over más cercano al 55%
        overs = {
            "OVER 1.5": abs(h.get('prob_over15', 0) - 55),
            "OVER 2.5": abs(h.get('prob_over25', 0) - 55),
            "OVER 3.5": abs(h.get('prob_over35', 0) - 55)
        }
        mejor_over = min(overs, key=overs.get)
        
        # Obtener la probabilidad correspondiente
        if mejor_over == "OVER 1.5":
            prob_mejor_over = h.get('prob_over15', 0)
        elif mejor_over == "OVER 2.5":
            prob_mejor_over = h.get('prob_over25', 0)
        else:
            prob_mejor_over = h.get('prob_over35', 0)
        
        # 6. Regla 6: Combinada (Victoria > 55% + Over cercano a 55%)
        if prob_ganador >= 55 and overs[mejor_over] <= 5:
            confianza_combo = (prob_ganador + prob_mejor_over) / 2
            return (f"⚽ GANA {equipo_favorito} + {mejor_over}", 
                    round(confianza_combo, 1), 
                    f"Victoria ({prob_ganador}%) + Over cercano a 55%",
                    6)

        # 7. Regla 5: Ganador simple
        if prob_ganador >= 55:
            return (f"⚽ GANA {equipo_favorito}", 
                    round(prob_ganador, 1), 
                    f"{prob_ganador}% de probabilidad ≥55%",
                    5)

        # 8. Si nada se cumple
        return ("❌ NO OPERABLE", 
                0, 
                "No cumple ningún filtro de seguridad",
                0)
    
    @staticmethod
    def obtener_color(confianza):
        """Determina el color según la confianza"""
        if confianza >= 70:
            return 'green'
        elif confianza >= 55:
            return 'orange'
        else:
            return 'red'
