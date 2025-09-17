# **Optimización de Rutas de Drones con Algoritmos Genéticos**

## **Descripción del Proyecto**

Este proyecto aborda el problema de optimización de rutas y asignación de tareas para una flota de drones en un entorno urbano. Utilizando algoritmos genéticos, se busca minimizar el consumo de energía total, garantizar el cumplimiento de los tiempos de entrega y optimizar la planificación de recargas en estaciones de carga. El enfoque propuesto se enmarca dentro de los problemas de **Scheduling**, donde se asignan y secuencian tareas sobre un conjunto de recursos limitados.

---

## **Estructura del Proyecto**

El proyecto está organizado en los siguientes módulos principales:

### **1. [`genetic_algorithm.py`](genetic_algorithm.py)**

Contiene la implementación de los operadores genéticos principales, incluyendo:

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

- **Características y especificaciones de los drones**: Velocidad, capacidad de batería, masa, etc.
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
   Ejecuta el script para generar estaciones de carga (desde la raíz del proyecto):

   ```bash
   python -m test.generar_estaciones 
   ```

2. **Ejecutar el algoritmo genético**:
   Corre el flujo principal del algoritmo:

   ```bash
   python main.py
   ```

3. **Visualizar resultados**:
   Los resultados incluyen:
   - Mapas interactivos generados con `folium`.
   - Gráficas de evolución del fitness generadas con `matplotlib`.
   - KPIs de las corridas en archivo .xlsx

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
  "tiempo_max": 900,
  "recarga_previa"
}
```

### **Drones**

Cada dron tiene los siguientes atributos:

```json
{
  "id": 0,
  "posicion_inicial": [lat, lon],
}
```

### **Estaciones de Carga**

Cada estación tiene los siguientes atributos:

```json
{
  "ubicacion": [lat, lon]
}
```

---

## **Resultados Esperados**

- **Optimización energética**: Minimización del consumo total de energía de la flota.
- **Cumplimiento de tiempos**: Los individuos que no cumplen con los tiempos previstos se descartan
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