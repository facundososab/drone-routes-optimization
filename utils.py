# Contiene funciones de utilidad, principalmente geométricas.

import random
import numpy as np

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

def encontrar_estacion_mas_cercana(punto, estaciones):
    """Encuentra la estación de carga más cercana a un punto dado."""
    distancias = [np.linalg.norm(np.array(punto) - np.array(estacion)) for estacion in estaciones]
    return estaciones[np.argmin(distancias)]