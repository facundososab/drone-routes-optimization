# **Optimización de Rutas de Drones con Algoritmos Genéticos**

## **Descripción del Proyecto**

Este proyecto aborda el problema de optimización de rutas y asignación de tareas para una flota de drones en un entorno urbano. Utilizando algoritmos genéticos, se busca minimizar el consumo de energía total, garantizar el cumplimiento de los tiempos de entrega y optimizar la planificación de recargas en estaciones de carga. El enfoque propuesto se enmarca dentro de los problemas de **Scheduling**, donde se asignan y secuencian tareas sobre un conjunto de recursos limitados.

---

## **Estructura del Proyecto**

El proyecto está organizado en los siguientes módulos principales:

### **1. [`genetic_algorithm.py`](genetic_algorithm.py)**

Contiene la implementación del algoritmo genético, incluyendo:

- **Inicialización de la población**: Generación de soluciones iniciales aleatorias.
- **Selección**: Métodos como ruleta, torneo y elitismo.
- **Crossover**: Operador PMX (Partially Mapped Crossover) para combinar soluciones.
- **Mutación**: Introducción de pequeñas modificaciones para mantener la diversidad genética.
- **Evaluación**: Generación de la población descendiente y cálculo de fitness.

### **2. [`simulation.py`](simulation.py)**

Simula la ejecución de las rutas asignadas a los drones y calcula la función objetivo:

- **Decodificación del cromosoma**: Traduce las soluciones genéticas en rutas específicas.
- **Cálculo de energía**: Evalúa el consumo energético de cada dron.
- **Lógica de recarga**: Gestiona las recargas en estaciones cercanas.
- **Restricciones**: Verifica tiempos de entrega y evita que los drones queden varados.

### **3. [`config.py`](config.py)**

Centraliza los parámetros configurables del proyecto, como:

- **Características de los drones**: Velocidad, capacidad de batería, masa.
- **Configuración del algoritmo genético**: Tamaño de la población, probabilidades de crossover y mutación.
- **Entorno de simulación**: Número de tareas, estaciones de carga, límites de tiempo.

### **4. [`points_generator.py`](points_generator.py)**

Genera puntos de pickup, dropoff y estaciones de carga:

- **Puntos aleatorios**: Generación dentro de un polígono definido.
- **Puntos equiespaciados**: Distribución uniforme en el área de simulación.

### **5. Carpeta [`test`](test)**

Contiene scripts y datos para pruebas:

- **`test_main.py`**: Pruebas del flujo completo del algoritmo.
- **`generar_estaciones.py`**: Generación de estaciones de carga basadas en datos geoespaciales.
- **Datos de prueba**: Archivos JSON con tareas, estaciones y configuraciones.

---

## **Requisitos del Proyecto**

### **Lenguaje y Librerías**

- **Python 3.8+**
- Librerías necesarias:
  - [`numpy`](/Users/facundososa/Library/Python/3.9/lib/python/site-packages/numpy/__init__.py)
  - `folium`
  - `osmnx`
  - `matplotlib`

### **Instalación**

1. Clona el repositorio:
   ```bash
   git clone https://github.com/usuario/drone-routes-optimization.git
   cd drone-routes-optimization
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Cómo Ejecutar el Proyecto**

1. **Generar datos de prueba**:
   Ejecuta el script para generar puntos de pickup, dropoff y estaciones de carga:

   ```bash
   python test/generar_estaciones.py
   ```

2. **Ejecutar el algoritmo genético**:
   Corre el flujo principal del algoritmo:

   ```bash
   python test/test_main.py
   ```

3. **Visualizar resultados**:
   Los resultados incluyen:
   - Mapas interactivos generados con `folium`.
   - Gráficas de evolución del fitness generadas con `matplotlib`.

---

## **Estructura de Datos**

### **Tareas**

Cada tarea tiene los siguientes atributos:

```json
{
  "id": 1,
  "pickup": [lat, lon],
  "dropoff": [lat, lon],
  "peso": 2.5,
  "tiempo_max": 900
}
```

### **Drones**

Cada dron tiene los siguientes atributos:

```json
{
  "id": 0,
  "posicion_inicial": [lat, lon],
  "capacidad_bateria": 10000
}
```

### **Estaciones de Carga**

Cada estación tiene los siguientes atributos:

```json
{
  "id": 0,
  "ubicacion": [lat, lon]
}
```

---

## **Resultados Esperados**

- **Optimización energética**: Minimización del consumo total de energía de la flota.
- **Cumplimiento de tiempos**: Reducción de penalizaciones por incumplimiento de plazos.
- **Visualización**: Mapas interactivos que muestran las rutas optimizadas.

---

## **Contribuciones**

Si deseas contribuir al proyecto:

1. Haz un fork del repositorio.
2. Crea una rama para tus cambios:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Envía un pull request.

---

## **Licencia**

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

- Falta por hacer:

- VER FUNCIÓN FITNESS
  Usar al función de calcular energía una sola vez con los tres parametros (a la vez)

Calculamos la energia para L1,L2,L3
Si el dron no tiene bateria para hacer el viaje:
Si tiene la bateria al 100%: --> #Significa que el dron esta en pos inicial o en una estación
Penalizar (ese viaje no se puede hacer)
Sino, ir a la estación de carga mas cercana y verificar que desde la estación, con el 100%, pueda completar la tarea (sino, penalizar)
Si el dron tiene bateria:
Hace el viaje (asegura que llega a L3).

La mejor version es como quedo en simulation.py. Hay que ver L3 porque no siempre vamos a L3 y contamos como que es energia gastada igualmente.

- Crear los puntos fijos de las estaciones de carga (usar API)
- Testear el programa buscando que el algoritmo converga a una solución que sepamos que es correcta (Ruta)
- Asignar los tiempos máximos de realización de tarea a cada dron. Cada tarea tiene un tiempo límite = tiempo ideal entre L1,L2,L3 + tiempo de tolerancia (10 min) + tiempo de cocción (10-30 min random). (ver de hacerlo en la funcion fitness)
- Decidir qué ocurre si el dron se retrasa en una tarea --> ¿Se desestima su fitness? ¿Lo reduce porcentualmente? --> REALIZAR PRUEBAS para evaluar resultados.
- Falta ver como se agregan las rutas de los drones a las estaciones de carga (estaria bueno que no queden dentro de la funcion fitness. sino que queden funciones separadas)
