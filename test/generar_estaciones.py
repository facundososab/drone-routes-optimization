import random
from config import POLIGONO_ROSARIO, NUM_ESTACIONES, ESTACIONES_DE_CARGA
import osmnx as ox
import shapely.geometry as geom

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
        print("No se encontraron estaciones de servicio en este polígono.")
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

estaciones = generar_estaciones_carga(NUM_ESTACIONES, POLIGONO_ROSARIO)
print("Estaciones de carga generadas:", estaciones)
ESTACIONES_DE_CARGA = estaciones
