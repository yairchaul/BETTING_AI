class RuleEngine:
    """
    Motor de reglas universal. Aplica las 7 reglas jerárquicas.
    """
    
    def ejecutar(self, evento):
        """
        Ejecuta las reglas según el deporte.
        """
        if evento.deporte == 'FUTBOL':
            return self._reglas_futbol(evento)
        elif evento.deporte == 'NBA':
            return self._reglas_nba(evento)
        elif evento.deporte == 'UFC':
            return self._reglas_ufc(evento)
        else:
            return []
    
    def _reglas_futbol(self, evento):
        """LAS 7 REGLAS DE FÚTBOL"""
        m = evento.mercados
        h = evento.local
        a = evento.visitante
        ph = m.get('prob_local', 0)
        pa = m.get('prob_visitante', 0)
        
        # REGLA 1: Over 1.5 Primer Tiempo > 60%
        if m.get('over_1_5_1t', 0) > 0.60:
            return [{
                'nivel': 1,
                'mercado': 'Over 1.5 1T',
                'prob': m['over_1_5_1t'],
                'justificacion': 'Regla 1: Over 1.5 1T dominante'
            }]
        
        # REGLA 2: Over 3.5 > 60% + Favorito > 55%
        if m.get('over_3_5', 0) > 0.60:
            picks = []
            if ph > 0.55:
                picks.append({'nivel': 2, 'mercado': f'Gana {h}', 'prob': ph})
                picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': m['over_3_5']})
                return picks
            if pa > 0.55:
                picks.append({'nivel': 2, 'mercado': f'Gana {a}', 'prob': pa})
                picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': m['over_3_5']})
                return picks
        
        # REGLA 3: BTTS > 60%
        if m.get('btts_yes', 0) > 0.60:
            return [{
                'nivel': 3,
                'mercado': 'BTTS Sí',
                'prob': m['btts_yes']
            }]
        
        # REGLA 4: Mejor Over (sin favorito claro)
        if ph < 0.55 and pa < 0.55:
            overs = [
                ('Over 1.5', m['over_1_5']),
                ('Over 2.5', m['over_2_5']),
                ('Over 3.5', m['over_3_5'])
            ]
            overs_validos = [(n, p) for n, p in overs if p > 0.55]
            if overs_validos:
                mejor = min(overs_validos, key=lambda x: abs(x[1] - 0.55))
                return [{'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]}]
            else:
                mejor = max(overs, key=lambda x: x[1])
                return [{'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]}]
        
        # REGLA 5: Favorito Local + Mejor Over
        if ph > 0.50 and pa < 0.40:
            overs = [('Over 1.5', m['over_1_5']), ('Over 2.5', m['over_2_5']), ('Over 3.5', m['over_3_5'])]
            mejor = max(overs, key=lambda x: x[1])
            return [
                {'nivel': 5, 'mercado': f'Gana {h}', 'prob': ph},
                {'nivel': 5, 'mercado': mejor[0], 'prob': mejor[1]}
            ]
        
        # REGLA 6: Favorito Visitante + Mejor Over
        if pa > 0.50 and ph < 0.40:
            overs = [('Over 1.5', m['over_1_5']), ('Over 2.5', m['over_2_5']), ('Over 3.5', m['over_3_5'])]
            mejor = max(overs, key=lambda x: x[1])
            return [
                {'nivel': 6, 'mercado': f'Gana {a}', 'prob': pa},
                {'nivel': 6, 'mercado': mejor[0], 'prob': mejor[1]}
            ]
        
        # REGLA 7: Default - Mejor Over
        overs = [('Over 1.5', m['over_1_5']), ('Over 2.5', m['over_2_5']), ('Over 3.5', m['over_3_5'])]
        mejor = max(overs, key=lambda x: x[1])
        return [{'nivel': 7, 'mercado': mejor[0], 'prob': mejor[1]}]
    
    def _reglas_nba(self, evento):
        """Reglas específicas para NBA"""
        picks = []
        m = evento.mercados
        
        if m.get('prob_spread', 0) > 0.60:
            picks.append({'nivel': 1, 'mercado': 'Spread', 'prob': m['prob_spread']})
        
        if m.get('prob_over', 0) > 0.60:
            picks.append({'nivel': 2, 'mercado': 'Over', 'prob': m['prob_over']})
        elif m.get('prob_under', 0) > 0.60:
            picks.append({'nivel': 2, 'mercado': 'Under', 'prob': m['prob_under']})
        
        if m.get('prob_home_ml', 0) > 0.65:
            picks.append({'nivel': 3, 'mercado': 'ML Local', 'prob': m['prob_home_ml']})
        elif m.get('prob_away_ml', 0) > 0.65:
            picks.append({'nivel': 3, 'mercado': 'ML Visitante', 'prob': m['prob_away_ml']})
        
        return picks
    
    def _reglas_ufc(self, evento):
        """Reglas específicas para UFC"""
        # Implementar después
        return []
