import random
import folium
import numpy as np

# --- 1. PARÁMETROS DE CONFIGURACIÓN Y DATOS INICIALES ---

POLIGONO_ROSARIO = [
    (-32.960350, -60.684600), (-32.926592, -60.676048),
    (-32.925379, -60.660771), (-32.939847, -60.634862),
    (-32.960690, -60.620853), (-32.971469, -60.622220)
]
CENTRO_ROSARIO = np.mean(POLIGONO_ROSARIO, axis=0).tolist()

NUM_TAREAS = 15
NUM_DRONES = 4
NUM_ESTACIONES = 3
TAMANO_POBLACION = 50
NUM_GENERACIONES = 100
PROBABILIDAD_MUTACION = 0.1

PESO_DRON_VACIO = 1.5
VELOCIDAD_DRON = 15
BATERIA_MAXIMA = 1000
BATERIA_RESERVA = BATERIA_MAXIMA * 0.05
CONSUMO_POR_DISTANCIA = 1.0
CONSUMO_EXTRA_POR_PESO = 0.5

# --- 2. FUNCIONES AUXILIARES Y DE GENERACIÓN ---

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

def generar_puntos_aleatorios(cantidad, poligono):
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

def generar_tareas(num_tareas, poligono):
    pickups = generar_puntos_aleatorios(num_tareas, poligono)
    dropoffs = generar_puntos_aleatorios(num_tareas, poligono)
    return [{"id": i, "pickup": pickups[i], "dropoff": dropoffs[i], "peso": round(random.uniform(0.1, 2.0), 2)} for i in range(num_tareas)]

def generar_drones(num_drones, poligono):
    posiciones = generar_puntos_aleatorios(num_drones, poligono)
    return [{"id": i, "posicion_inicial": posiciones[i]} for i in range(num_drones)]

def generar_estaciones_carga(num_estaciones, poligono):
    return generar_puntos_aleatorios(num_estaciones, poligono)

# --- 3. LÓGICA DEL ALGORITMO GENÉTICO ---

def crear_individuo():
    c_i = list(range(NUM_TAREAS))
    random.shuffle(c_i)
    num_cortes = NUM_DRONES - 1
    if num_cortes >= NUM_TAREAS:
        num_cortes = NUM_TAREAS - 1 if NUM_TAREAS > 1 else 0
    if num_cortes > 0:
        puntos_de_corte = sorted(random.sample(range(1, NUM_TAREAS), num_cortes))
    else:
        puntos_de_corte = []
    c_ii = puntos_de_corte
    return [c_i, c_ii]

def crear_poblacion_inicial():
    return [crear_individuo() for _ in range(TAMANO_POBLACION)]

def decodificar_cromosoma(individuo, tareas, drones):
    c_i, c_ii = individuo
    rutas_drones = {dron["id"]: [] for dron in drones}
    num_drones_reales = len(c_ii) + 1
    puntos_corte_extendidos = [0] + c_ii + [NUM_TAREAS]
    for i in range(num_drones_reales):
        idx_inicio = puntos_corte_extendidos[i]
        idx_fin = puntos_corte_extendidos[i+1]
        id_tareas_asignadas = c_i[idx_inicio:idx_fin]
        if i < len(drones):
            rutas_drones[i] = [tareas[id_tarea] for id_tarea in id_tareas_asignadas]
    return rutas_drones

def encontrar_estacion_mas_cercana(punto, estaciones):
    distancias = [np.linalg.norm(np.array(punto) - np.array(estacion)) for estacion in estaciones]
    return estaciones[np.argmin(distancias)]

def calcular_energia(distancia, peso_carga):
    consumo_base = distancia * CONSUMO_POR_DISTANCIA
    consumo_carga = distancia * peso_carga * CONSUMO_EXTRA_POR_PESO
    return consumo_base + consumo_carga

def funcion_fitness(individuo, tareas, drones, estaciones_carga):
    rutas = decodificar_cromosoma(individuo, tareas, drones)
    energia_total_flota = 0
    tiempo_maximo = 0
    for id_dron, tareas_asignadas in rutas.items():
        posicion_actual = drones[id_dron]["posicion_inicial"]
        bateria_actual = BATERIA_MAXIMA
        tiempo_dron = 0
        for tarea in tareas_asignadas:
            dist_base_a_pickup = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
            energia_ida = calcular_energia(dist_base_a_pickup, 0)
            dist_pickup_a_dropoff = np.linalg.norm(np.array(tarea["pickup"]) - np.array(tarea["dropoff"]))
            energia_vuelta = calcular_energia(dist_pickup_a_dropoff, tarea["peso"])
            estacion_post_tarea = encontrar_estacion_mas_cercana(tarea["dropoff"], estaciones_carga)
            dist_dropoff_a_estacion = np.linalg.norm(np.array(tarea["dropoff"]) - np.array(estacion_post_tarea))
            energia_a_estacion_segura = calcular_energia(dist_dropoff_a_estacion, 0)
            energia_requerida_total = energia_ida + energia_vuelta + energia_a_estacion_segura
            if energia_requerida_total > bateria_actual - BATERIA_RESERVA:
                estacion_mas_cercana = encontrar_estacion_mas_cercana(posicion_actual, estaciones_carga)
                dist_a_carga = np.linalg.norm(np.array(posicion_actual) - np.array(estacion_mas_cercana))
                energia_viaje_carga = calcular_energia(dist_a_carga, 0)
                tiempo_dron += dist_a_carga / VELOCIDAD_DRON
                energia_total_flota += energia_viaje_carga
                bateria_actual = BATERIA_MAXIMA
                posicion_actual = estacion_mas_cercana
            dist_a_pickup = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["pickup"]))
            energia_consumida_ida = calcular_energia(dist_a_pickup, 0)
            bateria_actual -= energia_consumida_ida
            energia_total_flota += energia_consumida_ida
            tiempo_dron += dist_a_pickup / VELOCIDAD_DRON
            posicion_actual = tarea["pickup"]
            dist_a_dropoff = np.linalg.norm(np.array(posicion_actual) - np.array(tarea["dropoff"]))
            energia_consumida_vuelta = calcular_energia(dist_a_dropoff, tarea["peso"])
            bateria_actual -= energia_consumida_vuelta
            energia_total_flota += energia_consumida_vuelta
            tiempo_dron += dist_a_dropoff / VELOCIDAD_DRON
            posicion_actual = tarea["dropoff"]
        if tiempo_dron > tiempo_maximo:
            tiempo_maximo = tiempo_dron
    return 1 / (energia_total_flota * tiempo_maximo + 1e-6)

def seleccion(poblacion, fitness_scores):
    sorted_population = [x for _, x in sorted(zip(fitness_scores, poblacion), key=lambda pair: pair[0], reverse=True)]
    return sorted_population[:len(poblacion) // 2]

def partial_mapped_crossover(padre1, padre2):
    if padre1 == padre2:
        return padre1, padre2
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
    for i in list(range(start)) + list(range(end + 1, size)):
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
    for i in range(0, len(padres) - (len(padres) % 2), 2):
        padre1, padre2 = padres[i], padres[i+1]
        c_i_hijo1, c_i_hijo2 = partial_mapped_crossover(padre1[0], padre2[0])
        if len(padre1[1]) > 0:
            corte_cruce = random.randint(0, len(padre1[1]))
        else:
            corte_cruce = 0
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
    
def visualizar_rutas(mejor_solucion, tareas, drones, poligono, estaciones_carga, filename="rutas_drones_final.html"):
    rutas_decodificadas = decodificar_cromosoma(mejor_solucion, tareas, drones)
    mapa = folium.Map(location=CENTRO_ROSARIO, zoom_start=13)
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
            folium.Marker(location=tarea["pickup"], popup=f"Pedido {tarea['id']} Pickup (Dron {id_dron})", icon=folium.Icon(color=color_ruta, icon='box', prefix='fa')).add_to(mapa)
            folium.Marker(location=tarea["dropoff"], popup=f"Pedido {tarea['id']} Dropoff (Dron {id_dron})", icon=folium.Icon(color=color_ruta, icon='check-circle', prefix='fa')).add_to(mapa)
            puntos_ruta.append(tarea["pickup"])
            puntos_ruta.append(tarea["dropoff"])
        folium.PolyLine(puntos_ruta, color=color_ruta, weight=2.5, opacity=1).add_to(mapa)
    mapa.save(filename)
    print(f"Mapa guardado en '{filename}'")

# --- 4. EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    tareas = generar_tareas(NUM_TAREAS, POLIGONO_ROSARIO)
    drones = generar_drones(NUM_DRONES, POLIGONO_ROSARIO)
    estaciones_carga = generar_estaciones_carga(NUM_ESTACIONES, POLIGONO_ROSARIO)
    poblacion = crear_poblacion_inicial()
    mejor_solucion_global = None
    mejor_fitness_global = -1
    for gen in range(NUM_GENERACIONES):
        fitness_scores = [funcion_fitness(ind, tareas, drones, estaciones_carga) for ind in poblacion]
        mejor_fitness_gen = max(fitness_scores)
        if mejor_fitness_gen > mejor_fitness_global:
            mejor_fitness_global = mejor_fitness_gen
            mejor_solucion_global = poblacion[fitness_scores.index(mejor_fitness_gen)]
        padres = seleccion(poblacion, fitness_scores)
        descendencia = cruce(padres)
        if descendencia:
            poblacion = descendencia + padres[:len(poblacion) - len(descendencia)]
            poblacion = [mutacion(ind) for ind in poblacion]
        if (gen + 1) % 10 == 0: 
            print(f"Generación {gen+1}/{NUM_GENERACIONES} - Mejor Fitness: {mejor_fitness_global:.6f}")
    print("\n--- Optimización Finalizada ---")
    if mejor_solucion_global:
        print(f"Mejor solución encontrada: {mejor_solucion_global}")
        visualizar_rutas(mejor_solucion_global, tareas, drones, POLIGONO_ROSARIO, estaciones_carga)
    else:
        print("No se encontró una solución válida.")