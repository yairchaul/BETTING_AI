#!/usr/bin/env python3
"""
Motor de razonamiento para parlays - Regla 6 corregida SEGÚN ESPECIFICACIÓN
"""
import numpy as np

class ParlayReasoningEngine:
    """
    Implementa la Regla 6: Comparación de parlays vs picks simples
    PARA EL MISMO PARTIDO
    """
    
    def __init__(self, umbral_principal=0.50):
        self.umbral_principal = umbral_principal  # 50%
        self.umbral_comparacion = 0.45  # 45% para zona de comparación
    
    def evaluar_combinacion_mismo_partido(self, picks_del_partido):
        """
        Evalúa si es mejor combinar picks del MISMO PARTIDO o elegir el mejor simple
        Esta es la implementación correcta de la Regla 6
        
        Args:
            picks_del_partido: Lista de picks para el mismo partido
                              ej: [{'mercado': 'Gana Local', 'prob': 0.48},
                                   {'mercado': 'Over 1.5', 'prob': 0.55}]
        
        Returns:
            Decisión: 'combinado', 'mejor_simple', o 'ninguno'
        """
        if len(picks_del_partido) < 2:
            return {'decision': 'mejor_simple', 'pick': picks_del_partido[0] if picks_del_partido else None}
        
        # Ordenar picks por probabilidad (mejor primero)
        picks_ordenados = sorted(picks_del_partido, key=lambda x: x['prob'], reverse=True)
        
        # El mejor pick simple
        mejor_simple = picks_ordenados[0]
        
        # Intentar combinaciones de 2 picks (las más probables)
        mejores_combinaciones = []
        for i in range(len(picks_ordenados)):
            for j in range(i+1, len(picks_ordenados)):
                prob_combinada = picks_ordenados[i]['prob'] * picks_ordenados[j]['prob']
                
                # Calcular EV si hay odds
                ev_combinado = None
                ev_simple = None
                if 'odds' in mejor_simple and 'odds' in picks_ordenados[i] and 'odds' in picks_ordenados[j]:
                    ev_simple = (mejor_simple['prob'] * mejor_simple['odds']) - 1
                    ev_combinado = (prob_combinada * picks_ordenados[i]['odds'] * picks_ordenados[j]['odds']) - 1
                
                mejores_combinaciones.append({
                    'picks': [picks_ordenados[i], picks_ordenados[j]],
                    'prob_combinada': prob_combinada,
                    'ev_combinado': ev_combinado,
                    'ev_simple': ev_simple
                })
        
        # Ordenar combinaciones por probabilidad
        mejores_combinaciones.sort(key=lambda x: x['prob_combinada'], reverse=True)
        
        if not mejores_combinaciones:
            return {'decision': 'mejor_simple', 'pick': mejor_simple}
        
        mejor_combinacion = mejores_combinaciones[0]
        prob_combinada = mejor_combinacion['prob_combinada']
        
        # APLICAR REGLA 6 SEGÚN ESPECIFICACIÓN
        resultado = {
            'mejor_simple': mejor_simple,
            'mejor_combinacion': mejor_combinacion,
            'prob_combinada': prob_combinada,
            'decision': None,
            'justificacion': ''
        }
        
        # Caso 1: prob_combinada ≥ 50% → MANTENER combinado
        if prob_combinada >= self.umbral_principal:
            resultado['decision'] = 'combinado'
            resultado['justificacion'] = f'Combinado ≥ {self.umbral_principal:.0%} → MANTENER'
            resultado['picks_seleccionados'] = mejor_combinacion['picks']
        
        # Caso 2: prob_combinada < 45% → REEMPLAZAR por mejor simple
        elif prob_combinada < self.umbral_comparacion:
            resultado['decision'] = 'mejor_simple'
            resultado['justificacion'] = f'Combinado < {self.umbral_comparacion:.0%} → usar mejor simple: {mejor_simple["mercado"]} ({mejor_simple["prob"]:.0%})'
            resultado['picks_seleccionados'] = [mejor_simple]
        
        # Caso 3: prob_combinada entre 45% y 50% → COMPARAR y elegir el mayor
        else:
            # Comparar valor esperado si hay odds
            if mejor_combinacion['ev_combinado'] is not None and mejor_combinacion['ev_simple'] is not None:
                if mejor_combinacion['ev_combinado'] > mejor_combinacion['ev_simple']:
                    resultado['decision'] = 'combinado'
                    resultado['justificacion'] = f'Zona gris: mejor EV combinado ({mejor_combinacion["ev_combinado"]:.2%} vs {mejor_combinacion["ev_simple"]:.2%})'
                    resultado['picks_seleccionados'] = mejor_combinacion['picks']
                else:
                    resultado['decision'] = 'mejor_simple'
                    resultado['justificacion'] = f'Zona gris: mejor EV simple ({mejor_combinacion["ev_simple"]:.2%} vs {mejor_combinacion["ev_combinado"]:.2%})'
                    resultado['picks_seleccionados'] = [mejor_simple]
            else:
                # Sin odds, elegir el de mayor probabilidad
                if prob_combinada > mejor_simple['prob']:
                    resultado['decision'] = 'combinado'
                    resultado['justificacion'] = f'Zona gris: prob combinada > mejor simple ({prob_combinada:.2%} vs {mejor_simple["prob"]:.2%})'
                    resultado['picks_seleccionados'] = mejor_combinacion['picks']
                else:
                    resultado['decision'] = 'mejor_simple'
                    resultado['justificacion'] = f'Zona gris: mejor simple tiene mayor prob ({mejor_simple["prob"]:.2%} vs {prob_combinada:.2%})'
                    resultado['picks_seleccionados'] = [mejor_simple]
        
        return resultado
    
    def construir_parlay_por_partido(self, partidos_con_picks):
        """
        Construye parlay aplicando Regla 6 a cada partido individualmente
        
        Args:
            partidos_con_picks: Dict con partido como key y lista de picks como value
                               ej: {'Tottenham vs Arsenal': [pick1, pick2, ...]}
        
        Returns:
            Lista de picks seleccionados (uno por partido)
        """
        picks_finales = []
        
        for partido, picks in partidos_con_picks.items():
            if len(picks) == 1:
                picks_finales.append(picks[0])
                print(f"📌 {partido}: 1 pick → {picks[0]['mercado']} ({picks[0]['prob']:.0%})")
            else:
                resultado = self.evaluar_combinacion_mismo_partido(picks)
                if resultado['decision'] == 'combinado':
                    picks_combinados = resultado['picks_seleccionados']
                    prob_combinada = resultado['prob_combinada']
                    print(f"📌 {partido}: COMBINADO ({len(picks_combinados)} picks) → prob: {prob_combinada:.2%}")
                    for pick in picks_combinados:
                        print(f"      - {pick['mercado']} ({pick['prob']:.0%})")
                    # Para el parlay final, consideramos esto como UNA selección
                    picks_finales.append({
                        'partido': partido,
                        'tipo': 'combinado',
                        'picks': picks_combinados,
                        'prob': prob_combinada,
                        'justificacion': resultado['justificacion']
                    })
                else:
                    pick_elegido = resultado['picks_seleccionados'][0]
                    print(f"📌 {partido}: MEJOR SIMPLE → {pick_elegido['mercado']} ({pick_elegido['prob']:.0%})")
                    picks_finales.append(pick_elegido)
        
        return picks_finales

# Ejemplo de uso
if __name__ == "__main__":
    engine = ParlayReasoningEngine()
    
    print("🔍 PROBANDO REGLA 6 CORREGIDA (POR PARTIDO)")
    print("=" * 70)
    
    # Ejemplo 1: Tottenham vs Arsenal con múltiples picks
    partidos_ejemplo = {
        'Tottenham vs Arsenal': [
            {'partido': 'Tottenham vs Arsenal', 'mercado': 'Gana Tottenham', 'prob': 0.41, 'odds': 2.20},
            {'partido': 'Tottenham vs Arsenal', 'mercado': 'Over 1.5', 'prob': 0.53, 'odds': 1.85},
            {'partido': 'Tottenham vs Arsenal', 'mercado': 'BTTS Sí', 'prob': 0.48, 'odds': 2.10}
        ],
        'Liverpool vs United': [
            {'partido': 'Liverpool vs United', 'mercado': 'BTTS Sí', 'prob': 0.52, 'odds': 1.90},
            {'partido': 'Liverpool vs United', 'mercado': 'Over 2.5', 'prob': 0.55, 'odds': 1.88}
        ],
        'Real Madrid vs Barcelona': [
            {'partido': 'Real Madrid vs Barcelona', 'mercado': 'Gana Real Madrid', 'prob': 0.48, 'odds': 2.10}
        ]
    }
    
    print("\n📊 ANALIZANDO PARTIDOS:")
    print("-" * 70)
    
    picks_finales = engine.construir_parlay_por_partido(partidos_ejemplo)
    
    print("\n" + "=" * 70)
    print("🎯 PARLAY FINAL (1 pick por partido):")
    print("-" * 70)
    
    for pick in picks_finales:
        if pick.get('tipo') == 'combinado':
            print(f"📦 {pick['partido']}: COMBINADO")
            for p in pick['picks']:
                print(f"      - {p['mercado']} ({p['prob']:.0%})")
            print(f"      Prob total: {pick['prob']:.2%}")
        else:
            print(f"🎯 {pick['partido']}: {pick['mercado']} ({pick['prob']:.0%})")
    
    # Calcular probabilidad total del parlay
    prob_parlay = np.prod([p['prob'] if 'prob' in p else p.get('prob_combinada', 1) for p in picks_finales])
    print(f"\n📊 PROBABILIDAD TOTAL PARLAY: {prob_parlay:.2%}")
