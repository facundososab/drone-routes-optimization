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
    mejor_energia_global = -1
    energia_mejor_anterior = None

    # Parámetros de parada flexibles
    nmax = config.NUM_GENERACIONES
    epsilon = config.EPSILON
    nconv = getattr(config, 'NCONV', 20)        # Si no existe, usa 20
    contador_convergencia = 0
    print("--- Iniciando Optimización ---")
    for gen in range(nmax):
        # Evaluar la población
        resultados = [sim.funcion_fitness(ind, tareas, drones, estaciones) for ind in poblacion]
        fitness_scores = [r[0] for r in resultados]
        energias = [r[1] for r in resultados]

        # Encontrar y guardar la mejor solución
        mejor_fitness_gen = max(fitness_scores)
        print("Mejor fitness generación:", mejor_fitness_gen)
        idx_mejor = fitness_scores.index(mejor_fitness_gen)
        energia_mejor = energias[idx_mejor]
        mejora_energia = abs(energia_mejor - energia_mejor_anterior) if energia_mejor_anterior is not None else float('inf')

        # Criterio de convergencia: comparar con la generación anterior
        if mejora_energia > epsilon:
            mejor_energia_global = energia_mejor
            print (f"Generación {gen+1}: Nueva mejor energía encontrada: {mejor_energia_global:.2f} (Fitness: {mejor_fitness_gen:.6f})")
            mejor_solucion_global = poblacion[idx_mejor]
            contador_convergencia = 0
        else:
            contador_convergencia += 1
        energia_mejor_anterior = energia_mejor

        # Evolucionar la población
        padres = ga.seleccion(poblacion, fitness_scores)
        descendencia = ga.cruce(padres)
        if descendencia:
            poblacion = descendencia + padres[:len(poblacion) - len(descendencia)]
            poblacion = [ga.mutacion(ind) for ind in poblacion]

        print(f"Generación {gen+1}/{nmax} - Mejor Fitness: {mejor_fitness_gen} - Mejor Energía: {energia_mejor:.2f}")
        if contador_convergencia >= nconv:
            print(f"Convergencia alcanzada en la generación {gen+1}. Diferencia de energía: {mejora_energia:.4f} < {epsilon} por {contador_convergencia} generaciones.")
            break

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
                
                if tarea["recarga_previa"] is not None:
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