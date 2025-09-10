import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
import problem_setup as ps
import genetic_algorithm as ga
import simulation as sim
import numpy as np
from plotting import plot_fitness_evolution
import visualization as vis
import random
from config import TIEMPO_MIN_MIN, TIEMPO_MAX_MIN

def generar_tareas(num_tareas, poligono):
    """Genera la lista de tareas."""
    pickups = [[-32.95725661118796, -60.664089752558695], [-32.957177017243424, -60.66344776867995], [-32.96272183853973, -60.66912792002945], [-32.95402077807787, -60.636839227537216], [-32.93771002752342, -60.67211530315638]]
    dropoffs = [[-32.96257969995565, -60.67041521218382], [-32.939790781520344, -60.67356570157502], [-32.92648716696396, -60.67168846440852], [-32.959862113511015, -60.63135871248699], [-32.944088634078604, -60.67536088272771]]
    return [{
        "id": i,
        "pickup": pickups[i],
        "dropoff": dropoffs[i],
        "peso": 1, # en kilos
        "tiempo_max": random.randint(TIEMPO_MIN_MIN * 60, TIEMPO_MAX_MIN * 60),  # en segundos
        "recarga_previa": None,
    } for i in range(num_tareas)]
    
def generar_drones(num_drones, poligono):
    """Genera la lista de drones con sus bases."""
    posiciones = [[-32.9545, -60.6355], [-32.9556, -60.6340]]
    return [{"id": i, "posicion_inicial": posiciones[i]} for i in range(num_drones)]

def run_optimization():
    """Función principal que orquesta la optimización."""
    # 1. Generar los datos del problema
    tareas = generar_tareas(5, config.POLIGONO_ROSARIO)
    drones = ps.generar_drones(2, config.POLIGONO_ROSARIO)
    estaciones = [[-32.9545, -60.6355], [-32.9556, -60.6340]]

    # 2. Iniciar el algoritmo genético
    poblacion = ga.crear_poblacion_inicial() #Contiene: [[ci,cii], [ci,cii], ...]
    mejor_solucion_global = None
    mejor_energia_global = -1
    energia_mejor_anterior = None
    mejor_generacion = 0  # Rastrear la mejor generación

    # Listas para guardar el historial del fitness
    max_fitness_history = []
    avg_fitness_history = []
    min_fitness_history = []

    # Parámetros de parada flexibles
    nmax = config.NUM_GENERACIONES
    epsilon = config.EPSILON
    nconv = getattr(config, 'NCONV', 20) # Si no existe, usa 20                                                                                                          
    contador_convergencia = 0
    print("--- Iniciando Optimización ---")
    for gen in range(nmax):
        # Procesar generación completa: POPP → crossover/mutación → fitness → P'
        poblacion = ga.procesar_generacion(poblacion, tareas, drones, estaciones)

        # Calcular energías y fitness de la nueva población para estadísticas
        energias = [sim.funcion_objetivo(ind, tareas, drones, estaciones) for ind in poblacion]
        fitness_normalizados = ga.obtener_fitnesses(energias)

        print(f"Fitnesses normalizados: {[f'{f:.6f}' for f in fitness_normalizados[:5]]}")
        if all(f == 0 for f in fitness_normalizados):
            print("Todos los individuos tuvieron consumo de energia = 0 (IMPOSIBLE)")
           

        # Guardar datos para el gráfico
        max_fitness_history.append(np.max(fitness_normalizados))
        avg_fitness_history.append(np.mean(fitness_normalizados))
        min_fitness_history.append(np.min(fitness_normalizados))

        # Encontrar y guardar la mejor solución (menor energía)
        idx_mejor = energias.index(min(energias))  # El mejor es el de MENOR energía
        energia_mejor = energias[idx_mejor]
        mejor_fitness_gen = fitness_normalizados[idx_mejor]
        print("Mejor energía generación:", energia_mejor)
        mejora_energia = abs(energia_mejor - energia_mejor_anterior) if energia_mejor_anterior is not None else config.PENALTY_VALUE
        #Cuando el fitness es 0, la energia es infinita --> Porque energia infinita penaliza.

        # Criterio de convergencia: comparar con la generación anterior
        if mejora_energia > epsilon:
            mejor_energia_global = energia_mejor
            mejor_generacion = gen + 1  # Guardamos la generación (1-indexada)
            print (f"Generación {gen+1}: Nueva mejor energía encontrada: {mejor_energia_global:.2f} (Fitness: {mejor_fitness_gen:.6f})")
            mejor_solucion_global = poblacion[idx_mejor]
            contador_convergencia = 0
        else:
            contador_convergencia += 1
        energia_mejor_anterior = energia_mejor

        print(f"Generación {gen+1}/{nmax} - Mejor Fitness: {mejor_fitness_gen} - Mejor Energía: {energia_mejor:.2f}")
        if contador_convergencia >= nconv:
            print(f"Convergencia alcanzada en la generación {gen+1}. Diferencia de energía: {mejora_energia:.4e} < {epsilon} por {contador_convergencia} generaciones.")
            break

    print("\n--- Optimización Finalizada ---")
    
    
    # Generar y guardar el gráfico de evolución
    if max_fitness_history:
        plot_fitness_evolution(
            max_fitness_history,
            avg_fitness_history,
            min_fitness_history,
            len(max_fitness_history),
            mejor_generacion  # Pasamos la generación de la mejor solución
        )

    # 3. Mostrar resultados
    if mejor_solucion_global:
        print(f"🏆 Mejor solución encontrada en la Generación {mejor_generacion}")
        print(f"   Energía: {mejor_energia_global:.2f} J")

        # Decodificar rutas de la mejor solución
        rutas_mejor = sim.decodificar_cromosoma(mejor_solucion_global, tareas, drones)

        for id_dron, id_tareas_asignadas in rutas_mejor.items():
            print(f"\n--- Recorrido del Dron {id_dron} ---")
            posicion_actual = drones[id_dron]["posicion_inicial"]
            print(f"  Sale desde la base en {posicion_actual}")

            for id_tarea in id_tareas_asignadas:
                tarea = tareas[id_tarea] # Se obtiene la tarea original
                print(f"\n  -> Iniciando Tarea {tarea['id']}:")
                
                if tarea.get("recarga_previa") is not None:
                    print(f"     1) Va a estación de recarga previa en {tarea['recarga_previa']}")
                    posicion_actual = tarea["recarga_previa"]

                print(f"     2) Va al Pickup en {tarea['pickup']}")
                posicion_actual = tarea["pickup"]

                print(f"     3) Va al Dropoff en {tarea['dropoff']}")
                posicion_actual = tarea["dropoff"]

            print(f"\n  *** Dron {id_dron} termina en {posicion_actual} ***")

    # Visualización en el mapa
        vis.visualizar_rutas(mejor_solucion_global, tareas, drones, config.POLIGONO_ROSARIO, estaciones, config)
    else:
        print("No se encontró una solución válida.")

if __name__ == "__main__":
    run_optimization()