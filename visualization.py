# Genera el mapa de resultados con Folium.

import folium
from simulation import decodificar_cromosoma

def visualizar_rutas(mejor_solucion, tareas, drones, poligono, estaciones_carga, config, filename="rutas_drones_final.html"):
    """Dibuja el mapa de la mejor solución encontrada."""
    rutas_decodificadas = decodificar_cromosoma(mejor_solucion, tareas, drones)
    mapa = folium.Map(location=config.CENTRO_ROSARIO, zoom_start=13)
    folium.Polygon(locations=poligono, color='black', weight=2, fill=True, fill_color='grey', fill_opacity=0.1, tooltip='Área de Operación').add_to(mapa)
    colores = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue']
    
    for i, estacion in enumerate(estaciones_carga):
        folium.Marker(location=estacion, popup=f"Estación de Carga {i+1}", icon=folium.Icon(color='gray', icon='battery-full', prefix='fa')).add_to(mapa)
    
    for dron in drones:
        folium.Marker(location=dron["posicion_inicial"], popup=f"Base Dron {dron['id']}", icon=folium.Icon(color='black', icon='plane', prefix='fa')).add_to(mapa)
    
    for id_dron, tareas_asignadas in rutas_decodificadas.items():
        if not tareas_asignadas: continue
        puntos_ruta = [drones[id_dron]["posicion_inicial"]]
        color_ruta = colores[id_dron % len(colores)]
        for i, tarea in enumerate(tareas_asignadas):
            folium.Marker(location=tarea["pickup"], popup=f"Pedido {tarea['id']} Pickup", icon=folium.Icon(color=color_ruta, icon='box', prefix='fa')).add_to(mapa)
            folium.Marker(location=tarea["dropoff"], popup=f"Pedido {tarea['id']} Dropoff", icon=folium.Icon(color=color_ruta, icon='check-circle', prefix='fa')).add_to(mapa)
            puntos_ruta.append(tarea["pickup"])
            puntos_ruta.append(tarea["dropoff"])
        folium.PolyLine(puntos_ruta, color=color_ruta, weight=2.5, opacity=1).add_to(mapa)
        
    mapa.save(filename)
    print(f"Mapa guardado en '{filename}'")