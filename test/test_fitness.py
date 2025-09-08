from simulation import funcion_fitness
import config

# Datos dummy de ejemplo
individuo = [
    [0, 1],  # Orden de tareas (índices)
    []        # Sin cortes, un solo dron
]

tareas = [
    {
        "id": 0,
        "pickup": [0.0, 0.0],
        "dropoff": [1.0, 1.0],
        "peso": 1.0,
        "tiempo_max": 1000
    },
    {
        "id": 1,
        "pickup": [1.0, 1.0],
        "dropoff": [2.0, 2.0],
        "peso": 1.0,
        "tiempo_max": 1000
    }
]

drones = [
    {
        "id": 0,
        "posicion_inicial": [0.0, 0.0]
    }
]

estaciones = [
    [0.0, 0.0],
    [2.0, 2.0]
]

# Ejecutar el test
resultado = funcion_fitness(individuo, tareas, drones, estaciones)
print("Resultado fitness:", resultado)
