import random
import config

def tournament_selection(pop, fitnesses, k):
    """Selección por torneo"""
    indices = [random.randint(0, len(pop) - 1) for _ in range(k)]  # lista con k índices aleatorios
    candidatos = [pop[i] for i in indices]
    fitness_candidatos = [fitnesses[i] for i in indices]

    # Ahora mayor fitness = mejor individuo
    mejor_idx = fitness_candidatos.index(max(fitness_candidatos))
    
    return candidatos[mejor_idx]

def buscar_n_mejores(poblacion, fitness_scores, N_BEST):
    """Selección de padres (elitismo simple)."""
    N_MEJORES = min(N_BEST, len(poblacion))  # evita errores porque en caso de haber una población menor a N_BEST toma el menor de los dos
    # Ahora mayor fitness = mejor individuo, ordenar de mayor a menor
    sorted_population = [x for _, x in sorted(zip(fitness_scores, poblacion), key=lambda pair: pair[0], reverse=True)]
    return sorted_population[:N_MEJORES] # Devuelve los N mejores fitness (serían los máximos)
