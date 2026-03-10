#!/usr/bin/env python3
"""
Script para probar la Regla 6 corregida
"""
from modules.parlay_reasoning_engine import ParlayReasoningEngine

def main():
    print("🔍 PROBANDO REGLA 6 CORREGIDA")
    print("=" * 60)
    
    engine = ParlayReasoningEngine()
    
    # Caso 1: Tottenham (41%) + Over 1.5 (53%)
    picks1 = [
        {'partido': 'Tottenham vs Arsenal', 'mercado': 'Gana Tottenham', 'prob': 0.41, 'odds': 2.20},
        {'partido': 'Tottenham vs Arsenal', 'mercado': 'Over 1.5', 'prob': 0.53, 'odds': 1.85}
    ]
    
    print("\n📊 CASO 1: Tottenham (41%) + Over 1.5 (53%)")
    print(f"   Pick A: Gana Tottenham (prob: {picks1[0]['prob']:.0%}, odds: {picks1[0]['odds']})")
    print(f"   Pick B: Over 1.5 (prob: {picks1[1]['prob']:.0%}, odds: {picks1[1]['odds']})")
    
    resultado1 = engine.evaluar_combinacion(picks1[0], picks1[1])
    prob_combinada = picks1[0]['prob'] * picks1[1]['prob']
    print(f"\n   📈 Probabilidad combinada: {prob_combinada:.2%}")
    print(f"   ✅ Decisión: {resultado1['decision']}")
    print(f"   📝 Justificación: {resultado1['justificacion']}")
    
    # Caso 2: Ambos picks >50%
    picks2 = [
        {'partido': 'Liverpool vs United', 'mercado': 'BTTS Sí', 'prob': 0.52, 'odds': 1.90},
        {'partido': 'Liverpool vs United', 'mercado': 'Over 2.5', 'prob': 0.55, 'odds': 1.88}
    ]
    
    print("\n" + "=" * 60)
    print("\n📊 CASO 2: Ambos picks >50%")
    print(f"   Pick A: BTTS Sí (prob: {picks2[0]['prob']:.0%}, odds: {picks2[0]['odds']})")
    print(f"   Pick B: Over 2.5 (prob: {picks2[1]['prob']:.0%}, odds: {picks2[1]['odds']})")
    
    resultado2 = engine.evaluar_combinacion(picks2[0], picks2[1])
    prob_combinada2 = picks2[0]['prob'] * picks2[1]['prob']
    print(f"\n   📈 Probabilidad combinada: {prob_combinada2:.2%}")
    print(f"   ✅ Decisión: {resultado2['decision']}")
    print(f"   📝 Justificación: {resultado2['justificacion']}")
    
    # Caso 3: Un pick <45%
    picks3 = [
        {'partido': 'Real Madrid vs Barcelona', 'mercado': 'Gana Real Madrid', 'prob': 0.44, 'odds': 2.10},
        {'partido': 'Real Madrid vs Barcelona', 'mercado': 'Over 2.5', 'prob': 0.51, 'odds': 1.92}
    ]
    
    print("\n" + "=" * 60)
    print("\n📊 CASO 3: Pick bajo (44%) + pick normal (51%)")
    print(f"   Pick A: Gana Real Madrid (prob: {picks3[0]['prob']:.0%}, odds: {picks3[0]['odds']})")
    print(f"   Pick B: Over 2.5 (prob: {picks3[1]['prob']:.0%}, odds: {picks3[1]['odds']})")
    
    resultado3 = engine.evaluar_combinacion(picks3[0], picks3[1])
    prob_combinada3 = picks3[0]['prob'] * picks3[1]['prob']
    print(f"\n   📈 Probabilidad combinada: {prob_combinada3:.2%}")
    print(f"   ✅ Decisión: {resultado3['decision']}")
    print(f"   📝 Justificación: {resultado3['justificacion']}")

if __name__ == "__main__":
    main()
