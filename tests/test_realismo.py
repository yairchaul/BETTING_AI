# tests/test_realismo.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
sys.path.append('..')

from modules.pro_analyzer_ultimate import ProAnalyzerUltimate
from modules.value_detector import ValueDetector
from modules.betting_tracker import BettingTracker

def test_realismo(historical_data, initial_bankroll=1000, min_ev=0.05):
    """
    Prueba el sistema con datos históricos reales
    """
    analyzer = ProAnalyzerUltimate()
    detector = ValueDetector()
    tracker = BettingTracker()
    
    results = []
    bankroll = initial_bankroll
    
    for match in historical_data:
        # Simular odds (en datos reales vendrían de la historia)
        odds_data = {'all_odds': [match['home_odd'], match['draw_odd'], match['away_odd']]}
        
        # Analizar partido
        analysis = analyzer.analyze_match(match['home'], match['away'], odds_data)
        
        # Detectar valor
        value = detector.get_best_value_bet(analysis, odds_data, bankroll)
        
        if value and value.get('ev', 0) > min_ev:
            # Apostar (simulado)
            stake = value.get('stake', 50)
            
            # Resultado real (1 = local gana, 0 = empate, 2 = visitante gana)
            if match['result'] == 0 and 'Local' in value['market']:
                profit = stake * (value['decimal_odd'] - 1)
                result_text = 'WIN'
            elif match['result'] == 2 and 'Visitante' in value['market']:
                profit = stake * (value['decimal_odd'] - 1)
                result_text = 'WIN'
            elif match['result'] == 1 and 'Empate' in value['market']:
                profit = stake * (value['decimal_odd'] - 1)
                result_text = 'WIN'
            else:
                profit = -stake
                result_text = 'LOSS'
            
            bankroll += profit
            
            results.append({
                'date': match['date'],
                'match': f"{match['home']} vs {match['away']}",
                'market': value['market'],
                'ev': value['ev'],
                'odds': value['decimal_odd'],
                'stake': stake,
                'result': result_text,
                'profit': profit,
                'bankroll': bankroll
            })
    
    # Calcular métricas
    df = pd.DataFrame(results)
    
    if len(df) == 0:
        print("❌ No se generaron apuestas")
        return
    
    # ROI
    total_staked = df['stake'].sum()
    total_profit = df['profit'].sum()
    roi = (total_profit / total_staked) * 100
    
    # Win rate
    win_rate = (len(df[df['result'] == 'WIN']) / len(df)) * 100
    
    # Sharpe ratio
    returns = df['profit'].values / initial_bankroll
    sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
    
    # Max drawdown
    cumulative = initial_bankroll + df['profit'].cumsum()
    peak = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - peak) / peak * 100
    max_dd = abs(drawdown.min()) if len(drawdown) > 0 else 0
    
    print("=" * 50)
    print("📊 RESULTADOS DEL BACKTESTING")
    print("=" * 50)
    print(f"Apuestas totales: {len(df)}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"ROI: {roi:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd:.1f}%")
    print(f"Bankroll final: ${bankroll:.2f}")
    print("=" * 50)
    
    # Evaluación
    print("\n📈 EVALUACIÓN DE REALISMO:")
    
    if sharpe > 1.0:
        print("🟢 Sharpe Ratio EXCELENTE (>1.0)")
    elif sharpe > 0.5:
        print("🟡 Sharpe Ratio BUENO (>0.5)")
    else:
        print("🔴 Sharpe Ratio BAJO - Modelo no rentable")
    
    if max_dd < 10:
        print("🟢 Riesgo CONTROLADO (<10%)")
    elif max_dd < 20:
        print("🟡 Riesgo MODERADO (10-20%)")
    else:
        print("🔴 Riesgo ALTO (>20%)")
    
    if roi > 20:
        print("🟢 Rentabilidad EXCELENTE (>20%)")
    elif roi > 10:
        print("🟡 Rentabilidad BUENA (10-20%)")
    elif roi > 0:
        print("🟠 Rentabilidad BAJA (0-10%)")
    else:
        print("🔴 SISTEMA NO RENTABLE")
    
    return df
