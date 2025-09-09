# Contiene la lógica para simular una solución y calcular su funcion_objetivo.

import numpy as np
from points_generator import encontrar_estacion_mas_cercana, distancia_metros
import config

def decodificar_cromosoma(individuo, tareas, drones):
    """Traduce un cromosoma a una lista de IDs de tareas para cada dron."""
    c_i, c_ii = individuo
    rutas_drones = {dron["id"]: [] for dron in drones}
    num_drones_reales = len(c_ii) + 1
    puntos_corte_extendidos = [0] + c_ii + [config.NUM_TAREAS]
    for i in range(num_drones_reales): #Se asignan las tareas a cada dron
        idx_inicio = puntos_corte_extendidos[i] #id de la tarea inicialz
        idx_fin = puntos_corte_extendidos[i+1] #id de la tarea final (no incluida)
        id_tareas_asignadas = c_i[idx_inicio:idx_fin] 
        if i < len(drones):
            rutas_drones[i] = id_tareas_asignadas # Devolvemos solo los IDs
    return rutas_drones
#Retorna por ejemplo:{
#     0: [4, 2],
#     1: [0, 3],
#     2: [1]
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

    energia_total = (1 / config.EFICIENCIA_GLOBAL) * (term1 + term2 + term3)

    # print(f"[calcular_energia] L1={L1:.2f}, L2={L2:.2f}, L3={L3:.2f}, v={v}, mpj={mpj} => "
    #       f"term1={term1:.4f}, term2={term2:.4f}, term3={term3:.4f}, energia={energia_total:.4f}")

    return energia_total

def funcion_objetivo(individuo, tareas, drones, estaciones_carga):
    """
    Función objetivo refactorizada con lógica de recarga proactiva y
    verificación de tiempos de entrega.
    """
    # Las tareas son globales para todas las generaciones.
    # Entonces en cada generación, se deben reiniciar los campos de recarga de carga tarea.
    for tarea in tareas:
        tarea["recarga_previa"] = None
        
    rutas = decodificar_cromosoma(individuo, tareas, drones)

    energia_total_flota = 0
    # Usaremos el "makespan": el tiempo que tarda en terminar el último dron. Este sería el tiempo total de la generación (estaba mal acumular los tiempos porque las tareas se hacen en simultaneo)
    # Es una métrica más robusta para la optimización del tiempo total.
    makespan_flota = 0

    for id_dron, id_tareas_asignadas in rutas.items():
        posicion_actual = drones[id_dron]["posicion_inicial"]
        bateria_actual = config.BATERIA_MAXIMA
        tiempo_dron = 0

        for id_tarea in id_tareas_asignadas:
            tarea = tareas[id_tarea] # Obtenemos la tarea original
            #print ("Tarea:",tarea["id"])
            # --- 1. EVALUACIÓN PROACTIVA DE ENERGÍA PARA LA TAREA ACTUAL ---
            # ¿Cuánta energía necesito desde mi posición actual para completar esta tarea?
            L1 = distancia_metros(posicion_actual, tarea["pickup"])
            L2 = distancia_metros(tarea["pickup"], tarea["dropoff"])
            energia_requerida = calcular_energia(L1, L2, 0, config.VELOCIDAD_DRON, tarea["peso"])

            # --- 2. DECISIÓN DE RECARGA ---
            if bateria_actual < energia_requerida:
                # No tengo suficiente batería, debo recargar primero.
                print("Tarea:",tarea["id"] ,"Batería insuficiente, buscando estación de recarga...", "Necesito:", energia_requerida, "Tengo:", bateria_actual)
                estacion_cercana = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
                dist_a_estacion = distancia_metros(posicion_actual, estacion_cercana)
                energia_a_estacion = calcular_energia(dist_a_estacion, 0, 0, config.VELOCIDAD_DRON, 0)
                tarea["recarga_previa"] = estacion_cercana

                # Penalizar si ni siquiera puede llegar a la estación de carga.
                if bateria_actual < energia_a_estacion:
                    print(f"PENALIZACIÓN (Dron {id_dron}): No hay batería para llegar a la estación de carga. Falta: {energia_a_estacion - bateria_actual:.2f} J")
                    energia_total_flota += config.PENALTY_VALUE
                    tiempo_dron += config.PENALTY_VALUE # También penalizamos el tiempo
                    continue # Salta a la siguiente tarea, este dron no puede continuar esta ruta

                # Simular viaje a la estación y recarga (el tiempo de recarga es 0).
                energia_total_flota += energia_a_estacion
                tiempo_dron += (dist_a_estacion / config.VELOCIDAD_DRON)
                bateria_actual = config.BATERIA_MAXIMA
                posicion_actual = estacion_cercana
                
                # Una vez en la estación, recalculamos la energía necesaria para la tarea.
                L1 = distancia_metros(posicion_actual, tarea["pickup"])
                energia_requerida = calcular_energia(L1, L2, 0, config.VELOCIDAD_DRON, tarea["peso"])
                if energia_requerida > bateria_actual:
                    print(f"PENALIZACIÓN (Dron {id_dron}): Tarea imposible incluso con batería llena. Requiere: {energia_requerida:.2f} J")
                    energia_total_flota += config.PENALTY_VALUE
                    tiempo_dron += config.PENALTY_VALUE
                    continue # Salta a la siguiente tarea

            # --- 3. EJECUCIÓN DE LA TAREA ---
            # En este punto, garantizamos tener batería suficiente.
            energia_total_flota += energia_requerida
            bateria_actual -= energia_requerida
            tiempo_dron += (L1 + L2) / config.VELOCIDAD_DRON
            posicion_actual = tarea["dropoff"]

            # --- 4. VERIFICACIÓN DEL TIEMPO LÍMITE (DEADLINE) ---
            # Se comprueba si la tarea se completó a tiempo.
            if tiempo_dron > tarea["tiempo_max"]:
                print(f"PENALIZACIÓN (Dron {id_dron}): Plazo de entrega excedido. Tiempo: {tiempo_dron:.2f}s, Límite: {tarea['tiempo_max']}s")
                energia_total_flota += config.PENALTY_VALUE
                tiempo_dron += config.PENALTY_VALUE
                # No continuamos, la tarea se hizo tarde pero se hizo.

            # --- 5. VERIFICACIÓN DE SEGURIDAD (OPCIONAL PERO RECOMENDADO) ---
            # ¿Puede el dron, después de la entrega, llegar a una estación si fuera necesario? 
            # Esto asegura que en caso de no poder completar la siguiente tarea, pueda ir a hacer la recarga previa antes de hacerla
            estacion_segura = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
            dist_segura = distancia_metros(posicion_actual, estacion_segura)
            energia_segura = calcular_energia(dist_segura, 0, 0, config.VELOCIDAD_DRON, 0)
            if bateria_actual < energia_segura:
                print(f"PENALIZACIÓN (Dron {id_dron}): Dron queda varado. Batería: {bateria_actual:.2f} J, Necesaria: {energia_segura:.2f} J")
                energia_total_flota += config.PENALTY_VALUE
                tiempo_dron += config.PENALTY_VALUE
                continue # Salta a la siguiente tarea, este dron no puede continuar.

        # Actualizar el makespan de la flota
        if tiempo_dron > makespan_flota:
            makespan_flota = tiempo_dron

    # --- CÁLCULO FINAL DE LA FUNCION OBJETIVO ---
    # Evitar divisiones por cero o valores no válidos.
    if energia_total_flota <= 0 or makespan_flota <= 0:
        energia_total_flota += config.PENALTY_VALUE
        makespan_flota += config.PENALTY_VALUE

    # El objetivo es minimizar la energía total y el tiempo máximo (makespan).
    # Devolvemos la funcion_objetivo y la energía total para criterios de convergencia.
    print("PASAMOS")

    costo = (energia_total_flota * makespan_flota) #Si el individuo esta penalizado, costo = infinito
    funcion_objetivo = 1 / (1 + costo) # Si esta penalizado, funcion_objetivo tiende a 0. Sino, es un número entre 0 y 1. 
    #Mientras mayor sea la funcion objetivo, mejor el individuo
    #print(f"[funcion_objetivo] energia={energia_total_flota:.2f}, funcion_objetivo={funcion_objetivo}")
    return funcion_objetivo, energia_total_flota


