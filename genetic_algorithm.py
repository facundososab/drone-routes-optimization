# Contiene los operadores genéticos: selección, cruce y mutación.

import random
import config

def crear_individuo():
    """Crea un individuo de doble cromosoma."""
    c_i = list(range(config.NUM_TAREAS))
    random.shuffle(c_i)
    num_cortes = config.NUM_DRONES - 1
    if num_cortes >= config.NUM_TAREAS:
        num_cortes = config.NUM_TAREAS - 1 if config.NUM_TAREAS > 1 else 0
    if num_cortes > 0:
        puntos_de_corte = sorted(random.sample(range(1, config.NUM_TAREAS), num_cortes))
    else:
        puntos_de_corte = []
    c_ii = puntos_de_corte
    return [c_i, c_ii]

def crear_poblacion_inicial():
    """Crea la población inicial."""
    return [crear_individuo() for _ in range(config.TAMANO_POBLACION)]

def seleccion(poblacion, fitness_scores):
    """Selección de padres (elitismo simple)."""
    sorted_population = [x for _, x in sorted(zip(fitness_scores, poblacion), key=lambda pair: pair[0], reverse=True)]
    return sorted_population[:len(poblacion) // 2]

def partial_mapped_crossover(padre1, padre2):
    """Operador de cruce PMX."""
    if padre1 == padre2:
        return padre1, padre2
    size = len(padre1)
    hijo1, hijo2 = [-1]*size, [-1]*size
    start, end = sorted(random.sample(range(size), 2))
    hijo1[start:end+1] = padre1[start:end+1]
    hijo2[start:end+1] = padre2[start:end+1]
    for i in list(range(start)) + list(range(end + 1, size)):
        if padre2[i] not in hijo1:
            hijo1[i] = padre2[i]
        else:
            current_val = padre2[i]
            while current_val in hijo1:
                current_val = padre2[padre1.index(current_val)]
            hijo1[i] = current_val
    for i in list(range(start)) + list(range(end + 1, size)):
        if padre1[i] not in hijo2:
            hijo2[i] = padre1[i]
        else:
            current_val = padre1[i]
            while current_val in hijo2:
                current_val = padre1[padre2.index(current_val)]
            hijo2[i] = current_val
    return hijo1, hijo2

def cruce(padres):
    """Genera descendencia a partir de los padres seleccionados."""
    descendencia = []
    if len(padres) < 2: return padres
    for i in range(0, len(padres) - (len(padres) % 2), 2):
        padre1, padre2 = padres[i], padres[i+1]
        c_i_hijo1, c_i_hijo2 = partial_mapped_crossover(padre1[0], padre2[0])
        corte_cruce = random.randint(0, len(padre1[1])) if len(padre1[1]) > 0 else 0
        c_ii_hijo1 = sorted(padre1[1][:corte_cruce] + padre2[1][corte_cruce:])
        c_ii_hijo2 = sorted(padre2[1][:corte_cruce] + padre1[1][corte_cruce:])
        descendencia.append([c_i_hijo1, c_ii_hijo1])
        descendencia.append([c_i_hijo2, c_ii_hijo2])
    return descendencia

def mutacion(individuo):
    """Operador de mutación por intercambio (swap)."""
    if random.random() < config.PROBABILIDAD_MUTACION:
        c_i = individuo[0]
        idx1, idx2 = random.sample(range(len(c_i)), 2)
        c_i[idx1], c_i[idx2] = c_i[idx2], c_i[idx1]
    return individuo