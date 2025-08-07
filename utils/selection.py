import random

def tournament_selection(population, fitnesses, k=3):
    """Selección por torneo"""
    selected = random.sample(list(zip(population, fitnesses)), k)
    selected.sort(key=lambda x: x[1])  # menor energía es mejor
    return selected[0][0]
