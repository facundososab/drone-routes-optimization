# Contiene la lógica para simular una solución y calcular su funcion_objetivo.

import numpy as np
from points_generator import encontrar_estacion_mas_cercana, distancia_metros
import config
import copy

def decodificar_cromosoma(individuo, drones):
    """Traduce un cromosoma a una lista de IDs de tareas para cada dron."""
    c_i, c_ii = individuo
    rutas_drones = {dron["id"]: [] for dron in drones}
    num_drones_reales = len(c_ii) + 1
    puntos_corte_extendidos = [0] + c_ii + [config.NUM_TAREAS]
    for i in range(num_drones_reales):
        idx_inicio = puntos_corte_extendidos[i]
        idx_fin = puntos_corte_extendidos[i+1]
        id_tareas_asignadas = c_i[idx_inicio:idx_fin] 
        if i < len(drones):
            rutas_drones[i] = id_tareas_asignadas
    return rutas_drones

def calcular_energia(L1, L2, L3, v, mpj):
    """
    FUNCION OBJETIVO
    Calcula la energía consumida por un UAV durante una entrega.
    """
    term1 = config.COEFICIENTE_ARRASTRE * config.RHO * config.AREA_FRONTAL_DRON * (L1 + L2 + L3) * v**2
    sustentacion_const = v * config.FIGURE_OF_MERIT * np.sqrt(2 * config.RHO * config.AREA_ROTOR)
    numerador2 = L2 * np.sqrt(((config.MASA_DRON + mpj) * config.G)**3)
    term2 = numerador2 / sustentacion_const
    numerador3 = (L1 + L3) * np.sqrt((config.MASA_DRON * config.G)**3)
    term3 = numerador3 / sustentacion_const
    energia_total = (1 / config.EFICIENCIA_GLOBAL) * (term1 + term2 + term3)
    return energia_total / 1e6

def funcion_objetivo(individuo, tareas, drones, estaciones_carga):
    """
    Función objetivo refactorizada con lógica de recarga proactiva y
    verificación de tiempos de entrega.
    """
    # --- CORRECCIÓN CRÍTICA: Evitar la modificación del estado global ---
    # Se trabaja con una copia profunda para no "contaminar" los datos para el siguiente individuo.\
    #print("Evaluando individuo:", individuo)
    tareas_locales = copy.deepcopy(tareas)
        
    rutas = decodificar_cromosoma(individuo, drones)
    energia_total_flota = 0
    
    penalizacion = False

    for id_dron, id_tareas_asignadas in rutas.items():
        posicion_actual = drones[id_dron]["posicion_inicial"]
        bateria_actual = config.BATERIA_MAXIMA
        tiempo_dron = 0

        for id_tarea in id_tareas_asignadas:
            tarea = tareas_locales[id_tarea]

            # --- 1. REFACTORIZACIÓN LÓGICA: Planificación del viaje ---
            posicion_inicio_viaje = posicion_actual
            
            # Se calcula la energía requerida desde la posición actual para decidir si recargar
            L1_temporal = distancia_metros(posicion_actual, tarea["pickup"])
            L2 = distancia_metros(tarea["pickup"], tarea["dropoff"])
            energia_requerida_inicial = calcular_energia(L1_temporal, L2, 0, config.VELOCIDAD_DRON, tarea["peso"])

            # --- 2. DECISIÓN DE RECARGA ---
            if bateria_actual < energia_requerida_inicial:
                #print(f"Tarea: {tarea['id']} Batería insuficiente, buscando estación... Necesito: {energia_requerida_inicial:.2f}, Tengo: {bateria_actual:.2f}")
                estacion_cercana = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
                dist_a_estacion = distancia_metros(posicion_actual, estacion_cercana)
                energia_a_estacion = calcular_energia(dist_a_estacion, 0, 0, config.VELOCIDAD_DRON, 0)
                
                if bateria_actual < energia_a_estacion:
                    #print(f"PENALIZACIÓN (Dron {id_dron}): No hay batería para llegar a la estación. Falta: {energia_a_estacion - bateria_actual:.2f} J")
                    penalizacion = True
                    continue

                # Simular viaje a la estación y recarga
                energia_total_flota += energia_a_estacion
                tiempo_dron += (dist_a_estacion / config.VELOCIDAD_DRON)
                bateria_actual = config.BATERIA_MAXIMA
                
                # La nueva posición de inicio del viaje es la estación
                posicion_inicio_viaje = estacion_cercana
                tarea["recarga_previa"] = estacion_cercana # Se modifica la copia local

            # --- 3. EJECUCIÓN DE LA TAREA ---
            # Se calculan L1 y la energía del viaje definitivo desde el punto de partida correcto (actual o estación)
            L1 = distancia_metros(posicion_inicio_viaje, tarea["pickup"])
            energia_viaje_tarea = calcular_energia(L1, L2, 0, config.VELOCIDAD_DRON, tarea["peso"])

            if bateria_actual < energia_viaje_tarea:
                #print(f"PENALIZACIÓN (Dron {id_dron}): Tarea imposible incluso con batería llena. Requiere: {energia_viaje_tarea:.2f} J")
                penalizacion = True
                continue

            # Si es posible, se ejecuta la tarea
            energia_total_flota += energia_viaje_tarea
            bateria_actual -= energia_viaje_tarea
            tiempo_dron += (L1 + L2) / config.VELOCIDAD_DRON
            posicion_actual = tarea["dropoff"]

            # --- 4. VERIFICACIÓN DEL TIEMPO LÍMITE (DEADLINE) ---
            if tiempo_dron > tarea["tiempo_max"]:
                #print(f"PENALIZACIÓN (Dron {id_dron}): Plazo de entrega excedido. Tiempo: {tiempo_dron:.2f}s, Límite: {tarea['tiempo_max']}s, en la tarea {tarea['id']}")
                penalizacion = True
            
            # --- 5. VERIFICACIÓN DE SEGURIDAD ---
            estacion_segura = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
            dist_segura = distancia_metros(posicion_actual, estacion_segura)
            energia_segura = calcular_energia(dist_segura, 0, 0, config.VELOCIDAD_DRON, 0)
            if bateria_actual < energia_segura:
                print(f"PENALIZACIÓN (Dron {id_dron}): Dron queda varado. Batería: {bateria_actual:.2f} J, Necesaria: {energia_segura:.2f} J")
                penalizacion = True
                continue
            
        #print("La bateria que consumió el dron", id_dron, "fue de:", config.BATERIA_MAXIMA - bateria_actual)

    # --- CÁLCULO FINAL DE LA FUNCION OBJETIVO ---
    if penalizacion:
        energia_total_flota = 0
        print("Se aplicó penalización por incumplimientos.")
    print(f"La energia devuelta es: {energia_total_flota}")
    return (energia_total_flota / 1e6) #MegaJoules