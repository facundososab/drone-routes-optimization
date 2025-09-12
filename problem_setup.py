# Funciones para generar los datos iniciales del problema.

import random
from points_generator import generar_puntos_aleatorios, generar_puntos_equiespaciados
from config import POLIGONO_ROSARIO, NUM_ESTACIONES, PESO_MAX_PAQUETE, TIEMPO_MIN_MIN, TIEMPO_MAX_MIN # Asumiendo que PESO_MAX_PAQUETE está en config.py
import osmnx as ox
import shapely.geometry as geom


def generar_tareas(num_tareas, poligono):
    """Genera la lista de tareas."""
    pickups = generar_puntos_aleatorios(num_tareas, poligono)
    dropoffs = generar_puntos_aleatorios(num_tareas, poligono)
    #print("pickups:", pickups)
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

estaciones_de_carga = []
def generar_estaciones_carga(num_estaciones, poligono):
    """
    Genera una lista de puntos de estaciones de carga (fuel)
    dentro de un polígono definido por coordenadas [(lat, lon), ...].
    """
    # Convertir a (lon, lat) para shapely
    polygon_coords = [(lon, lat) for lat, lon in poligono]
    polygon = geom.Polygon(polygon_coords)

    # Buscar estaciones de servicio (fuel) dentro del polígono
    tags = {"amenity": "fuel"}
    lugares = ox.features_from_polygon(polygon, tags)

    if lugares.empty:
        #print("No se encontraron estaciones de servicio en este polígono.")
        return []

    # Tomar centroides o puntos
    coords = []
    for _, row in lugares.iterrows():
        geom_row = row.geometry
        if geom_row.geom_type == "Point":
            lat, lon = geom_row.y, geom_row.x
        else:  # Polígono o línea → centroid
            lat, lon = geom_row.centroid.y, geom_row.centroid.x
        coords.append([lat, lon])

    # Eliminar duplicados
    coords = [list(t) for t in {tuple(c) for c in coords}]

    # Si hay más que la cantidad pedida → sample aleatorio
    if len(coords) >= 50:
        coords = random.sample(coords, 50)
    else:
        print(f"Solo se encontraron {len(coords)} estaciones de servicio.")

    return coords[:num_estaciones]
