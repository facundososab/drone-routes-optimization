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

