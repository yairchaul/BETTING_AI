# modules/parlay_optimizer.py
import numpy as np
import pandas as pd
import streamlit as st
from itertools import combinations
import random

class ParlayOptimizer:
    """
    Optimizador de parlays usando teoría de portafolios
    Basado en Optimal Bets [citation:6] y algoritmos genéticos [citation:9]
    """
    
    def __init__(self):
        self.generation = 0
    
    def find_optimal_parlays(self, available_picks, max_size=4, target_odds=3.0, population_size=50):
        """
        Encuentra parlays óptimos usando algoritmo genético
        """
        if len(available_picks) < 2:
            return []
        
        # Población inicial
        population = self._initialize_population(available_picks, max_size, population_size)
        
        # Evolución (simplificada)
        best_fitness = 0
        best_parlay = None
        
        for generation in range(10):  # 10 generaciones
            # Evaluar fitness
            fitness_scores = []
            for parlay in population:
                fitness = self._calculate_fitness(parlay, target_odds)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_parlay = parlay
            
            # Selección (torneo)
            selected = self._tournament_selection(population, fitness_scores)
            
            # Cruce y mutación
            next_population = []
            for i in range(0, len(selected), 2):
                if i+1 < len(selected):
                    child1, child2 = self._crossover(selected[i], selected[i+1])
                    next_population.append(self._mutate(child1, available_picks))
                    next_population.append(self._mutate(child2, available_picks))
            
            population = next_population[:population_size]
        
        return best_parlay
    
    def _initialize_population(self, picks, max_size, size):
        """Crea población inicial aleatoria"""
        population = []
        for _ in range(size):
            n_picks = random.randint(2, max_size)
            parlay = random.sample(picks, min(n_picks, len(picks)))
            population.append(parlay)
        return population
    
    def _calculate_fitness(self, parlay, target_odds):
        """Calcula fitness de un parlay"""
        if not parlay or len(parlay) < 2:
            return 0
        
        # Probabilidad total
        prob_total = np.prod([p.get('prob', 0.5) for p in parlay])
        
        # Cuota total
        odds_total = np.prod([p.get('odd', 2.0) for p in parlay])
        
        # EV (Valor Esperado)
        ev = (prob_total * odds_total) - 1
        
        # Cercanía a odds objetivo (si se especifica)
        odds_distance = 1 - abs(odds_total - target_odds) / target_odds if target_odds else 1
        
        # Diversificación (penalizar mercados similares)
        categories = [p.get('category', '') for p in parlay]
        unique_cats = len(set(categories))
        diversity = unique_cats / len(parlay) if parlay else 0
        
        # Fitness combinado
        fitness = (ev * 0.5) + (odds_distance * 0.3) + (diversity * 0.2)
        
        return max(0, fitness)
    
    def _tournament_selection(self, population, fitness_scores, tournament_size=3):
        """Selección por torneo"""
        selected = []
        for _ in range(len(population)):
            # Seleccionar torneo_size individuos al azar
            indices = random.sample(range(len(population)), min(tournament_size, len(population)))
            # Elegir el mejor del torneo
            best_idx = indices[0]
            for idx in indices[1:]:
                if fitness_scores[idx] > fitness_scores[best_idx]:
                    best_idx = idx
            selected.append(population[best_idx])
        return selected
    
    def _crossover(self, parent1, parent2):
        """Cruza dos padres para crear hijos"""
        if len(parent1) < 2 or len(parent2) < 2:
            return parent1, parent2
        
        # Punto de cruce aleatorio
        point1 = random.randint(1, len(parent1)-1)
        point2 = random.randint(1, len(parent2)-1)
        
        child1 = parent1[:point1] + parent2[point2:]
        child2 = parent2[:point2] + parent1[point1:]
        
        return child1, child2
    
    def _mutate(self, parlay, available_picks, mutation_rate=0.2):
        """Muta un parlay"""
        if random.random() > mutation_rate:
            return parlay
        
        if not parlay:
            return parlay
        
        # Mutación: reemplazar un pick
        idx = random.randint(0, len(parlay)-1)
        new_pick = random.choice(available_picks)
        parlay[idx] = new_pick
        
        return parlay
    
    def calculate_kelly_stake(self, prob, odds, bankroll, fraction=0.25):
        """
        Calcula stake óptimo usando Kelly Criterion [citation:6]
        """
        # Fórmula de Kelly: f = (bp - q) / b
        # donde b = odds - 1, p = prob, q = 1-p
        b = odds - 1
        if b <= 0:
            return 0
        
        p = prob
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Kelly fraccionado para reducir riesgo
        optimal_stake = bankroll * kelly_fraction * fraction
        
        return max(0, min(optimal_stake, bankroll * 0.1))  # Máximo 10% del bankroll
    
    def efficient_frontier(self, parlays, bankroll=1000):
        """
        Calcula la frontera eficiente de parlays (Sharpe Ratio) [citation:6]
        """
        results = []
        for parlay in parlays:
            if len(parlay) < 2:
                continue
            
            prob_total = np.prod([p.get('prob', 0.5) for p in parlay])
            odds_total = np.prod([p.get('odd', 2.0) for p in parlay])
            
            expected_return = (prob_total * odds_total) - 1
            risk = 1 - prob_total  # riesgo aproximado
            
            sharpe = expected_return / risk if risk > 0 else 0
            
            results.append({
                'parlay': parlay,
                'prob': prob_total,
                'odds': odds_total,
                'expected_return': expected_return,
                'risk': risk,
                'sharpe': sharpe,
                'stake': self.calculate_kelly_stake(prob_total, odds_total, bankroll)
            })
        
        # Ordenar por Sharpe Ratio
        return sorted(results, key=lambda x: x['sharpe'], reverse=True)