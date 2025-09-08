# Funciones para generar los datos iniciales del problema.

import random
from points_generator import generar_puntos_aleatorios, generar_puntos_equiespaciados
from config import PESO_MAX_PAQUETE # Asumiendo que PESO_MAX_PAQUETE está en config.py

def generar_tareas(num_tareas, poligono):
    """Genera la lista de tareas."""
    pickups = generar_puntos_aleatorios(num_tareas, poligono)
    dropoffs = generar_puntos_aleatorios(num_tareas, poligono)
    return [{"id": i, "pickup": pickups[i], "dropoff": dropoffs[i], "peso": round(random.uniform(0.1, 2.0), 2), "tiempo_limite": None, "recarga_previa": None, "recarga_posterior": None} for i in range(num_tareas)]

def generar_drones(num_drones, poligono):
    """Genera la lista de drones con sus bases."""
    posiciones = generar_puntos_aleatorios(num_drones, poligono)
    return [{"id": i, "posicion_inicial": posiciones[i]} for i in range(num_drones)]

def generar_estaciones_carga(num_estaciones, poligono):
    """Genera la lista de estaciones de carga."""
    return generar_puntos_equiespaciados(num_estaciones, poligono, 0.009, 30)