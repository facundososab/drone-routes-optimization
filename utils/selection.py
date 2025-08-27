import random

def tournament_selection(population, fitnesses, k=3):
    """Selección por torneo"""
    selected = random.sample(list(zip(population, fitnesses)), k)
    selected.sort(key=lambda x: x[1])  # menor energía es mejor
    return selected[0][0] ## Devuelve el individuo con mejor fitness


def elitism_selection(poblacion, fitness_scores):
    """Selección de padres (elitismo simple)."""
    sorted_population = [x for _, x in sorted(zip(fitness_scores, poblacion), key=lambda pair: pair[0], reverse=True)]
    return sorted_population[:len(poblacion) // 2] # Devuelve la mitad superior de la población

