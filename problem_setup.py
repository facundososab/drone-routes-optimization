# Funciones para generar los datos iniciales del problema.

import random
from points_generator import generar_puntos_aleatorios, generar_puntos_equiespaciados
from config import PESO_MAX_PAQUETE, TIEMPO_MIN_MIN, TIEMPO_MAX_MIN # Asumiendo que PESO_MAX_PAQUETE está en config.py

def generar_tareas(num_tareas, poligono):
    """Genera la lista de tareas."""
    pickups = generar_puntos_aleatorios(num_tareas, poligono)
    dropoffs = generar_puntos_aleatorios(num_tareas, poligono)
    print("pickups:", pickups)
    return [{
        "id": i,
        "pickup": pickups[i],
        "dropoff": dropoffs[i],
        "peso": round(random.uniform(0.1, PESO_MAX_PAQUETE), 2), # en kilos
        "tiempo_max": random.randint(TIEMPO_MIN_MIN * 60, TIEMPO_MAX_MIN * 60),  # en segundos
        "recarga_previa": None,
    } for i in range(num_tareas)]

def generar_drones(num_drones, poligono):
    """Genera la lista de drones con sus bases."""
    posiciones = generar_puntos_aleatorios(num_drones, poligono)
    return [{"id": i, "posicion_inicial": posiciones[i]} for i in range(num_drones)]

def generar_estaciones_carga(num_estaciones, poligono):
    """Genera la lista de estaciones de carga."""
    return generar_puntos_equiespaciados(num_estaciones, poligono, 0.009, 30)