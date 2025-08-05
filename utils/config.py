# Constantes físicas
G = 9.81  # Aceleración gravitacional (m/s²)
RHO = 1.225  # Densidad del aire (kg/m³)

# Parámetros del dron (constantes fijas por UAV)
DRONE_PARAMS = {
    "mass": 19,           # Masa del UAV i (kg) (https://www.theguardian.com/technology/2025/apr/11/amazon-slayer-dublin-startup-manna-aero-taking-giants-autonomous-drone-deliveries?utm_source=chatgpt.com)
    "cd": 0.8,              # Coeficiente de arrastre
    "A_d": 0.06,            # Área frontal del UAV respecto a su dirección (m²)
    "A_r": 0.1,             # Área del rotor del UAV (m²), estimado
    "figure_of_merit": 0.7  # F_M^i: eficiencia aerodinámica del rotor, valor típico entre 0.6 y 0.75
}

# Variables dinámicas (cambian por tarea o situación)
# Estos se definirán en tiempo de ejecución
DYNAMIC_PARAMS = {
    "L1": None,  # Distancia del UAV al punto de recogida del paquete (m)
    "L2": None,  # Distancia del pick-up al drop-off (m)
    "L3": None,  # Distancia del drop-off a la estación de carga más cercana (m)
    "m_p": None,  # Masa del paquete (kg)
    "v": None     # Velocidad del UAV para la entrega (m/s)
}
