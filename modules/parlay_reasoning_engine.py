# -*- coding: utf-8 -*-
"""
Motor de razonamiento para parlays - REGLAS 1-7 (ORDEN CORREGIDO)
"""
class ParlayReasoningEngine:
    """
    Implementa las 7 reglas jerárquicas en el orden correcto
    """
    
    def __init__(self):
        self.umbral_over_1t = 0.60     # Regla 1
        self.umbral_over_3_5 = 0.60    # Regla 2
        self.umbral_favorito_over = 0.55  # Regla 2
        self.umbral_btts = 0.60        # Regla 3
        self.umbral_over = 0.55        # Regla 4
        self.objetivo_over = 0.55      # Regla 4
        self.umbral_favorito = 0.50    # Reglas 5 y 6
        self.umbral_underdog = 0.40    # Reglas 5 y 6
        self.umbral_combinado = 0.50   # Regla 7
    
    def aplicar_reglas(self, markets, probs_1x2, home, away):
        """
        Aplica las 7 reglas en orden jerárquico
        """
        picks = []
        
        # =====================================================================
        # REGLA 1 - Over 1.5 Primer Tiempo (>60%) [MÁXIMA PRIORIDAD]
        # =====================================================================
        over_1_5_1t = markets['overs']['over1_5_1t']
        if over_1_5_1t > self.umbral_over_1t:
            picks.append({
                'nivel': 1,
                'mercado': 'Over 1.5 1T',
                'prob': over_1_5_1t,
                'justificacion': f'Regla 1: Over 1.5 1T = {over_1_5_1t:.1%} > 60%'
            })
            return picks
        
        # =====================================================================
        # REGLA 2 - Over 3.5 >60% + Favorito >55% [NUEVA ALTA PRIORIDAD]
        # =====================================================================
        over_3_5 = markets['overs']['over3_5']
        home_win = probs_1x2['home']
        away_win = probs_1x2['away']
        
        if over_3_5 > self.umbral_over_3_5:
            if home_win > self.umbral_favorito_over:
                # 2 picks: Gana Local + Over 3.5
                picks.append({
                    'nivel': 2,
                    'mercado': f'Gana {home}',
                    'prob': home_win,
                    'justificacion': f'Regla 2: Local favorito + Over 3.5'
                })
                picks.append({
                    'nivel': 2,
                    'mercado': 'Over 3.5',
                    'prob': over_3_5,
                    'justificacion': f'Regla 2: Over 3.5 complementario'
                })
                return picks
            
            elif away_win > self.umbral_favorito_over:
                # 2 picks: Gana Visitante + Over 3.5
                picks.append({
                    'nivel': 2,
                    'mercado': f'Gana {away}',
                    'prob': away_win,
                    'justificacion': f'Regla 2: Visitante favorito + Over 3.5'
                })
                picks.append({
                    'nivel': 2,
                    'mercado': 'Over 3.5',
                    'prob': over_3_5,
                    'justificacion': f'Regla 2: Over 3.5 complementario'
                })
                return picks
        
        # =====================================================================
        # REGLA 3 - BTTS (>60%)
        # =====================================================================
        btts = markets['btts']
        if btts > self.umbral_btts:
            picks.append({
                'nivel': 3,
                'mercado': 'BTTS Sí',
                'prob': btts,
                'justificacion': f'Regla 3: BTTS = {btts:.1%} > 60%'
            })
            return picks
        
        # =====================================================================
        # REGLA 4 - Mejor Over (cuando no hay favorito claro)
        # =====================================================================
        if home_win < self.umbral_favorito and away_win < self.umbral_favorito:
            overs = [
                ('Over 1.5', markets['overs']['over1_5']),
                ('Over 2.5', markets['overs']['over2_5']),
                ('Over 3.5', markets['overs']['over3_5'])
            ]
            
            overs_validos = [(nombre, prob) for nombre, prob in overs if prob > self.umbral_over]
            
            if overs_validos:
                # Elegir el más cercano a 55%
                mejor_over = min(overs_validos, key=lambda x: abs(x[1] - self.objetivo_over))
                picks.append({
                    'nivel': 4,
                    'mercado': mejor_over[0],
                    'prob': mejor_over[1],
                    'justificacion': f'Regla 4: {mejor_over[0]} más cercano a 55%'
                })
            else:
                mejor_over = max(overs, key=lambda x: x[1])
                picks.append({
                    'nivel': 4,
                    'mercado': mejor_over[0],
                    'prob': mejor_over[1],
                    'justificacion': f'Regla 4: {mejor_over[0]} (ninguno >55%)'
                })
            
            return picks
        
        # =====================================================================
        # REGLA 5 - Favorito Local (>50%) + Mejor Over
        # =====================================================================
        if home_win > self.umbral_favorito and away_win < self.umbral_underdog:
            picks.append({
                'nivel': 5,
                'mercado': f'Gana {home}',
                'prob': home_win,
                'justificacion': f'Regla 5: Favorito Local = {home_win:.1%}'
            })
            
            # Buscar mejor Over
            overs = [
                ('Over 1.5', markets['overs']['over1_5']),
                ('Over 2.5', markets['overs']['over2_5']),
                ('Over 3.5', markets['overs']['over3_5'])
            ]
            overs_validos = [(nombre, prob) for nombre, prob in overs if prob > self.umbral_over]
            
            if overs_validos:
                mejor_over = min(overs_validos, key=lambda x: abs(x[1] - self.objetivo_over))
            else:
                mejor_over = max(overs, key=lambda x: x[1])
            
            picks.append({
                'nivel': 5,
                'mercado': mejor_over[0],
                'prob': mejor_over[1],
                'justificacion': f'Regla 5: Over complementario'
            })
            
            return picks
        
        # =====================================================================
        # REGLA 6 - Favorito Visitante (>50%) + Mejor Over
        # =====================================================================
        if away_win > self.umbral_favorito and home_win < self.umbral_underdog:
            picks.append({
                'nivel': 6,
                'mercado': f'Gana {away}',
                'prob': away_win,
                'justificacion': f'Regla 6: Favorito Visitante = {away_win:.1%}'
            })
            
            overs = [
                ('Over 1.5', markets['overs']['over1_5']),
                ('Over 2.5', markets['overs']['over2_5']),
                ('Over 3.5', markets['overs']['over3_5'])
            ]
            overs_validos = [(nombre, prob) for nombre, prob in overs if prob > self.umbral_over]
            
            if overs_validos:
                mejor_over = min(overs_validos, key=lambda x: abs(x[1] - self.objetivo_over))
            else:
                mejor_over = max(overs, key=lambda x: x[1])
            
            picks.append({
                'nivel': 6,
                'mercado': mejor_over[0],
                'prob': mejor_over[1],
                'justificacion': f'Regla 6: Over complementario'
            })
            
            return picks
        
        # =====================================================================
        # REGLA 7 - Default (mejor Over)
        # =====================================================================
        overs = [
            ('Over 1.5', markets['overs']['over1_5']),
            ('Over 2.5', markets['overs']['over2_5']),
            ('Over 3.5', markets['overs']['over3_5'])
        ]
        mejor_over = max(overs, key=lambda x: x[1])
        picks.append({
            'nivel': 7,
            'mercado': mejor_over[0],
            'prob': mejor_over[1],
            'justificacion': f'Regla 7: Default = {mejor_over[0]}'
        })
        
        return picks
    
    def validar_combinacion(self, picks_partido):
        """
        REGLA 7 - Validación de combinados
        Si la probabilidad combinada < 50%, reemplazar por el mejor pick simple
        """
        if len(picks_partido) != 2:
            return picks_partido
        
        prob_combinada = picks_partido[0]['prob'] * picks_partido[1]['prob']
        
        if prob_combinada < self.umbral_combinado:
            mejor_pick = max(picks_partido, key=lambda x: x['prob'])
            return [mejor_pick]
        
        return picks_partido
