import config
import problem_setup as ps
import genetic_algorithm as ga
import simulation as sim
import visualization as vis
import numpy as np
from plotting import plot_fitness_evolution, plot_energia_evolution

def run_optimization():
    """Función principal que orquesta la optimización."""
    # 1. Generar los datos del problema
    tareas = ps.generar_tareas(config.NUM_TAREAS, config.POLIGONO_ROSARIO)
    drones = ps.generar_drones(config.NUM_DRONES, config.POLIGONO_ROSARIO)
    estaciones = config.ESTACIONES_DE_CARGA[:config.NUM_ESTACIONES]  # Usar las estaciones predefinidas en config.py

    # 2. Iniciar el algoritmo genético
    poblacion = ga.crear_poblacion_inicial() #Contiene: [[ci,cii], [ci,cii], ...]
    mejor_solucion_global = None
    mejor_energia_global = float("inf")
    #energia_mejor_anterior = None
    mejor_generacion = 0  # Rastrear la mejor generación

    # Listas para guardar el historial del fitness
    max_fitness_history = []
    avg_fitness_history = []
    min_fitness_history = []

    max_energias_history = []
    avg_energias_history = []
    min_energias_history = []

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
        print(f"Generación {gen+1}: Max Fitness = {max_fitness_history[-1]:.6f}")
        avg_fitness_history.append(np.mean(fitness_normalizados))
        min_fitness_history.append(np.min(fitness_normalizados))

        max_energias_history.append(np.max(energias))
        avg_energias_history.append(np.mean(energias))
        min_energias_history.append(np.min(energias))
        print(f"Generación {gen+1}: Min Energía = {min_energias_history[-1]:.2f}")

        # Encontrar y guardar la mejor solución (menor energía)
        idx_mejor = energias.index(min(energias))  # El mejor es el de MENOR energía
        energia_mejor = energias[idx_mejor]
        #print("Mejor energía generación:", energia_mejor)

        if energia_mejor < mejor_energia_global:  
            mejor_energia_global = energia_mejor
            mejor_solucion_global = poblacion[idx_mejor]
            mejor_generacion = gen + 1 #La mejor generacion es la de menor energia, pero esta a veces no coincide con la de mayor fitness
        

    print("\n--- Optimización Finalizada ---")
    
    
    # Generar y guardar los gráficos de evolución para distintas métricas
    if max_fitness_history:
        plot_fitness_evolution(
            max_fitness_history,
            avg_fitness_history,
            min_fitness_history,
            len(max_fitness_history),
            mejor_generacion
        )
    if max_energias_history:
        plot_energia_evolution(
            max_energias_history,
            avg_energias_history,
            min_energias_history,
            len(min_energias_history),
            mejor_generacion
        )

    # 3. Mostrar resultados
    if mejor_solucion_global:
        print(f"🏆 Mejor solución encontrada en la Generación {mejor_generacion}")
        print(f"   Energía: {mejor_energia_global:.2f} J")

        # Decodificar rutas de la mejor solución
        rutas_mejor = sim.decodificar_cromosoma(mejor_solucion_global, drones)

        for id_dron, id_tareas_asignadas in rutas_mejor.items():
            print(f"\n--- Recorrido del Dron {id_dron} ---")
            posicion_actual = drones[id_dron]["posicion_inicial"]
            print(f"  Sale desde la base en {posicion_actual}")

            for id_tarea in id_tareas_asignadas:
                tarea = tareas[id_tarea]  # Se obtiene la tarea original
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
        print("❌ No se encontró una solución válida.")

if __name__ == "__main__":
    run_optimization()