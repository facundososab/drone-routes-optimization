# Contiene la lógica para simular una solución y calcular su fitness.

import numpy as np
from utils import encontrar_estacion_mas_cercana
import config

def decodificar_cromosoma(individuo, tareas, drones):
    """Traduce un cromosoma a una lista de rutas para cada dron."""
    c_i, c_ii = individuo
    rutas_drones = {dron["id"]: [] for dron in drones}
    num_drones_reales = len(c_ii) + 1
    puntos_corte_extendidos = [0] + c_ii + [config.NUM_TAREAS]
    for i in range(num_drones_reales):
        idx_inicio = puntos_corte_extendidos[i]
        idx_fin = puntos_corte_extendidos[i+1]
        id_tareas_asignadas = c_i[idx_inicio:idx_fin]
        if i < len(drones):
            rutas_drones[i] = [tareas[id_tarea] for id_tarea in id_tareas_asignadas]
    return rutas_drones

def calcular_energia(L1, L2, L3, v, mpj):
    """
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
    energia_total_flota = 0
    tiempo_maximo = 0

    for id_dron, tareas_asignadas in rutas.items():
        posicion_actual = drones[id_dron]["posicion_inicial"]
        bateria_actual = config.BATERIA_MAXIMA
        tiempo_dron = 0
        
        for tarea in tareas_asignadas:
            # 1. Definir distancias L1, L2, L3 para la tarea actual
            L1 = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
            L2 = np.linalg.norm(np.array(tarea["pickup"]) - np.array(tarea["dropoff"]))
            estacion_post_tarea = encontrar_estacion_mas_cercana(tarea["dropoff"], estaciones_carga)
            L3_segura = np.linalg.norm(np.array(tarea["dropoff"]) - np.array(estacion_post_tarea))

            # 2. Calcular energía necesaria para la tarea y el viaje seguro a la estación
            energia_requerida_total = calcular_energia(L1, L2, L3_segura, config.VELOCIDAD_DRON, tarea["peso"])

            # 3. Condición de recarga
            if energia_requerida_total > bateria_actual - config.BATERIA_RESERVA:
                estacion_previa = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
                dist_a_carga = np.linalg.norm(np.array(posicion_actual) - np.array(estacion_previa))
                
                # Simular viaje a la estación (sin carga útil)
                energia_viaje_carga = calcular_energia(L1=dist_a_carga, L2=0, L3=0, v=config.VELOCIDAD_DRON, mpj=0)
                energia_total_flota += energia_viaje_carga
                tiempo_dron += dist_a_carga / config.VELOCIDAD_DRON
                
                # Carga y actualización de estado
                bateria_actual = config.BATERIA_MAXIMA
                posicion_actual = estacion_previa
                
                # Recalcular L1 desde la nueva posición (la estación de carga)
                L1 = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))

            # 4. Simular la ejecución de la tarea
            energia_tarea_real = calcular_energia(L1=L1, L2=L2, L3=0, v=config.VELOCIDAD_DRON, mpj=tarea["peso"])
            energia_total_flota += energia_tarea_real
            bateria_actual -= energia_tarea_real
            tiempo_dron += (L1 + L2) / config.VELOCIDAD_DRON
            posicion_actual = tarea["dropoff"]

        if tiempo_dron > tiempo_maximo:
            tiempo_maximo = tiempo_dron
            
    # Penalizar soluciones que dejen la batería en negativo (aunque no debería pasar con la lógica de recarga)
    if energia_total_flota <= 0 or tiempo_maximo <= 0:
        return 1e-9 # Evitar división por cero y fitness negativo

    return 1 / (energia_total_flota * tiempo_maximo)