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
elo.load_ratings()

# Partidos de la captura (con nombres normalizados)
partidos = [
    ('Puebla', 'Tigres UANL'),
    ('Monterrey', 'Querétaro FC'),
    ('Atlas', 'Tijuana'),
    ('América', 'FC Juárez')
]

print('\n ANALIZANDO CADA PARTIDO...\n')

all_picks = []

for local, visitante in partidos:
    print(f'{"="*60}')
    print(f' {local} vs {visitante}')
    print('=' * 60)
    
    # Obtener estadísticas
    local_stats = searcher.get_team_stats(local)
    visit_stats = searcher.get_team_stats(visitante)
    
    # Calcular fuerzas
    home_attack = local_stats.get('avg_goals_scored', 1.35)
    home_defense = local_stats.get('avg_goals_conceded', 1.35)
    away_attack = visit_stats.get('avg_goals_scored', 1.35)
    away_defense = visit_stats.get('avg_goals_conceded', 1.35)
    
    # Ajustes
    home_attack *= 1.1
    away_defense *= 1.05
    
    lambda_home = home_attack * away_defense
    lambda_away = away_attack * home_defense
    
    # Probabilidades ELO
    elo_probs = elo.get_win_probability(local, visitante)
    
    # Analizar todos los mercados
    markets, goal_dist = analyzer.analyze_match(
        local, visitante, lambda_home, lambda_away, elo_probs
    )
    
    print(f'   Goles esperados: {lambda_home:.2f} - {lambda_away:.2f}')
    print(f'   Over 1.5: {next((m["prob"] for m in markets if m["name"]=="Over 1.5"), 0):.1%}')
    print(f'   Over 2.5: {next((m["prob"] for m in markets if m["name"]=="Over 2.5"), 0):.1%}')
    print(f'   BTTS: {next((m["prob"] for m in markets if m["name"]=="BTTS - Sí"), 0):.1%}')
    
    # Crear picks para el optimizador
    odds_map = {
        ('Puebla', 'Tigres UANL'): {'local': 3.70, 'draw': 3.55, 'away': 1.97},
        ('Monterrey', 'Querétaro FC'): {'local': 1.41, 'draw': 4.70, 'away': 7.20},
        ('Atlas', 'Tijuana'): {'local': 2.14, 'draw': 3.45, 'away': 3.30},
        ('América', 'FC Juárez'): {'local': 1.52, 'draw': 3.95, 'away': 6.75},
    }
    
    odds = odds_map.get((local, visitante), {'local': 2.0, 'draw': 3.0, 'away': 3.0})
    
    # Seleccionar mejores mercados por EV
    for market in markets:
        if market['category'] in ['Totales', 'BTTS', '1X2']:
            # Mapear a odds
            if 'Local' in market['name'] and 'y' not in market['name']:
                market_odds = odds['local']
            elif 'Visitante' in market['name'] and 'y' not in market['name']:
                market_odds = odds['away']
            elif 'Empate' in market['name']:
                market_odds = odds['draw']
            elif 'Over' in market['name'] or 'Under' in market['name']:
                # Estimar odds justas
                market_odds = 1 / market['prob'] * 0.95
            elif 'BTTS' in market['name']:
                market_odds = 1 / market['prob'] * 0.95
            else:
                continue
            
            ev = (market['prob'] * market_odds) - 1
            
            if ev > 0.05:  # Solo EV positivo
                all_picks.append({
                    'match': f'{local} vs {visitante}',
                    'selection': market['name'],
                    'prob': market['prob'],
                    'odds': market_odds,
                    'ev': ev,
                    'category': market['category']
                })
                print(f'    {market["name"]}: EV {ev:.1%}')

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
        print(f'       {pick["match"]}: {pick["selection"]} ({pick["prob"]:.1%})')
    
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
