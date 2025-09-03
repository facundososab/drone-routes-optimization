import config
import problem_setup as ps
import genetic_algorithm as ga
import simulation as sim
import visualization as vis

def run_optimization():
    """Función principal que orquesta la optimización."""
    # 1. Generar los datos del problema
    tareas = ps.generar_tareas(config.NUM_TAREAS, config.POLIGONO_ROSARIO)
    drones = ps.generar_drones(config.NUM_DRONES, config.POLIGONO_ROSARIO)
    estaciones = ps.generar_estaciones_carga(config.NUM_ESTACIONES, config.POLIGONO_ROSARIO)

    # 2. Iniciar el algoritmo genético
    poblacion = ga.crear_poblacion_inicial() #Contiene: [[ci,cii], [ci,cii], ...]
    mejor_solucion_global = None
    mejor_fitness_global = -1

    print("--- Iniciando Optimización ---")
    for gen in range(config.NUM_GENERACIONES):
        # Evaluar la población
        fitness_scores = [sim.funcion_fitness(ind, tareas, drones, estaciones) for ind in poblacion]
        
        # Encontrar y guardar la mejor solución
        mejor_fitness_gen = max(fitness_scores)
        if mejor_fitness_gen > mejor_fitness_global:
            mejor_fitness_global = mejor_fitness_gen
            mejor_solucion_global = poblacion[fitness_scores.index(mejor_fitness_gen)]
        
        # Evolucionar la población
        padres = ga.seleccion(poblacion, fitness_scores)
        descendencia = ga.cruce(padres)
        if descendencia:
            poblacion = descendencia + padres[:len(poblacion) - len(descendencia)]
            poblacion = [ga.mutacion(ind) for ind in poblacion]
        
        if (gen + 1) % 10 == 0: 
            print(f"Generación {gen+1}/{config.NUM_GENERACIONES} - Mejor Fitness: {mejor_fitness_global:.6f}")

    print("\n--- Optimización Finalizada ---")
    
    # 3. Mostrar resultados
    if mejor_solucion_global:
        print(f"Mejor solución encontrada.")

        # Decodificar rutas de la mejor solución
        rutas_mejor = sim.decodificar_cromosoma(mejor_solucion_global, tareas, drones)

        for id_dron, tareas_asignadas in rutas_mejor.items():
            print(f"\n--- Recorrido del Dron {id_dron} ---")
            posicion_actual = drones[id_dron]["posicion_inicial"]
            print(f"  Sale desde la base en {posicion_actual}")

            for tarea in tareas_asignadas:
                print(f"\n  -> Iniciando Tarea {tarea['id']}:")
                
                if "recarga_previa" in tarea and tarea["recarga_previa"] is not None:
                    print(f"     1) Va a estación de recarga en {tarea['recarga_previa']}")
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