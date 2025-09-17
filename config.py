# Almacena todos los parámetros y constantes del proyecto.
import numpy as np
import math

# --- PARÁMETROS GEOGRÁFICOS ---
POLIGONO_ROSARIO = [ #(lat,lon)
    (-32.960350, -60.684600), 
    (-32.926592, -60.676048),
    (-32.925379, -60.660771), 
    (-32.939847, -60.634862),
    (-32.960690, -60.620853), 
    (-32.971469, -60.622220)
]
CENTRO_ROSARIO = np.mean(POLIGONO_ROSARIO, axis=0).tolist()

# --- PARÁMETROS DEL ALGORITMO GENÉTICO ---
NUM_TAREAS = 60 #A partir de las entregas promedio diarias, voy a tener una cantidad de drones.
NUM_DRONES = 10 #Si la cant. de drones es baja, voy a tener que aumentar los tiempos de entrega (sino todas las soluciones son inviables) --> Peor servicio (SLA bajo).
NUM_ESTACIONES = 15
TAMANO_POBLACION = 50 # cantidad de individuos (flotas) por generación
PROBABILIDAD_MUTACION = 0.05
PROBABILIDAD_CRUCE = 0.3 #0.3 da buenos resultados. Mayor a 0.3 puede ser inestable
NUM_GENERACIONES = 20
N_BEST = math.floor((0.5)*TAMANO_POBLACION)  # Cantidad de mejores individuos que se mantienen en cada generación de la población (P Unión POPP).
K_TORNEO = math.floor((3/4)*TAMANO_POBLACION) # Número de individuos en cada torneo (mínimo 2)

# --- PARÁMETROS DE LA SIMULACIÓN ---
VELOCIDAD_DRON = 10  # m/s
PESO_MAX_PAQUETE = 2.7  # kg, peso máximo del paquete
TIEMPO_MIN_MIN = 60  # minutos.  #Si hay pocos drones y muchas tareas, aumentar este valor
TIEMPO_MAX_MIN = 90  # minutos.

# --- PARÁMETROS FÍSICOS DEL DRON Multirotor (DJI Matrice 300 RTK con 2 baterías TB60) ---
BATERIA_MAXIMA = (2 * (274 * 3600)) #[MJoules] --> 2 (baterias) * (Wh de cada bateria * 3600 s para conversión de Wh a Joules) 
MASA_DRON = 6.3 # [Kg] mi, masa del dron
PAYLOAD_MAX = 2.7 # [Kg] mp, carga máxima del paquete del dron
RHO = 1.225  # rho, densidad del aire en kg/m^3 al nivel del mar
AREA_FRONTAL_DRON = 0.2  # m^2 (estimación: calibrar)
COEFICIENTE_ARRASTRE = 1.0  # c_d, adimensional
FIGURE_OF_MERIT = 0.7  # F_M, eficiencia del rotor, adimensional
AREA_ROTOR = 0.89383 #[m^2] Ar, área del rotor
EFICIENCIA_GLOBAL = 0.9 # eta, eficiencia global del sistema
G = 9.81 # Aceleración gravitacional

ESTACIONES_DE_CARGA = None
