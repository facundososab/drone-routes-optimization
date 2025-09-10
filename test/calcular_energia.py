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

import numpy as np


import numpy as np
def calcular_energia(L1, L2, L3, v, mpj):
    """
    FUNCION OBJETIVO
    Calcula la energía consumida por un UAV durante una entrega,
    basado en el modelo matemático del paper.
    """
    # Término 1: Consumo por resistencia aerodinámica
    term1 = COEFICIENTE_ARRASTRE * RHO * AREA_FRONTAL_DRON * (L1 + L2 + L3) * v**2
    
    # Constante para los términos de sustentación
    sustentacion_const = v * FIGURE_OF_MERIT * np.sqrt(2 * RHO * AREA_ROTOR)
    
    # Término 2: Consumo por sustentación con carga
    numerador2 = L2 * np.sqrt(((MASA_DRON + mpj) * G)**3)
    term2 = numerador2 / sustentacion_const

    # Término 3: Consumo por sustentación sin carga
    numerador3 = (L1 + L3) * np.sqrt((MASA_DRON * G)**3)
    term3 = numerador3 / sustentacion_const

    energia_total = (1 / EFICIENCIA_GLOBAL) * (term1 + term2 + term3)

    # print(f"[calcular_energia] L1={L1:.2f}, L2={L2:.2f}, L3={L3:.2f}, v={v}, mpj={mpj} => "
    #       f"term1={term1:.4f}, term2={term2:.4f}, term3={term3:.4f}, energia={energia_total:.4f}")

    return energia_total

def test_calcular_energia():
    # Parámetros de prueba
    velocidades = [5, 10, 15]  # m/s
    cargas = [0, 1, 2.7]       # kg
    distancias = [
        (100, 200, 100),  # L1, L2, L3 (m)
        (500, 1000, 500),
        (1000, 2000, 1000),
    ]

    print("=== Test de calcular_energia ===")
    for v in velocidades:
        for mpj in cargas:
            for (L1, L2, L3) in distancias:
                energia = calcular_energia(L1, L2, L3, v, mpj)
                print(
                    f"v={v:>2} m/s | carga={mpj:.1f} kg | "
                    f"L1={L1}, L2={L2}, L3={L3} m => "
                    f"Energia = {energia:.2e} J"
                )

    # Caso extra: comparar efecto de la carga
    print("\n=== Comparación carga ===")
    energia_sin_carga = calcular_energia(500, 1000, 500, 10, 0)
    energia_con_carga = calcular_energia(500, 1000, 500, 10, 2.7)
    print(f"Sin carga: {energia_sin_carga:.2e} J")
    print(f"Con carga máxima: {energia_con_carga:.2e} J")
    print(f"Factor aumento: {energia_con_carga/energia_sin_carga:.2f}x")

if __name__ == "__main__":
    test_calcular_energia()

