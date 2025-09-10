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

def crear_poblacion_inicial():
    return [crear_individuo() for _ in range(config.TAMANO_POBLACION)]


def generar_poblacion_opuesta(P, num_tareas):
    """Genera la población opuesta POPP a partir de P usando Opposition-Based Learning."""
    POPP = []
    for (c_i, c_ii) in P:
        ci_opuesto = [(num_tareas - 1) - gene for gene in c_i]
        opuesto = [ci_opuesto, c_ii] 
        POPP.append(opuesto)
    return POPP



def procesar_generacion(poblacion_P, tareas, drones, estaciones):
    """
    Procesa una generación completa siguiendo la secuencia estándar:
    1. Crear población opuesta (POPP)
    2. Aplicar crossover y mutación a P y POPP
    3. Evaluar fitness de P y POPP procesados
    4. Crear población descendiente P' usando esos fitness
    """
    
    # Paso 1: Crear población opuesta
    POPP = generar_poblacion_opuesta(poblacion_P, config.NUM_TAREAS)
    
    # Paso 2: Aplicar crossover y mutación a P y POPP
    print("Aplicando crossover y mutación a P...")
    P_procesada = aplicar_operadores_geneticos(poblacion_P)
    
    print("Aplicando crossover y mutación a POPP...")
    POPP_procesada = aplicar_operadores_geneticos(POPP)

    
    # Paso 3: Evaluar fitness de P y POPP procesados
    poblacion_total_procesada = P_procesada + POPP_procesada
    
    energias_totales = []
    for ind in poblacion_total_procesada:
        print("Individuo a evaluar:", ind)
        energias_totales.append(sim.funcion_objetivo(ind, tareas, drones, estaciones))
        
    # energias_totales = [sim.funcion_objetivo(ind, tareas, drones, estaciones) for ind in poblacion_total_procesada]
    fitness_totales = obtener_fitnesses(energias_totales)
    
    # Encontrar el individuo con el mejor fitness
    mejor_fitness = max(fitness_totales)
    indice_mejor = fitness_totales.index(mejor_fitness)
    mejor_individuo = poblacion_total_procesada[indice_mejor]

    print(f"El mejor individuo es: {mejor_individuo} con un fitness de: {mejor_fitness}")
    
    # Paso 4: Crear población descendiente P' usando los fitness calculados
    P_prima = crear_poblacion_descendiente_con_fitness(
        P_procesada, POPP_procesada, 
        poblacion_total_procesada, fitness_totales
    )
    
    return P_prima


def aplicar_operadores_geneticos(poblacion):
    """
    Aplica crossover y mutación a una población.
    """
    # Selección de padres para crossover
    fitness_temp = [1.0 / len(poblacion)] * len(poblacion)  # Fitness uniforme temporal para selección
    padres = seleccion(poblacion, fitness_temp)
    
    # Aplicar crossover
    descendencia = cruce(padres)
    
    # Aplicar mutación
    poblacion_procesada = [mutacion(ind) for ind in descendencia]
    
    return poblacion_procesada


def crear_poblacion_descendiente_con_fitness(P_procesada, POPP_procesada, poblacion_total, fitness_totales):
    """
    Crea la población descendiente P' usando los fitness ya calculados:
    1. Fusión: mitad de P, mitad de POPP
    2. Inclusión de élite basada en fitness
    3. Selección por ruleta del resto
    4. Mantenimiento del tamaño
    """
    
    # 1. Fusión: selección aleatoria de mitades
    mitad_tamano = config.TAMANO_POBLACION // 2
    
    # Seleccionar aleatoriamente mitad de P procesada
    if len(P_procesada) > 0:
        indices_P = random.sample(range(len(P_procesada)), min(mitad_tamano, len(P_procesada)))
        individuos_de_P = [P_procesada[i] for i in indices_P]
    else:
        individuos_de_P = []
    
    # Seleccionar aleatoriamente mitad de POPP procesada  
    if len(POPP_procesada) > 0:
        indices_POPP = random.sample(range(len(POPP_procesada)), min(mitad_tamano, len(POPP_procesada)))
        individuos_de_POPP = [POPP_procesada[i] for i in indices_POPP]
    else:
        individuos_de_POPP = []
    
    # Población descendiente inicial
    poblacion_descendiente = individuos_de_P + individuos_de_POPP
    
    # 2. Inclusión de individuos élite de la población total
    elite = selection.buscar_n_mejores(poblacion_total, fitness_totales, config.N_BEST)
    
    # Agregar élite que no esté ya en la descendencia
    for individuo_elite in elite:
        if individuo_elite not in poblacion_descendiente:
            poblacion_descendiente.append(individuo_elite)
    
    # 3. Selección por ruleta para completar hasta TAMANO_POBLACION
    while len(poblacion_descendiente) < config.TAMANO_POBLACION:
        individuo_ruleta = roulette_wheel_selection(poblacion_total, fitness_totales)
        poblacion_descendiente.append(individuo_ruleta)
    
    # 4. Truncar si excede el tamaño
    if len(poblacion_descendiente) > config.TAMANO_POBLACION:
        poblacion_descendiente = poblacion_descendiente[:config.TAMANO_POBLACION]
    
    return poblacion_descendiente


def roulette_wheel_selection(pop, fitnesses):
    """Selección por ruleta"""
    # Ahora los fitness ya están correctos: mayor fitness = mejor individuo
    
    if not pop or not fitnesses:
        return random.choice(pop) if pop else None
    
    total = sum(fitnesses)
    if total == 0:
        # Caso extremo: todos los individuos tienen fitness 0
        return random.choice(pop)
    
    # Los fitness ya están normalizados, así que son directamente probabilidades
    probs = fitnesses  # Ya normalizados en obtener_fitnesses
    
    # Crear probabilidades acumuladas
    probs_acumuladas, acum = [], 0
    for p in probs:
        acum += p
        probs_acumuladas.append(acum)

    r = random.random()
    seleccionado = pop[-1]  # Por defecto, seleccionar el último individuo
    
    for i in range(len(probs_acumuladas)):
        if r <= probs_acumuladas[i]:
            seleccionado = pop[i]
            break
    
    return seleccionado



def obtener_fitnesses(funcion_objetivo_values):
    """
    Calcula fitness normalizados para problema de minimización.
    Menor energía → Mayor fitness (mejor individuo)
    """
    EPS = 1e-9  # Para evitar división por cero
    
    # Transformar energías a fitness usando inverso
    # Menor energía → Mayor fitness
    fitness_values = [1.0 / (f + EPS) for f in funcion_objetivo_values]
    
    # Normalizar para que sumen 1
    total = sum(fitness_values)
    if total > 0:
        fitness_values = [f / total for f in fitness_values]
    else:
        # Caso extremo: todos fitness infinitos, asignar igual probabilidad
        fitness_values = [1.0 / len(funcion_objetivo_values)] * len(funcion_objetivo_values)
    
    # Debugging
    print("Sumatoria de fitness (debe dar 1):", sum(fitness_values))
    print(f"Energías: min={min(funcion_objetivo_values):.2f}, max={max(funcion_objetivo_values):.2f}")
    print(f"Fitness: min={min(fitness_values):.6f}, max={max(fitness_values):.6f}")
    
    return fitness_values



def seleccion(poblacion, fitness_scores):
    """Selecciona padres usando selección por torneo y elitismo."""
    if all(f == 0 for f in fitness_scores):
        # Si todos los fitness son 0 --> Devuelve padres inviables al azar
        return [random.choice(poblacion) for _ in range(config.TAMANO_POBLACION)]


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
