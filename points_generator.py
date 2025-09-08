# Contiene funciones para generar puntos aleatorios y equiespaciados dentro de un polígono,
# así como para encontrar la estación de carga más cercana a un punto dado.
import random
import numpy as np
import math
import config
from math import radians, sin, cos, sqrt, atan2

def distancia_metros(coord1, coord2):
    """Calcula la distancia en metros entre dos coordenadas (lat, lon)."""
    R = 6371000  # Radio de la Tierra en metros
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def punto_en_poligono(punto, poligono):
    """Verifica si un punto está dentro de un polígono usando Ray Casting."""
    lat, lon = punto
    n = len(poligono)
    dentro = False
    p1_lat, p1_lon = poligono[0]
    for i in range(n + 1):
        p2_lat, p2_lon = poligono[i % n]
        if min(p1_lon, p2_lon) < lon <= max(p1_lon, p2_lon):
            if lat <= max(p1_lat, p2_lat):
                if p1_lon != p2_lon:
                    lat_interseccion = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                if p1_lat == p2_lat or lat <= lat_interseccion:
                    dentro = not dentro
        p1_lat, p1_lon = p2_lat, p2_lon
    return dentro

def generar_puntos_aleatorios(cantidad, poligono):
    """Genera una lista de puntos aleatorios dentro de un polígono."""
    puntos = []
    lats = [p[0] for p in poligono]
    lons = [p[1] for p in poligono]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    while len(puntos) < cantidad:
        lat = random.uniform(min_lat, max_lat)
        lon = random.uniform(min_lon, max_lon)
        if punto_en_poligono([lat, lon], poligono):
            puntos.append([lat, lon])
    return puntos

def generar_puntos_equiespaciados(num_estaciones, poligono, radio, k=30): #radio de aprox 300m en rosario
    """
    Genera puntos con Poisson Disk Sampling dentro de un polígono.
    - radius: distancia mínima entre puntos
    - k: intentos de rechazo (rejection_samples)
    """

    first_point = config.CENTRO_ROSARIO #El punto base va a ser el centro. A partir de ahi se van a empezar a buscar vecinos.

    puntos = [first_point]
    activos = [first_point] #PUNTOS CANDIDATOS A GENERAR VECINOS

    while activos and len(puntos) < num_estaciones:
        idx = random.randint(0, len(activos) - 1)
        base_point = activos[idx]
        found = False

        for _ in range(k): #A cada puntoX activo se le va a intentar agregar puntos vecinos, si se rechazan k puntos cercanos
            #porque no cumplen con la dist_min del radio, entonces se rechaza el puntoX

            r = random.uniform(radio, 2 * radio) #genera un radio
            theta = random.uniform(0, 2 * math.pi)# Se genera un ángulo aleatorio
            #Construye el punto nuevo
            new_point = (
                base_point[0] + r * math.cos(theta), # lon
                base_point[1] + r * math.sin(theta)  # lat
            )

            if punto_en_poligono(new_point, poligono):
                # chequear distancia mínima con todos los puntos existentes
                if all(math.dist(new_point, p) >= radio for p in puntos):
                    puntos.append(new_point) #Agregamos al vecino valido
                    activos.append(new_point)
                    found = True
                    break
        if not found: #Ningun vecino fue valido
            activos.pop(idx)
            print("Se descarta el punto")

    return puntos


def encontrar_estacion_mas_cercana(punto, estaciones):
    """Encuentra la estación de carga más cercana a un punto dado en metros."""
    distancias = [distancia_metros(punto, estacion) for estacion in estaciones]
    return estaciones[np.argmin(distancias)]
