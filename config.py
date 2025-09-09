# Almacena todos los parámetros y constantes del proyecto.
import numpy as np

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
NUM_TAREAS = 5
NUM_DRONES = 2
NUM_ESTACIONES = 2
TAMANO_POBLACION = 100 # cantidad de individuos (flotas) por generación
PROBABILIDAD_MUTACION = 0.1
PROBABILIDAD_CRUCE = 0.75
EPSILON = 300 # Tolerancia de energía entre soluciones Esto me parece que es un numero muy chico, deberi ser mas grande
NUM_GENERACIONES = 1000
NCONV = 100 # Número de generaciones sin mejora para considerar convergencia
N_BEST = 5  # Cantidad de mejores individuos que se mantienen en cada generación de la población (P Unión POPP)
# --- Factor de Penalización ---
PENALTY_VALUE = 1e12  # Valor grande para penalizar soluciones inviables.

# --- PARÁMETROS DE LA SIMULACIÓN ---
VELOCIDAD_DRON = 10  # m/s
PESO_MAX_PAQUETE = 2.7  # kg, peso máximo del paquete
TIEMPO_MIN_MIN = 20  # minutos
TIEMPO_MAX_MIN = 75  # minutos

# --- PARÁMETROS FÍSICOS DEL DRON Multirotor (DJI Matrice 300 RTK con 2 baterías TB60) ---
BATERIA_MAXIMA = 2 * (274 * 3600) #[Joules] --> 2 (baterias) * (Wh de cada bateria * 3600 s para conversión de Wh a Joules) 
MASA_DRON = 6.3 # [Kg] mi, masa del dron
PAYLOAD_MAX = 2.7 # [Kg] mp, carga máxima del paquete del dron
RHO = 1.225  # rho, densidad del aire en kg/m^3 al nivel del mar
AREA_FRONTAL_DRON = 0.2  # m^2 (estimación: calibrar)
COEFICIENTE_ARRASTRE = 1.0  # c_d, adimensional
FIGURE_OF_MERIT = 0.7  # F_M, eficiencia del rotor, adimensional
AREA_ROTOR = 0.89383 #[m^2] Ar, área del rotor
EFICIENCIA_GLOBAL = 0.9 # eta, eficiencia global del sistema
G = 9.81 # Aceleración gravitacional