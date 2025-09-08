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

    # Las tareas son globales para todas las generaciones.
    # Entonces en cada generación, se deben reiniciar los campos de recarga de carga tarea.
    for tarea in tareas:
        tarea["recarga_previa"] = None
        tarea["recarga_posterior"] = None
        
    rutas = decodificar_cromosoma(individuo, tareas, drones)

    energia_total_flota = 0
    tiempo_total_flota = 0

    for id_dron, tareas_asignadas in rutas.items():
        posicion_actual = drones[id_dron]["posicion_inicial"]
        bateria_actual = config.BATERIA_MAXIMA
        tiempo_dron = 0

        for i, tarea in enumerate(tareas_asignadas):
            # --- Calcular distancias ---
            # L1 = base -> pickup
            L1 = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
            # L2 = pickup -> dropoff
            L2 = np.linalg.norm(np.array(tarea["pickup"]) - np.array(tarea["dropoff"]))
            # L0 = dropoff -> estación más cercana a la posición actual
            estacion_previa = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
            L0 = np.linalg.norm(np.array(posicion_actual) - np.array(estacion_previa))
            # L3 = dropoff -> estación más cercana al dropoff
            estacion_post = encontrar_estacion_mas_cercana(tarea["dropoff"], estaciones_carga)
            L3 = np.linalg.norm(np.array(tarea["dropoff"]) - np.array(estacion_post))

            energia_L1L2 = calcular_energia(L1, L2, 0, config.VELOCIDAD_DRON, tarea["peso"])
            energia_L0 = calcular_energia(L0, 0, 0, config.VELOCIDAD_DRON, 0)
            energia_L3 = calcular_energia(L3, 0, 0, config.VELOCIDAD_DRON, 0)

            # --- Verificar si puedo cumplir la tarea directamente ---
            if energia_L1L2 > bateria_actual: # No me alcanza, debo recargar antes en L0
                
                if energia_L0 > bateria_actual: # penalizar: ni siquiera llego a estación previa
                    return 1e-9  
                # Simular recarga previa
                energia_total_flota += energia_L0
                tiempo_dron += (L0 / config.VELOCIDAD_DRON)
                posicion_actual = estacion_previa
                bateria_actual = config.BATERIA_MAXIMA
                tarea["recarga_previa"] = estacion_previa

                # Recalcular L1 tras recarga
                L1 = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
                energia_L1L2 = calcular_energia(L1, L2, 0, config.VELOCIDAD_DRON, tarea["peso"])

            # --- Ejecutar la tarea ---
            bateria_actual -= energia_L1L2
            energia_total_flota += energia_L1L2
            tiempo_dron += (L1 + L2) / config.VELOCIDAD_DRON
            posicion_actual = tarea["dropoff"]

            # --- Verificar si necesito recarga posterior ---
            # (si hay una próxima tarea, miro si me alcanza)
            if i < len(tareas_asignadas) - 1:
                prox_tarea = tareas_asignadas[i + 1]
                L1_next = np.linalg.norm(np.array(posicion_actual) - np.array(prox_tarea["pickup"]))
                L2_next = np.linalg.norm(np.array(prox_tarea["pickup"]) - np.array(prox_tarea["dropoff"]))
                energia_prox = calcular_energia(L1_next, L2_next, 0, config.VELOCIDAD_DRON, prox_tarea["peso"])

                if bateria_actual < energia_prox:
                    # No alcanza para la próxima, intento ir a recarga en L3 (recarga posterior de la tarea actual)
                    if bateria_actual < energia_L3:# penalizar: no llego ni a estación
                        return 1e-9  
                    # Hago recarga posterior
                    energia_total_flota += energia_L3
                    tiempo_dron += (L3 / config.VELOCIDAD_DRON)
                    posicion_actual = estacion_post
                    bateria_actual = config.BATERIA_MAXIMA
                    tarea["recarga_posterior"] = estacion_post
                    
        tiempo_total_flota += tiempo_dron

    if energia_total_flota <= 0 or tiempo_total_flota <= 0:
        return 1e-9

    return 1 / (energia_total_flota * tiempo_total_flota)
