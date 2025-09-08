# Contiene los operadores genéticos: selección, cruce y mutación.
import random
import config
import utils.crossover as crossover
import utils.selection as selection
import utils.mutation as mutation

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
    """Selecciona padres usando selección por torneo y elitismo."""
    padres = selection.elitism_selection(poblacion, fitness_scores)
    while len(padres) < len(poblacion) // 2:
        padre = selection.tournament_selection(poblacion, fitness_scores, k=3)
        if padre not in padres:
            padres.append(padre)
    return padres


def cruce(padres):
    """Genera descendencia a partir de los padres seleccionados."""
    descendencia = []
    if len(padres) < 2: return padres
    for i in range(0, len(padres) - (len(padres) % 2), 2):
        padre1, padre2 = padres[i], padres[i+1]
        if random.random() < config.PROBABILIDAD_CRUCE:
            c_i_hijo1, c_i_hijo2 = crossover.pmx(padre1[0], padre2[0])
            corte_cruce = random.randint(0, len(padre1[1])) if len(padre1[1]) > 0 else 0
            c_ii_hijo1 = sorted(padre1[1][:corte_cruce] + padre2[1][corte_cruce:])
            c_ii_hijo2 = sorted(padre2[1][:corte_cruce] + padre1[1][corte_cruce:])
            descendencia.append([c_i_hijo1, c_ii_hijo1])
            descendencia.append([c_i_hijo2, c_ii_hijo2])
        else:
            # --- No se cruzan, se copian los padres ---
            descendencia.append((padre1))
            descendencia.append((padre2))
    return descendencia

def mutacion(individuo):
    """
    Orquesta la mutación para ambos cromosomas (orden y cortes)
    con probabilidades independientes.
    """
    c_i, c_ii = individuo
    
    # 1. Mutar Cromosoma I (Orden de Tareas)
    if random.random() < config.PROBABILIDAD_MUTACION:
        # Elige aleatoriamente entre swap o inversión para variar la estrategia
        if random.random() < 0.7: # 70% de probabilidad de hacer un swap simple
            c_i = mutation.swap_mutation(c_i)
        else: # 30% de probabilidad de hacer una inversión más disruptiva
            c_i = mutation.reverse_segment(c_i)
            
    # 2. Mutar Cromosoma II (Asignación a Drones)
    # Se usa una probabilidad diferente para no alterar la asignación tan a menudo
    if random.random() < config.PROBABILIDAD_MUTACION:
        c_ii = mutation.cuts_mutation(c_ii, config.NUM_TAREAS)
        
    return [c_i, c_ii]

