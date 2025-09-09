# Contiene los operadores genéticos: selección, cruce y mutación.
import random
import config
import utils.crossover as crossover
import utils.selection as selection
import utils.mutation as mutation
import simulation as sim

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

def roulette_wheel_selection(pop, fitnesses):
    """Selección por ruleta"""
    #El fitness más alto implica mejor solución (menor energía)
    total = sum(fitnesses)
    if total == 0:
        # Evitar división por cero: seleccionar aleatorio uniforme
        return random.choice(pop)

    # Normalización
    probs = [f / total for f in fitnesses]

    # Probabilidades acumuladas
    probs_acumuladas, acum = [], 0
    for prob in probs:
        acum += prob
        probs_acumuladas.append(acum)

    for _ in range(len(pop)):
        r = random.random()
        for i in range(len(probs_acumuladas)):
            if r <= probs_acumuladas[i]:
                seleccionado = (pop[i])
                break
            #Sino, vuelve al ciclo y sigue buscando a quien le corresponde el número aleatorio
    return seleccionado

def generar_individuos_opuestos(P, num_tareas):
    """Genera la población opuesta POPP a partir de P usando Opposition-Based Learning."""
    POPP = []
    for (c_i, c_ii) in P:
        ci_opuesto = [(num_tareas - 1) - gene for gene in c_i]
        opuesto = [ci_opuesto, c_ii] 
        POPP.append(opuesto)
    return POPP



def crear_poblacion_total(poblacion_previa, tareas, drones, estaciones):
    """Crea la población total."""
    POPP= generar_individuos_opuestos(poblacion_previa, config.NUM_TAREAS)

    fitnesses_candidatos = [
            sim.funcion_fitness(ind, tareas, drones, estaciones)[0]  # me quedo solo con el fitness
            for ind in (poblacion_previa + POPP)
        ]
    
    elite = selection.buscar_n_mejores((poblacion_previa + POPP), fitnesses_candidatos,config.N_BEST) #permitimos que los individuos de elite se dupliquen en la poblacion

    poblacion_total = elite.copy()
    while len(poblacion_total) < config.TAMANO_POBLACION:
        individuo_restante = roulette_wheel_selection((poblacion_previa + POPP), fitnesses_candidatos)
        poblacion_total.append(individuo_restante)

    return poblacion_total

def crear_poblacion_inicial():
    return [crear_individuo() for _ in range(config.TAMANO_POBLACION)]


def seleccion(poblacion, fitness_scores):
    """Selecciona padres usando selección por torneo y elitismo."""
    padres = []
    for _ in range(config.TAMANO_POBLACION):
        padre = selection.tournament_selection(poblacion, fitness_scores, k=(config.TAMANO_POBLACION // 5))
        padres.append(padre)
    
    #VER ESTE CASO
    # if config.TAMANO_POBLACION % 2 == 1: # Si es impar, seleccionamos un padre extra
    #     padre_extra = selection.tournament_selection(poblacion, fitness_scores, k=(config.TAMANO_POBLACION // 5))
    #     padres.append(padre_extra)

    return padres


def cruce(padres):
    """Genera descendencia a partir de los padres seleccionados."""
    descendencia = []
    if len(padres) < 2: return padres

    for i in range(0, len(padres) - (len(padres) % 2), 2):
        padre1, padre2 = padres[i], padres[(i+1) % (len(padres))] #Se seleccionan los padres contiguos. En caso de que len(padres) sea impar, la operación módulo (% len(padres)) asegura que se toma el último padre junto con el primero del array (porque el módulo devuelve 0).

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
        print("ocurre mutacion")
        if random.random() < 0.7: # 70% de probabilidad de hacer un swap simple
            c_i = mutation.swap_mutation(c_i)
        else: # 30% de probabilidad de hacer una inversión más disruptiva
            c_i = mutation.reverse_segment(c_i)
            
    # 2. Mutar Cromosoma II (Asignación a Drones)
    # Se usa una probabilidad diferente para no alterar la asignación tan a menudo
    if random.random() < config.PROBABILIDAD_MUTACION:
        c_ii = mutation.cuts_mutation(c_ii, config.NUM_TAREAS)
        
    return [c_i, c_ii]

