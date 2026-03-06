import streamlit as st
from modules.smart_searcher import SmartSearcher
from modules.elo_system import ELOSystem
from modules.complete_market_analyzer import CompleteMarketAnalyzer
from modules.parlay_optimizer_pro import ParlayOptimizerPro
import numpy as np

print(' GENERANDO PARLAY PROFESIONAL CON DATOS REALES')
print('=' * 70)

# Inicializar componentes
searcher = SmartSearcher()
elo = ELOSystem()
analyzer = CompleteMarketAnalyzer()
optimizer = ParlayOptimizerPro(bankroll=1000)

# Cargar ratings ELO
try:
    elo.load_ratings()
except:
    print(' No se pudieron cargar ratings ELO, usando valores por defecto')

# Partidos de la captura con sus odds REALES
partidos = [
    {
        'local': 'Puebla',
        'visitante': 'Tigres UANL',
        'odds_local': 3.70,
        'odds_draw': 3.55,
        'odds_visit': 1.97
    },
    {
        'local': 'Monterrey',
        'visitante': 'Querétaro FC',
        'odds_local': 1.41,
        'odds_draw': 4.70,
        'odds_visit': 7.20
    },
    {
        'local': 'Atlas',
        'visitante': 'Tijuana',
        'odds_local': 2.14,
        'odds_draw': 3.45,
        'odds_visit': 3.30
    },
    {
        'local': 'América',
        'visitante': 'FC Juárez',
        'odds_local': 1.52,
        'odds_draw': 3.95,
        'odds_visit': 6.75
    }
]

print('\n ANALIZANDO CADA PARTIDO...\n')

all_picks = []

for p in partidos:
    local = p['local']
    visitante = p['visitante']
    odds_local = p['odds_local']
    odds_draw = p['odds_draw']
    odds_visit = p['odds_visit']
    
    print(f'{"="*60}')
    print(f' {local} vs {visitante}')
    print('=' * 60)
    
    # Obtener estadísticas específicas de cada equipo
    local_stats = searcher.get_team_stats(local)
    visit_stats = searcher.get_team_stats(visitante)
    
    # DEBUG: Mostrar estadísticas obtenidas
    print(f'   Stats {local}: {local_stats}')
    print(f'   Stats {visitante}: {visit_stats}')
    
    # Calcular fuerzas (usar datos reales si existen, sino promedios)
    home_attack = local_stats.get('avg_goals_scored', 1.35)
    home_defense = local_stats.get('avg_goals_conceded', 1.35)
    away_attack = visit_stats.get('avg_goals_scored', 1.35)
    away_defense = visit_stats.get('avg_goals_conceded', 1.35)
    
    # Ajustes por localía
    home_attack *= 1.1
    home_defense *= 0.95
    away_attack *= 0.95
    away_defense *= 1.05
    
    # Calcular λ específicos para ESTE partido
    lambda_home = home_attack * away_defense
    lambda_away = away_attack * home_defense
    
    print(f'   Goles esperados: Local {lambda_home:.2f} - Visitante {lambda_away:.2f}')
    
    # Probabilidades ELO
    elo_probs = elo.get_win_probability(local, visitante)
    print(f'   ELO: Local {elo_probs["home"]:.1%}, Empate {elo_probs["draw"]:.1%}, Visitante {elo_probs["away"]:.1%}')
    
    # Analizar todos los mercados
    markets, goal_dist = analyzer.analyze_match(
        local, visitante, lambda_home, lambda_away, elo_probs
    )
    
    # Mostrar probabilidades clave
    btts_prob = next((m['prob'] for m in markets if m['name'] == 'BTTS - Sí'), 0)
    over1_5 = next((m['prob'] for m in markets if m['name'] == 'Over 1.5'), 0)
    over2_5 = next((m['prob'] for m in markets if m['name'] == 'Over 2.5'), 0)
    
    print(f'   BTTS: {btts_prob:.1%}')
    print(f'   Over 1.5: {over1_5:.1%}')
    print(f'   Over 2.5: {over2_5:.1%}')
    
    # ============================================================================
    # MAPEO CORRECTO DE MERCADOS A ODDS
    # ============================================================================
    mercados_con_odds = [
        # Mercados 1X2
        {
            'name': 'Gana Local',
            'prob': elo_probs['home'],
            'odds': odds_local,
            'category': '1X2',
            'match': f'{local} vs {visitante}'
        },
        {
            'name': 'Empate',
            'prob': elo_probs['draw'],
            'odds': odds_draw,
            'category': '1X2',
            'match': f'{local} vs {visitante}'
        },
        {
            'name': 'Gana Visitante',
            'prob': elo_probs['away'],
            'odds': odds_visit,
            'category': '1X2',
            'match': f'{local} vs {visitante}'
        },
        # Mercados BTTS
        {
            'name': 'BTTS - Sí',
            'prob': btts_prob,
            'odds': 1 / btts_prob * 0.95 if btts_prob > 0 else 0,
            'category': 'BTTS',
            'match': f'{local} vs {visitante}'
        },
        {
            'name': 'BTTS - No',
            'prob': 1 - btts_prob,
            'odds': 1 / (1 - btts_prob) * 0.95 if (1 - btts_prob) > 0 else 0,
            'category': 'BTTS',
            'match': f'{local} vs {visitante}'
        },
        # Mercados Totales
        {
            'name': 'Over 1.5',
            'prob': over1_5,
            'odds': 1 / over1_5 * 0.95 if over1_5 > 0 else 0,
            'category': 'Totales',
            'match': f'{local} vs {visitante}'
        },
        {
            'name': 'Under 1.5',
            'prob': 1 - over1_5,
            'odds': 1 / (1 - over1_5) * 0.95 if (1 - over1_5) > 0 else 0,
            'category': 'Totales',
            'match': f'{local} vs {visitante}'
        },
        {
            'name': 'Over 2.5',
            'prob': over2_5,
            'odds': 1 / over2_5 * 0.95 if over2_5 > 0 else 0,
            'category': 'Totales',
            'match': f'{local} vs {visitante}'
        },
        {
            'name': 'Under 2.5',
            'prob': 1 - over2_5,
            'odds': 1 / (1 - over2_5) * 0.95 if (1 - over2_5) > 0 else 0,
            'category': 'Totales',
            'match': f'{local} vs {visitante}'
        }
    ]
    
    # Calcular EV para cada mercado
    for m in mercados_con_odds:
        if m['odds'] > 0:
            m['ev'] = (m['prob'] * m['odds']) - 1
            if m['ev'] > 0.05:  # Solo EV positivo
                all_picks.append(m)
                print(f'    {m["name"]}: Prob {m["prob"]:.1%}, Odds {m["odds"]:.2f}, EV {m["ev"]:.1%}')

# Optimizar parlay
print('\n OPTIMIZANDO PARLAY...')
best_parlay = optimizer.find_best_parlay(all_picks, max_size=3)

if best_parlay:
    print('\n MEJOR PARLAY ENCONTRADO:')
    print(f'   Probabilidad total: {best_parlay["prob_total"]:.1%}')
    print(f'   Odds totales: {best_parlay["odds_total"]:.2f}')
    print(f'   EV total: {best_parlay["ev_total"]:.1%}')
    print(f'   Stake sugerido: ')
    
    print('\n   Selecciones:')
    for pick in best_parlay['picks']:
        print(f'       {pick["match"]}: {pick["name"]} ({pick["prob"]:.1%}) [EV: {pick["ev"]:.1%}]')
    
    # Análisis de riesgo
    risk = optimizer.analyze_parlay_risk(best_parlay)
    if risk:
        print(f'\n Análisis de riesgo:')
        print(f'   Probabilidad de ganar: {risk["win_prob"]:.1%}')
        print(f'   Retorno esperado: ')
        print(f'   VaR 95%: ')
        print(f'   Ratio Sharpe: {risk["sharpe_ratio"]:.2f}')
else:
    print(' No se encontró parlay con EV positivo')

print('\n' + '=' * 70)
