import random
from points_generator import generar_puntos_aleatorios, generar_puntos_equiespaciados
from config import POLIGONO_ROSARIO, NUM_ESTACIONES, PESO_MAX_PAQUETE, TIEMPO_MIN_MIN, TIEMPO_MAX_MIN # Asumiendo que PESO_MAX_PAQUETE está en config.py
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
#[[-32.951464, -60.671927], [-32.955493395731686, -60.64931543684792], [-32.95462524807064, -60.641456196321016], [-32.95705476993344, -60.64066405279374], [-32.94209065744972, -60.66111699145832], [-32.9434759, -60.6458624], [-32.9569943710962, -60.64112126056307], [-32.94286265990093, -60.63902348215416], [-32.9390096, -60.6788675], [-32.9403854, -60.6655418], [-32.95145340874381, -60.66841189759766], [-32.95535427882167, -60.6503802447167], [-32.95028232307268, -60.655301212446375], [-32.94627837970099, -60.647060085696005], [-32.9354337, -60.6581155]]