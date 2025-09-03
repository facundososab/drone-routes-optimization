# Contiene la lógica para simular una solución y calcular su fitness.

import numpy as np
from points_generator import encontrar_estacion_mas_cercana
import config

def decodificar_cromosoma(individuo, tareas, drones):
    """Traduce un cromosoma a una lista de rutas para cada dron."""
    c_i, c_ii = individuo
    rutas_drones = {dron["id"]: [] for dron in drones}
    num_drones_reales = len(c_ii) + 1
    puntos_corte_extendidos = [0] + c_ii + [config.NUM_TAREAS]
    for i in range(num_drones_reales): #Se asignan las tareas a cada dron
        idx_inicio = puntos_corte_extendidos[i] #id de la tarea inicial
        idx_fin = puntos_corte_extendidos[i+1] #id de la tarea final (no incluida)
        id_tareas_asignadas = c_i[idx_inicio:idx_fin] 
        if i < len(drones):
            rutas_drones[i] = [tareas[id_tarea] for id_tarea in id_tareas_asignadas] #Los IDs se asignan a las tareas reales
    return rutas_drones
#Retorna por ejemplo:{
#     0: [tarea4, tarea2],
#     1: [tarea0, tarea3],
#     2: [tarea1]
# }

def calcular_energia(L1, L2, L3, v, mpj):
    """
    FUNCION OBJETIVO
    Calcula la energía consumida por un UAV durante una entrega,
    basado en el modelo matemático del paper.
    """
    # Término 1: Consumo por resistencia aerodinámica
    term1 = config.COEFICIENTE_ARRASTRE * config.RHO * config.AREA_FRONTAL_DRON * (L1 + L2 + L3) * v**2
    
    # Constante para los términos de sustentación
    sustentacion_const = v * config.FIGURE_OF_MERIT * np.sqrt(2 * config.RHO * config.AREA_ROTOR)
    
    # Término 2: Consumo por sustentación con carga
    numerador2 = L2 * np.sqrt(((config.MASA_DRON + mpj) * config.G)**3)
    term2 = numerador2 / sustentacion_const

    # Término 3: Consumo por sustentación sin carga
    numerador3 = (L1 + L3) * np.sqrt((config.MASA_DRON * config.G)**3)
    term3 = numerador3 / sustentacion_const
    
    return (1 / config.EFICIENCIA_GLOBAL) * (term1 + term2 + term3)

def funcion_fitness(individuo, tareas, drones, estaciones_carga):
    rutas = decodificar_cromosoma(individuo, tareas, drones)
#    Ej: rutas ={
#     0: [tarea4, tarea2],
#     1: [tarea0, tarea3],
#     2: [tarea1]
# }
    energia_total_flota = 0
    tiempo_total = 0 # tiempo total de todos los drones
    #rutas_a_estacion = {} # Para registrar las rutas a estaciones de carga

    for id_dron, tareas_asignadas in rutas.items():
        posicion_actual = drones[id_dron]["posicion_inicial"]
        bateria_actual = config.BATERIA_MAXIMA
        tiempo_dron = 0 #tiempo que tarda el dron en hacer todas sus tareas
        
        for tarea in tareas_asignadas:
            # 1. Definir distancias L1, L2, L3 para la tarea actual
            L1 = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
            L2 = np.linalg.norm(np.array(tarea["pickup"]) - np.array(tarea["dropoff"]))

            estacion_post_tarea = encontrar_estacion_mas_cercana(tarea["dropoff"], estaciones_carga)
            L3_segura = np.linalg.norm(np.array(tarea["dropoff"]) - np.array(estacion_post_tarea))
            energia_L3_segura = calcular_energia(L1=L3_segura, L2=0, L3=0, v=config.VELOCIDAD_DRON, mpj=0)

            # 2. Calcular energía necesaria para la tarea
            energia_requerida_total = calcular_energia(L1, L2, L3_segura, config.VELOCIDAD_DRON, tarea["peso"])

            # 3. Condición de recarga
            while energia_requerida_total > bateria_actual:
                #Verificar si la bateria del dron esta cargada al 100% 
                if bateria_actual == config.BATERIA_MAXIMA:
                    return 1e-9 # Penalizar si no se cumple el tiempo máximo de la tarea
                #Sino 
                estacion_previa = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
                #rutas_a_estacion[id_dron] = estacion_previa
                dist_a_carga = np.linalg.norm(np.array(posicion_actual) - np.array(estacion_previa))
                # Simular viaje a la estación (sin carga útil)
                energia_viaje_a_carga_previa = calcular_energia(L1=dist_a_carga, L2=0, L3=0, v=config.VELOCIDAD_DRON, mpj=0)
                energia_total_flota += energia_viaje_a_carga_previa
                tiempo_tarea = dist_a_carga / config.VELOCIDAD_DRON
                tiempo_dron += tiempo_tarea

                tarea["recarga_previa"] = estacion_previa

                # Carga y actualización de estado
                bateria_actual = config.BATERIA_MAXIMA
                posicion_actual = estacion_previa



                # Recalcular L1 desde la nueva posición (la estación de carga)
                L1 = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
                energia_requerida_total = calcular_energia(L1, L2, L3_segura, config.VELOCIDAD_DRON, tarea["peso"])
                
            # if energia_requerida_total > bateria_actual:
            #     return 1e-9 # Penalizar si no se cumple el tiempo máximo de la tarea

            # 4. Simular la ejecución de la tarea
            #Esto asegura que se va a poder realizar la tarea actual, pero luego de esta tarea puede passar que el dron quede con muy poca batería y que no llegue a la próxima tarea, hay que verificar eso.
            energia_total_flota += energia_requerida_total #+ energia a cagar previa (si hubo)
            bateria_actual -= energia_requerida_total
            tiempo_tarea = (L1 + L2) / config.VELOCIDAD_DRON
            tiempo_dron += tiempo_tarea + (energia_viaje_a_carga_previa / config.VELOCIDAD_DRON)
            posicion_actual = tarea["dropoff"]

            #if bateria_actual <= energia_L3_segura: #Ya no es necesario porque al principio validamos que si llegue a L3 luego de L2
                #return 1e-9 # Penalizar si no se cumple el tiempo máximo de la tarea
                
            #if tiempo_tarea > tarea["tiempo_max"]:
                #return 1e-9 # Penalizar si no se cumple el tiempo máximo de la tarea

        tiempo_total += tiempo_dron

    # Penalizar soluciones que dejen la batería en negativo (aunque no debería pasar con la lógica de recarga)
    if energia_total_flota <= 0 or tiempo_total <= 0:
        return 1e-9 # Evitar división por cero y fitness negativo

    return 1 / (energia_total_flota * tiempo_total)