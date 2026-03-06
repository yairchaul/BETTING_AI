# parlay_real.py
import streamlit as st
from modules.smart_searcher import SmartSearcher
from modules.elo_system import ELOSystem
from modules.pro_analyzer_ultimate import ProAnalyzerUltimate
from modules.parlay_optimizer import ParlayOptimizer
import numpy as np

print('🎯 GENERANDO PARLAY CON DATOS REALES')
print('=' * 70)

# Inicializar componentes
searcher = SmartSearcher()
elo = ELOSystem()
analyzer = ProAnalyzerUltimate()
optimizer = ParlayOptimizer()

# Cargar ratings ELO existentes
elo.load_ratings()

# Partidos de la captura (con nombres normalizados)
partidos = [
    ('Puebla', 'Tigres UANL'),
    ('Monterrey', 'Querétaro FC'),
    ('Atlas', 'Tijuana'),
    ('América', 'FC Juárez')
]

print('\n ANALIZANDO PARTIDOS CON DATOS REALES...\n')

all_picks = []
bankroll = 1000  #  de bankroll simulado

for local, visitante in partidos:
    print(f'{"="*50}')
    print(f' {local} vs {visitante}')
    print('=' * 50)
    
    # 1. Obtener IDs y estadísticas reales
    local_id = searcher.get_team_id(local)
    visit_id = searcher.get_team_id(visitante)
    
    print(f'   IDs: {local}={local_id}, {visitante}={visit_id}')
    
    # 2. Obtener estadísticas
    local_stats = searcher.get_team_stats(local)
    visit_stats = searcher.get_team_stats(visitante)
    
    print(f'    Goles promedio: {local}={local_stats["avg_goals_scored"]:.2f}, {visitante}={visit_stats["avg_goals_scored"]:.2f}')
    
    # 3. Probabilidades ELO
    elo_probs = elo.get_win_probability(local, visitante)
    print(f'    ELO: Local {elo_probs["home"]:.1%}, Empate {elo_probs["draw"]:.1%}, Visitante {elo_probs["away"]:.1%}')
    
    # 4. Calcular BTTS dinámico (fórmula Poisson)
    lambda_local = local_stats['avg_goals_scored'] * 1.1
    lambda_visit = visit_stats['avg_goals_scored']
    
    from math import exp
    prob_home_zero = exp(-lambda_local)
    prob_away_zero = exp(-lambda_visit)
    btts_prob = (1 - prob_home_zero) * (1 - prob_away_zero)
    
    print(f'    BTTS: {btts_prob:.1%}')
    
    # 5. Generar picks para el optimizador
    picks_partido = [
        {
            'match': f'{local} vs {visitante}',
            'selection': f'Gana {local}',
            'prob': elo_probs['home'],
            'odd': 1/elo_probs['home'] * 0.95,  # Odds justas con margen
            'category': '1X2',
            'ev': 0
        },
        {
            'match': f'{local} vs {visitante}',
            'selection': 'BTTS - Sí',
            'prob': btts_prob,
            'odd': 1/btts_prob * 0.95,
            'category': 'BTTS',
            'ev': 0
        }
    ]
    
    # Calcular EV para cada pick
    for pick in picks_partido:
        pick['ev'] = (pick['prob'] * pick['odd']) - 1
        print(f'    {pick["selection"]}: Prob {pick["prob"]:.1%}, Odd {pick["odd"]:.2f}, EV {pick["ev"]:.1%}')
    
    all_picks.extend(picks_partido)
    print()

# 6. Optimizar parlay
print('\n OPTIMIZANDO PARLAY...')
optimal = optimizer.find_optimal_parlays(all_picks, max_size=4, target_ev=0.05)

if optimal and 'picks' in optimal:
    prob_parlay = np.prod([p['prob'] for p in optimal['picks']])
    odds_parlay = np.prod([p['odd'] for p in optimal['picks']])
    ev_parlay = (prob_parlay * odds_parlay) - 1
    
    print('\n PARLAY ENCONTRADO:')
    print(f'    Probabilidad total: {prob_parlay:.1%}')
    print(f'    Cuota total: {odds_parlay:.2f}')
    print(f'    EV total: {ev_parlay:.1%}')
    print(f'    Stake sugerido (Kelly): ')
    
    print('\n   Selecciones:')
    for pick in optimal['picks']:
        print(f'       {pick["match"]}: {pick["selection"]} ({pick["prob"]:.1%})')
else:
    print(' No se encontró parlay con EV positivo')

print('\n' + '=' * 70)
