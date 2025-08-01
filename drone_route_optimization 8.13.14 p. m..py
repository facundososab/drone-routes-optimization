import random
import folium
import numpy as np

# --- 1. PARÁMETROS DE CONFIGURACIÓN Y DATOS INICIALES ---

# Coordenadas aproximadas de Rosario, Argentina, para generar puntos.
CENTRO_ROSARIO = [-32.9477, -60.6304]

# NUEVO: Polígono que representa la Av. Circunvalación 25 de Mayo en Rosario.
# Coordenadas aproximadas obtenidas de OpenStreetMap.
POLIGONO_ROSARIO = [
    # Límite por la Circunvalación (lado oeste y sur)
    (-32.960350,-60.684600),
    (-32.926592, -60.676048),
    (-32.925379, -60.660771), 
    (-32.939847, -60.634862), 
    (-32.960690, -60.620853),  
    (-32.971469, -60.622220),  
]



# Parámetros del AG
NUM_TAREAS = 15
NUM_DRONES = 4
TAMANO_POBLACION = 50
NUM_GENERACIONES = 100
PROBABILIDAD_MUTACION = 0.1

# Parámetros de los drones y paquetes (según PDF)
PESO_DRON = 1.5  # kg, fijo
PESO_MAX_PAQUETE = 2.0  # kg (2000 gramos)

# NUEVO: Función para verificar si un punto está dentro de un polígono.
# Implementa el algoritmo de Ray Casting.
def punto_en_poligono(punto, poligono):
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

# MODIFICADO: Generar tareas asegurando que estén dentro del polígono.
def generar_tareas(num_tareas, poligono):
    """Genera una lista de tareas con coordenadas y pesos aleatorios dentro del polígono."""
    tareas = []
    # Obtener los límites del polígono para generar puntos de forma más eficiente
    lats = [p[0] for p in poligono]
    lons = [p[1] for p in poligono]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    for i in range(num_tareas):
        punto_pickup, punto_dropoff = None, None
        
        while not punto_pickup:
            lat = random.uniform(min_lat, max_lat)
            lon = random.uniform(min_lon, max_lon)
            if punto_en_poligono([lat, lon], poligono):
                punto_pickup = [lat, lon]
        
        while not punto_dropoff:
            lat = random.uniform(min_lat, max_lat)
            lon = random.uniform(min_lon, max_lon)
            if punto_en_poligono([lat, lon], poligono):
                punto_dropoff = [lat, lon]
                
        tarea = {
            "id": i,
            "pickup": punto_pickup,
            "dropoff": punto_dropoff,
            "peso": round(random.uniform(0.1, PESO_MAX_PAQUETE), 2) # Peso variable
        }
        tareas.append(tarea)
    return tareas

def generar_drones(num_drones, poligono):
    """Genera las posiciones iniciales de los drones dentro del polígono."""
    drones = []
    for i in range(num_drones):
        posicion = None
        while not posicion:
            lat = random.uniform(min(p[0] for p in poligono), max(p[0] for p in poligono))
            lon = random.uniform(min(p[1] for p in poligono), max(p[1] for p in poligono))
            if punto_en_poligono([lat, lon], poligono):
                posicion = [lat, lon]
        drones.append({"id": i, "posicion_inicial": posicion})
    return drones

# --- 2. ESTRUCTURA DEL ALGORITMO GENÉTICO (Sin cambios) ---
# ... (Las funciones crear_individuo, crear_poblacion_inicial, decodificar_cromosoma, 
# funcion_fitness, seleccion, partial_mapped_crossover, cruce y mutacion permanecen igual)
def crear_individuo():
    c_i = list(range(NUM_TAREAS))
    random.shuffle(c_i)
    puntos_de_corte = sorted(random.sample(range(1, NUM_TAREAS), NUM_DRONES - 1))
    c_ii = puntos_de_corte
    return [c_i, c_ii]

def crear_poblacion_inicial():
    return [crear_individuo() for _ in range(TAMANO_POBLACION)]

def decodificar_cromosoma(individuo, tareas, drones):
    c_i, c_ii = individuo
    rutas_drones = {dron["id"]: [] for dron in drones}
    puntos_corte_extendidos = [0] + c_ii + [NUM_TAREAS]
    for i in range(NUM_DRONES):
        idx_inicio = puntos_corte_extendidos[i]
        idx_fin = puntos_corte_extendidos[i+1]
        id_tareas_asignadas = c_i[idx_inicio:idx_fin]
        rutas_drones[i] = [tareas[id_tarea] for id_tarea in id_tareas_asignadas]
    return rutas_drones

def funcion_fitness(individuo, tareas, drones):
    rutas = decodificar_cromosoma(individuo, tareas, drones)
    costo_total = 0
    tiempo_maximo = 0
    for id_dron, tareas_asignadas in rutas.items():
        if not tareas_asignadas:
            continue
        tiempo_dron = 0
        energia_dron = 0
        posicion_actual = drones[id_dron]["posicion_inicial"]
        for tarea in tareas_asignadas:
            dist_al_pickup = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
            dist_del_dropoff = np.linalg.norm(np.array(tarea["pickup"]) - np.array(tarea["dropoff"]))
            costo_dron_tarea = dist_al_pickup + dist_del_dropoff
            energia_dron += costo_dron_tarea
            tiempo_dron += costo_dron_tarea / 10
            posicion_actual = tarea["dropoff"]
        costo_total += energia_dron
        if tiempo_dron > tiempo_maximo:
            tiempo_maximo = tiempo_dron
    fitness = 1 / (costo_total + tiempo_maximo + 1e-6)
    return fitness

def seleccion(poblacion, fitness_scores):
    sorted_population = [x for _, x in sorted(zip(fitness_scores, poblacion), key=lambda pair: pair[0], reverse=True)]
    return sorted_population[:len(poblacion) // 2]

def partial_mapped_crossover(padre1, padre2):
    size = len(padre1)
    hijo1, hijo2 = [-1]*size, [-1]*size
    start, end = sorted(random.sample(range(size), 2))
    hijo1[start:end+1] = padre1[start:end+1]
    hijo2[start:end+1] = padre2[start:end+1]
    for i in list(range(start)) + list(range(end + 1, size)):
        if padre2[i] not in hijo1:
            hijo1[i] = padre2[i]
        else:
            current_val = padre2[i]
            while current_val in hijo1:
                idx = padre1.index(current_val)
                current_val = padre2[idx]
            hijo1[i] = current_val
        if padre1[i] not in hijo2:
            hijo2[i] = padre1[i]
        else:
            current_val = padre1[i]
            while current_val in hijo2:
                idx = padre2.index(current_val)
                current_val = padre1[idx]
            hijo2[i] = current_val
    return hijo1, hijo2

def cruce(padres):
    descendencia = []
    if len(padres) < 2: return padres
    for i in range(0, len(padres) - (len(padres)%2), 2):
        padre1, padre2 = padres[i], padres[i+1]
        c_i_hijo1, c_i_hijo2 = partial_mapped_crossover(padre1[0], padre2[0])
        corte_cruce = random.randint(1, len(padre1[1])-1) if len(padre1[1]) > 1 else 0
        c_ii_hijo1 = sorted(padre1[1][:corte_cruce] + padre2[1][corte_cruce:])
        c_ii_hijo2 = sorted(padre2[1][:corte_cruce] + padre1[1][corte_cruce:])
        descendencia.append([c_i_hijo1, c_ii_hijo1])
        descendencia.append([c_i_hijo2, c_ii_hijo2])
    return descendencia

def mutacion(individuo):
    if random.random() < PROBABILIDAD_MUTACION:
        c_i = individuo[0]
        idx1, idx2 = random.sample(range(len(c_i)), 2)
        c_i[idx1], c_i[idx2] = c_i[idx2], c_i[idx1]
    return individuo

# --- 3. VISUALIZACIÓN EN MAPA (Modificado) ---

def visualizar_rutas(mejor_solucion, tareas, drones, poligono, filename="rutas_drones_delimitado.html"):
    """Genera un mapa HTML con Folium para visualizar las rutas y el polígono."""
    rutas_decodificadas = decodificar_cromosoma(mejor_solucion, tareas, drones)
    
    mapa = folium.Map(location=CENTRO_ROSARIO, zoom_start=12)
    
    # NUEVO: Dibujar el polígono del área de operación en el mapa
    folium.Polygon(
        locations=poligono,
        color='black',
        weight=2,
        fill=True,
        fill_color='grey',
        fill_opacity=0.1,
        tooltip='Área de Operación'
    ).add_to(mapa)
    
    colores = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue']

    for dron in drones:
        folium.Marker(location=dron["posicion_inicial"], popup=f"Base Dron {dron['id']}", icon=folium.Icon(color='black', icon='home')).add_to(mapa)

    for id_dron, tareas_asignadas in rutas_decodificadas.items():
        if not tareas_asignadas:
            continue
        puntos_ruta = [drones[id_dron]["posicion_inicial"]]
        color_ruta = colores[id_dron % len(colores)]
        for i, tarea in enumerate(tareas_asignadas):
            folium.Marker(location=tarea["pickup"], popup=f"T{tarea['id']} Pickup (D{id_dron})", icon=folium.Icon(color=color_ruta, icon='arrow-up')).add_to(mapa)
            folium.Marker(location=tarea["dropoff"], popup=f"T{tarea['id']} Dropoff (D{id_dron})", icon=folium.Icon(color=color_ruta, icon='gift')).add_to(mapa)
            puntos_ruta.append(tarea["pickup"])
            puntos_ruta.append(tarea["dropoff"])
        folium.PolyLine(puntos_ruta, color=color_ruta, weight=2.5, opacity=1).add_to(mapa)

    mapa.save(filename)
    print(f"Mapa guardado en '{filename}'")

# --- 4. EJECUCIÓN PRINCIPAL DEL ALGORITMO (Modificado) ---

if __name__ == "__main__":
    # MODIFICADO: Pasar el polígono a las funciones de generación
    tareas = generar_tareas(NUM_TAREAS, POLIGONO_ROSARIO)
    drones = generar_drones(NUM_DRONES, POLIGONO_ROSARIO)
    
    poblacion = crear_poblacion_inicial()
    mejor_solucion_global = None
    mejor_fitness_global = -1
    
    for gen in range(NUM_GENERACIONES):
        fitness_scores = [funcion_fitness(ind, tareas, drones) for ind in poblacion]
        mejor_fitness_gen = max(fitness_scores)
        if mejor_fitness_gen > mejor_fitness_global:
            mejor_fitness_global = mejor_fitness_gen
            mejor_solucion_global = poblacion[fitness_scores.index(mejor_fitness_gen)]
        
        padres = seleccion(poblacion, fitness_scores)
        descendencia = cruce(padres)
        poblacion = descendencia + padres[:len(poblacion) - len(descendencia)]
        poblacion = [mutacion(ind) for ind in poblacion]
        
        if (gen + 1) % 10 == 0:
            print(f"Generación {gen+1}/{NUM_GENERACIONES} - Mejor Fitness: {mejor_fitness_global:.6f}")

    print("\n--- Optimización Finalizada ---")
    print(f"Mejor solución encontrada: {mejor_solucion_global}")
    
    # MODIFICADO: Pasar el polígono a la función de visualización
    visualizar_rutas(mejor_solucion_global, tareas, drones, POLIGONO_ROSARIO)