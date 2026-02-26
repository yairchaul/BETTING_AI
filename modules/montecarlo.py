import random

def simulate_parlay(picks, simulations=500):

    wins = 0

    for _ in range(simulations):

        success = True

        for p in picks:
            if random.random() > (p.probabilidad/100):
                success = False
                break

        if success:
            wins += 1

    return round((wins/simulations)*100,2)
