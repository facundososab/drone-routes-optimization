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
NUM_TAREAS = 15
NUM_DRONES = 5
NUM_ESTACIONES = 6
TAMANO_POBLACION = 50
PROBABILIDAD_MUTACION = 0.2
EPSILON = 300  # Tolerancia de energía entre soluciones
NUM_GENERACIONES = 1000
NCONV = 200        # Número de generaciones sin mejora para considerar convergencia

# --- PARÁMETROS DE LA SIMULACIÓN ---
VELOCIDAD_DRON = 16  # m/s, variable de decisión
BATERIA_MAXIMA = 680000  # Joules
PESO_MAX_PAQUETE = 2.0  # kg, peso máximo del paquete
TIEMPO_MIN_MIN = 20  # minutos
TIEMPO_MAX_MIN = 75  # minutos

# --- PARÁMETROS FÍSICOS Y DEL DRON (para tu nueva función) ---
MASA_DRON = 1 # mi, masa del dron en kg
RHO = 1.225  # rho, densidad del aire en kg/m^3
AREA_FRONTAL_DRON = 0.4  # Ad, en m^2
COEFICIENTE_ARRASTRE = 1.0  # c_d, adimensional
FIGURE_OF_MERIT = 0.7  # F_M, eficiencia del rotor, adimensional
AREA_ROTOR = 0.2# Ar, área del rotor
EFICIENCIA_GLOBAL = 0.9 # eta, eficiencia global del sistema
G = 9.81 # Aceleración gravitacional