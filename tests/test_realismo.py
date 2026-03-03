# tests/test_realismo.py
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Añadir el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.pro_analyzer_ultimate import ProAnalyzerUltimate
from modules.value_detector import ValueDetector
from modules.elo_system import ELOSystem
from modules.montecarlo_pro import MonteCarloPro

class RealismoTester:
    """
    Suite completa de pruebas de realismo para el sistema de apuestas
    """
    
    def __init__(self, initial_bankroll=1000):
        self.analyzer = ProAnalyzerUltimate()
        self.detector = ValueDetector()
        self.elo = ELOSystem()
        self.montecarlo = MonteCarloPro()
        self.initial_bankroll = initial_bankroll
        self.results = []
    
    def prepare_match_data(self, historical_matches):
        """
        Prepara datos históricos para simulación
        """
        processed = []
        
        for match in historical_matches:
            # Convertir odds si están disponibles
            if match.get('odds'):
                home_odd = match['odds'].get('home', 2.0)
                draw_odd = match['odds'].get('draw', 3.0)
                away_odd = match['odds'].get('away', 3.5)
            else:
                # Odds estimadas basadas en resultado
                if match['resultado'] == 0:  # local gana
                    home_odd, draw_odd, away_odd = 1.8, 3.5, 4.5
                elif match['resultado'] == 1:  # empate
                    home_odd, draw_odd, away_odd = 2.8, 2.0, 3.2
                else:  # visitante gana
                    home_odd, draw_odd, away_odd = 4.0, 3.5, 1.9
            
            processed.append({
                'date': match['date'],
                'home': match['home_team'],
                'away': match['away_team'],
                'home_odd': home_odd,
                'draw_odd': draw_odd,
                'away_odd': away_odd,
                'result': match['resultado'],
                'league': match.get('league', 'Desconocida'),
                'season': match.get('season', '2024')
            })
        
        return processed
    
    def run_backtest(self, historical_data, min_ev=0.05, stake_fraction=0.25):
        """
        Ejecuta backtesting completo
        """
        processed_data = self.prepare_match_data(historical_data)
        
        results = []
        bankroll = self.initial_bankroll
        bankroll_history = [bankroll]
        
        for match in processed_data:
            # Crear odds_data para el analizador
            odds_data = {
                'all_odds': [
                    self._decimal_to_american(match['home_odd']),
                    self._decimal_to_american(match['draw_odd']),
                    self._decimal_to_american(match['away_odd'])
                ]
            }
            
            # Analizar partido
            analysis = self.analyzer.analyze_match(match['home'], match['away'], odds_data)
            
            # Detectar valor
            value = self.detector.get_best_value_bet(analysis, odds_data, bankroll)
            
            if value and value.get('ev', 0) > min_ev:
                # Calcular stake según Kelly
                stake = self.detector.calculate_kelly_stake(
                    value['market_prob'], 
                    value['decimal_odd'], 
                    bankroll, 
                    stake_fraction
                )
                
                # Determinar resultado
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
                    'league': match['league'],
                    'market': value['market'],
                    'ev': value['ev'],
                    'prob': value['market_prob'],
                    'odds': value['decimal_odd'],
                    'stake': stake,
                    'result': result_text,
                    'profit': profit,
                    'bankroll': bankroll
                })
            
            bankroll_history.append(bankroll)
        
        # Calcular métricas
        metrics = self._calculate_metrics(results, bankroll_history)
        
        return {
            'results': results,
            'metrics': metrics,
            'bankroll_history': bankroll_history
        }
    
    def _decimal_to_american(self, decimal):
        """Convierte odds decimales a americanas (aproximación)"""
        if decimal >= 2.0:
            return f"+{int((decimal - 1) * 100)}"
        else:
            return f"-{int(100 / (decimal - 1))}"
    
    def _calculate_metrics(self, results, bankroll_history):
        """Calcula todas las métricas de rendimiento"""
        if not results:
            return {}
        
        df = pd.DataFrame(results)
        
        # ROI
        total_staked = df['stake'].sum()
        total_profit = df['profit'].sum()
        roi = (total_profit / total_staked) * 100 if total_staked > 0 else 0
        
        # Win rate
        wins = len(df[df['result'] == 'WIN'])
        total_bets = len(df)
        win_rate = (wins / total_bets) * 100 if total_bets > 0 else 0
        
        # Sharpe Ratio
        returns = np.diff(bankroll_history) / bankroll_history[:-1]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        
        # Max Drawdown
        bankroll_array = np.array(bankroll_history)
        peak = np.maximum.accumulate(bankroll_array)
        drawdown = (bankroll_array - peak) / peak * 100
        max_drawdown = abs(np.min(drawdown))
        
        # Profit Factor
        total_wins = df[df['result'] == 'WIN']['profit'].sum()
        total_losses = abs(df[df['result'] == 'LOSS']['profit'].sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # EV promedio
        avg_ev = df['ev'].mean()
        
        # Calmar Ratio (ROI / Max Drawdown)
        calmar = roi / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'total_bets': total_bets,
            'wins': wins,
            'win_rate': win_rate,
            'total_staked': total_staked,
            'total_profit': total_profit,
            'roi': roi,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'avg_ev': avg_ev,
            'calmar_ratio': calmar,
            'final_bankroll': bankroll_history[-1]
        }
    
    def plot_results(self, results):
        """Genera gráficos de resultados"""
        if not results or not results.get('results'):
            print("No hay resultados para graficar")
            return
        
        df = pd.DataFrame(results['results'])
        bankroll = results['bankroll_history']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Evolución del bankroll
        axes[0, 0].plot(bankroll, color='blue', linewidth=2)
        axes[0, 0].axhline(y=1000, color='gray', linestyle='--', label='Bankroll inicial')
        axes[0, 0].set_title('Evolución del Bankroll')
        axes[0, 0].set_xlabel('Apuesta #')
        axes[0, 0].set_ylabel('Bankroll ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Distribución de EV
        axes[0, 1].hist(df['ev'], bins=20, color='green', alpha=0.7, edgecolor='black')
        axes[0, 1].axvline(x=0.05, color='red', linestyle='--', label='Umbral EV')
        axes[0, 1].set_title('Distribución de EV')
        axes[0, 1].set_xlabel('EV')
        axes[0, 1].set_ylabel('Frecuencia')
        axes[0, 1].legend()
        
        # Resultados por liga
        if 'league' in df.columns:
            league_stats = df.groupby('league').agg({
                'profit': ['sum', 'count'],
                'ev': 'mean'
            }).round(2)
            
            axes[1, 0].bar(league_stats.index, league_stats[('profit', 'sum')], color='orange')
            axes[1, 0].set_title('Profit por Liga')
            axes[1, 0].set_xlabel('Liga')
            axes[1, 0].set_ylabel('Profit ($)')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Drawdown
        bankroll_array = np.array(bankroll)
        peak = np.maximum.accumulate(bankroll_array)
        drawdown = (bankroll_array - peak) / peak * 100
        
        axes[1, 1].fill_between(range(len(drawdown)), drawdown, 0, color='red', alpha=0.3)
        axes[1, 1].set_title('Drawdown')
        axes[1, 1].set_xlabel('Apuesta #')
        axes[1, 1].set_ylabel('Drawdown (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def print_report(self, results):
        """Imprime reporte detallado"""
        if not results or not results.get('metrics'):
            print("❌ No hay resultados para reportar")
            return
        
        m = results['metrics']
        
        print("\n" + "=" * 60)
        print("📊 REPORTE DE BACKTESTING".center(60))
        print("=" * 60)
        
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Apuestas totales: {m['total_bets']}")
        print(f"   • Apuestas ganadas: {m['wins']}")
        print(f"   • Win Rate: {m['win_rate']:.2f}%")
        print(f"   • Total apostado: ${m['total_staked']:.2f}")
        print(f"   • Profit total: ${m['total_profit']:.2f}")
        
        print(f"\n📊 MÉTRICAS DE RENDIMIENTO:")
        print(f"   • ROI: {m['roi']:.2f}%")
        print(f"   • Sharpe Ratio: {m['sharpe_ratio']:.3f}")
        print(f"   • Profit Factor: {m['profit_factor']:.3f}")
        print(f"   • Calmar Ratio: {m['calmar_ratio']:.3f}")
        
        print(f"\n⚠️  MÉTRICAS DE RIESGO:")
        print(f"   • Max Drawdown: {m['max_drawdown']:.2f}%")
        print(f"   • EV Promedio: {m['avg_ev']:.2%}")
        print(f"   • Bankroll final: ${m['final_bankroll']:.2f}")
        
        print("\n" + "=" * 60)
        
        # Evaluación
        print("\n🎯 EVALUACIÓN DE REALISMO:")
        
        if m['sharpe_ratio'] > 1.0:
            print("   🟢 Sharpe Ratio EXCELENTE (>1.0)")
        elif m['sharpe_ratio'] > 0.5:
            print("   🟡 Sharpe Ratio BUENO (>0.5)")
        else:
            print("   🔴 Sharpe Ratio BAJO - Modelo no rentable")
        
        if m['max_drawdown'] < 10:
            print("   🟢 Riesgo CONTROLADO (<10%)")
        elif m['max_drawdown'] < 20:
            print("   🟡 Riesgo MODERADO (10-20%)")
        else:
            print("   🔴 Riesgo ALTO (>20%)")
        
        if m['roi'] > 20:
            print("   🟢 Rentabilidad EXCELENTE (>20%)")
        elif m['roi'] > 10:
            print("   🟡 Rentabilidad BUENA (10-20%)")
        elif m['roi'] > 0:
            print("   🟠 Rentabilidad BAJA (0-10%)")
        else:
            print("   🔴 SISTEMA NO RENTABLE")
        
        print("=" * 60)

# Función principal para ejecutar pruebas
def run_complete_test(data_collector, leagues=['Mexico Liga MX', 'England Premier League'], 
                     seasons=['2024', '2023'], min_ev=0.05):
    """
    Ejecuta prueba completa con múltiples ligas
    """
    tester = RealismoTester(initial_bankroll=1000)
    all_matches = []
    
    for league in leagues:
        print(f"\n📥 Recolectando datos de {league}...")
        league_id = data_collector.get_league_id(league)
        
        if league_id:
            for season in seasons:
                matches = data_collector.get_historical_matches(league_id, season, limit=200)
                for match in matches:
                    match['league'] = league
                all_matches.extend(matches)
                print(f"   ✅ {len(matches)} partidos de {season}")
    
    print(f"\n📊 Total de partidos recolectados: {len(all_matches)}")
    
    if len(all_matches) < 100:
        print("❌ Insuficientes datos para backtesting")
        return
    
    # Ejecutar backtesting con diferentes umbrales
    results = {}
    for ev in [0.03, 0.05, 0.08]:
        print(f"\n🎯 Probando con umbral EV = {ev:.0%}")
        result = tester.run_backtest(all_matches, min_ev=ev)
        results[ev] = result
        tester.print_report(result)
    
    return results
