class RuleEngine:
    """
    Motor de reglas universal.
    Toma un evento enriquecido y aplica las reglas jerárquicas.
    """
    
    def ejecutar(self, evento):
        """
        Ejecuta las reglas según el deporte y devuelve los picks.
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
        """LAS 6 REGLAS DE FÚTBOL (tu código original)"""
        picks = []
        m = evento.mercados
        
        # REGLA 1: Over 1.5 Primer Tiempo > 60%
        if m.get('over_1_5_1t', 0) > 0.60:
            picks.append({
                'nivel': 1,
                'mercado': 'Over 1.5 1T',
                'prob': m['over_1_5_1t'],
                'justificacion': 'Regla 1: Over 1.5 1T dominante'
            })
            return picks
        
        # REGLA 2: Over 3.5 > 60% + Favorito > 55%
        if m.get('over_3_5', 0) > 0.60:
            if m.get('prob_local', 0) > 0.55:
                picks.append({'nivel': 2, 'mercado': f'Gana {evento.local}', 'prob': m['prob_local']})
                picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': m['over_3_5']})
                return picks
            if m.get('prob_visitante', 0) > 0.55:
                picks.append({'nivel': 2, 'mercado': f'Gana {evento.visitante}', 'prob': m['prob_visitante']})
                picks.append({'nivel': 2, 'mercado': 'Over 3.5', 'prob': m['over_3_5']})
                return picks
        
        # REGLA 3: BTTS > 60%
        if m.get('btts_yes', 0) > 0.60:
            picks.append({
                'nivel': 3,
                'mercado': 'BTTS Sí',
                'prob': m['btts_yes']
            })
            return picks
        
        # REGLA 4: Mejor Over (cercano a 55%)
        if m.get('prob_local', 0) < 0.55 and m.get('prob_visitante', 0) < 0.55:
            overs = [
                ('Over 1.5', m['over_1_5']),
                ('Over 2.5', m['over_2_5']),
                ('Over 3.5', m['over_3_5'])
            ]
            overs_validos = [(n, p) for n, p in overs if p > 0.55]
            if overs_validos:
                mejor = min(overs_validos, key=lambda x: abs(x[1] - 0.55))
                picks.append({'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]})
            else:
                mejor = max(overs, key=lambda x: x[1])
                picks.append({'nivel': 4, 'mercado': mejor[0], 'prob': mejor[1]})
            return picks
        
        # REGLA 5: Favorito Local + Over
        if m.get('prob_local', 0) > 0.50 and m.get('prob_visitante', 0) < 0.40:
            picks.append({'nivel': 5, 'mercado': f'Gana {evento.local}', 'prob': m['prob_local']})
            overs = [('Over 1.5', m['over_1_5']), ('Over 2.5', m['over_2_5']), ('Over 3.5', m['over_3_5'])]
            mejor = max(overs, key=lambda x: x[1])
            picks.append({'nivel': 5, 'mercado': mejor[0], 'prob': mejor[1]})
            return picks
        
        # REGLA 6: Favorito Visitante + Over
        if m.get('prob_visitante', 0) > 0.50 and m.get('prob_local', 0) < 0.40:
            picks.append({'nivel': 6, 'mercado': f'Gana {evento.visitante}', 'prob': m['prob_visitante']})
            overs = [('Over 1.5', m['over_1_5']), ('Over 2.5', m['over_2_5']), ('Over 3.5', m['over_3_5'])]
            mejor = max(overs, key=lambda x: x[1])
            picks.append({'nivel': 6, 'mercado': mejor[0], 'prob': mejor[1]})
            return picks
        
        # Default: Mejor Over
        overs = [('Over 1.5', m['over_1_5']), ('Over 2.5', m['over_2_5']), ('Over 3.5', m['over_3_5'])]
        mejor = max(overs, key=lambda x: x[1])
        picks.append({'nivel': 7, 'mercado': mejor[0], 'prob': mejor[1]})
        return picks
    
    def _reglas_nba(self, evento):
        """Reglas para NBA (ejemplo)"""
        picks = []
        m = evento.mercados
        if m.get('spread_cover', 0) > 0.60:
            picks.append({'nivel': 1, 'mercado': 'Spread favorito', 'prob': m['spread_cover']})
        return picks
    
    def _reglas_ufc(self, evento):
        """Reglas para UFC (ejemplo)"""
        picks = []
        m = evento.mercados
        if m.get('prob_local', 0) > 0.65:
            picks.append({'nivel': 1, 'mercado': f'Gana {evento.local}', 'prob': m['prob_local']})
        return picks
