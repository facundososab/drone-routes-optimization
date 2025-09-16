import random
import config
import problem_setup as ps
import genetic_algorithm as ga
import simulation as sim
import visualization as vis
import numpy as np
from plotting import plot_fitness_evolution, plot_energia_evolution
import pandas as pd
import os

energias_corridas = []
tiempos_medio_entrega_corridas = []
parametros_inviables_corridas = []

def run_optimization(params=None, verbose=True):
    """
    Corre una optimización con parámetros específicos (si params != None).
    Devuelve un dict con KPIs de la corrida.
    """
    if params:
        # Override dinámico de parámetros
        for key, value in params.items():
            setattr(config, key, value)
            if verbose:
                print(f"[CONFIG] {key} = {value}")
    
    # 1. Generar los datos del problema
    tareas = ps.generar_tareas(config.NUM_TAREAS, config.POLIGONO_ROSARIO)
    drones = ps.generar_drones(config.NUM_DRONES, config.POLIGONO_ROSARIO)
    estaciones = config.ESTACIONES_DE_CARGA[:config.NUM_ESTACIONES]  # Usar las estaciones predefinidas en config.py

    # 2. Iniciar el algoritmo genético
    poblacion = ga.crear_poblacion_inicial() #Contiene: [[ci,cii], [ci,cii], ...]
    mejor_individuo_global = None
    mejor_generacion = 0  # Rastrear la mejor generación
    
    #Para normalización global del fitness
    energia_menor_global = 0 #El limite mínimo de un individuo viable es > 0
    energia_mayor_global = 50e6 # El limite máximo es arbitrario. Se supone que en MJ no consumiran mas de 5MJ
    mejor_energia_global = float('inf') #Para almacenar la mejor energia global de los individuos
    tareas_con_estaciones_carga_mejor = None #Las tareas del mejor individuo que incluyen las recargas previas

    # Listas para guardar el historial del fitness
    max_fitness_history = []
    avg_fitness_history = []
    min_fitness_history = []

    max_energias_history = []
    avg_energias_history = []
    min_energias_history = []

    nmax = config.NUM_GENERACIONES

    print("--- Iniciando Optimización ---")
    for gen in range(nmax):
        # Procesar generación completa: POPP → crossover/mutación → fitness → P'
        poblacion, parametros_inviables = ga.procesar_generacion(poblacion, tareas, drones, estaciones)
        #Acá los individuos que llegan son todos viables
        #Acá las funciones fitness implementadas deben ser locales --> Los individuos compiten por ser seleccionados ante sus propios compañeros, no ante los globales.
        if parametros_inviables is True:
            break  # Si hay parámetros inviables, salir de la corrida
        # Calcular energías y fitness de la nueva población para estadísticas
        #energias es un array de floats, pero tareas_con_estaciones_carga tiene que llegar como un único array de diccionarios, no varios arrays
        resultados = [sim.funcion_objetivo(ind, tareas, drones, estaciones) for ind in poblacion]
        energias = [energia for energia, _ in resultados]
        tareas_con_estaciones_carga = [tareas_mod for _, tareas_mod in resultados] #Array de arrays con diccionarios. Son Las tareas de cada individuo de la generación
        
        print(f"Energías de la población: {[f'{e:.2e}' for e in energias[:5]]} ...")
        #Las energias se suponen que son viables
        if any(e <= 0 for e in energias):
            print("Error: Se encontró una energía no positiva en la población que se pasará a la siguiente iteración (IMPOSIBLE)")
            break
        
        fitness_globales = ga.obtener_fitnesses_global(energias, energia_menor_global, energia_mayor_global)

        print(f"Fitnesses normalizados: {[f'{f:.6e}' for f in fitness_globales[:5]]}")
        if all(f == 0 for f in fitness_globales):
            print("Todos los individuos tuvieron consumo de energia = 0 (IMPOSIBLE)")
           

        # Guardar datos para el gráfico
        max_fitness_history.append(np.max(fitness_globales))
        print(f"Generación {gen+1}: Max Fitness = {max_fitness_history[-1]:.6e}")
        avg_fitness_history.append(np.mean(fitness_globales))
        min_fitness_history.append(np.min(fitness_globales))

        max_energias_history.append(np.max(energias))
        avg_energias_history.append(np.mean(energias))
        min_energias_history.append(np.min(energias))
        print(f"Generación {gen+1}: Min Energía = {min_energias_history[-1]:.2e}")

        # Encontrar y guardar la mejor solución (menor energía)
        idx_mejor = energias.index(min(energias))  # El mejor es el de MENOR energía
        energia_mejor = energias[idx_mejor]
        #print("Mejor energía generación:", energia_mejor)

        if energia_mejor <= mejor_energia_global:  
            mejor_energia_global = energia_mejor
            mejor_individuo_global = poblacion[idx_mejor]
            #Reemplazar las tareas globales por las locales del mejor individuo
            mejor_generacion = gen + 1 
            tareas_con_estaciones_carga_mejor = tareas_con_estaciones_carga[idx_mejor]

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
    if mejor_individuo_global:
        print(f"🏆 Mejor solución encontrada en la Generación {mejor_generacion}")
        print(f"   Energía: {mejor_energia_global:.2e} J")
        print(f"   Cromosoma: {mejor_individuo_global}")
        print(f"Tareas: {tareas}")
        print(f"Drones: {drones}")
        print(f"Estaciones: {estaciones}")

        # # Decodificar rutas de la mejor solución
        # #rutas_mejor = sim.decodificar_cromosoma(mejor_individuo_global, drones)

        # # for id_dron, id_tareas_asignadas in rutas_mejor.items():
        # #     print(f"\n--- Recorrido del Dron {id_dron} ---")
        # #     posicion_actual = drones[id_dron]["posicion_inicial"]
        # #     print(f"  Sale desde la base en {posicion_actual}")

        # #     for id_tarea in id_tareas_asignadas:
        # #         tarea = tareas[id_tarea]  # Se obtiene la tarea original
        # #         print(f"\n  -> Iniciando Tarea {tarea['id']}:")

        # #         if tarea.get("recarga_previa") is not None:
        # #             print(f"     1) Va a estación de recarga previa en {tarea['recarga_previa']}")
        # #             posicion_actual = tarea["recarga_previa"]

        # #         print(f"     2) Va al Pickup en {tarea['pickup']}")
        # #         posicion_actual = tarea["pickup"]

        # #         print(f"     3) Va al Dropoff en {tarea['dropoff']}")
        # #         posicion_actual = tarea["dropoff"]

        # #     print(f"\n  *** Dron {id_dron} termina en {posicion_actual} ***")

        # Visualización en el mapa
        vis.visualizar_rutas(mejor_individuo_global, tareas_con_estaciones_carga_mejor, drones, config.POLIGONO_ROSARIO, estaciones, config)

        # 3. Retornar KPIs
        return {
            "params": params.copy() if params else {},
            "mejor_energia": (mejor_energia_global), #En MegaJoules
            "tiempo_medio_entrega": sim.calcular_tiempo_medio_entrega(mejor_individuo_global, tareas, drones, estaciones),
            "parametros_inviables": parametros_inviables,
        }
    else:
        print("❌ No se encontró una solución válida.")
        return {
            "params": params.copy() if params else {},
            "mejor_energia": None,
            "tiempo_medio_entrega": None,
            "parametros_inviables": parametros_inviables,
        }


def main():

    corridas = [
        #Probamos con 10 drones
        {"NUM_TAREAS": 60, "NUM_DRONES":20 , "TIEMPO_MIN": 150, "TIEMPO_MAX_MIN": 180},   
        {"NUM_TAREAS": 90, "NUM_DRONES":20 , "TIEMPO_MIN": 135, "TIEMPO_MAX_MIN": 165},
        {"NUM_TAREAS": 120, "NUM_DRONES":30 , "TIEMPO_MIN": 120, "TIEMPO_MAX_MIN": 150},
        # # Probamos reduciendo los tiempos de pedido --> Mejor servicio
        {"NUM_TAREAS": 60, "NUM_DRONES":10 , "TIEMPO_MIN": 140, "TIEMPO_MAX_MIN": 170},   
        {"NUM_TAREAS": 90, "NUM_DRONES":20 , "TIEMPO_MIN": 125, "TIEMPO_MAX_MIN": 155},
        {"NUM_TAREAS": 120, "NUM_DRONES":30 , "TIEMPO_MIN": 110, "TIEMPO_MAX_MIN": 140},
    ]

    resultados = []
    for i in range(len(corridas)):
        print(f"\n=== Iniciando Corrida {i+1}/{len(corridas)} con parámetros: {corridas[i]} ===")
        try:
            kpis = run_optimization(params=corridas[i], verbose=False)

            if kpis.get("parametros_inviables", True): #Si parametros_inviables es True, se considera que la corrida fue inviable
                print(f"❌ Corrida {i+1} inviable con parámetros {corridas[i]}")
                resultados.append({
                    "params": corridas[i],
                    "status": "inviable",
                    "mejor_energia": None,
                    "tiempo_medio_entrega": None
                })
            else:
                resultados.append({
                    **kpis,
                    "status": "ok"
                })
        except Exception as e:
            print(f"⚠️ Error en la corrida {i+1}: {e}")
            resultados.append({
                "params": corridas[i],
                "status": "inviable",
                "mejor_energia": None,
                "tiempo_medio_entrega": None
            })
    
    # Comparación de resultados
    df = pd.DataFrame(resultados)
    print("\n=== TABLA DE COMPARACIÓN DE CORRIDAS ===")
    print(df[["params", "status", "mejor_energia", "tiempo_medio_entrega"]])

    os.makedirs("resultados", exist_ok=True)
    df.to_excel(f"resultados/resultados_corridas{random.randint(1, 1000)}.xlsx", 
            index=False, 
            engine="openpyxl")
    print(f"\nResultados guardados en resultados_corridas{random.randint(1, 1000)}.xlsx ✅")

if __name__ == "__main__":
    main()