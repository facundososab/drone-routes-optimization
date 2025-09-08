from config import CENTRO_ROSARIO
from points_generator import distancia_metros

print("Distancia Rosario-BsAs:", distancia_metros((-32.95, -60.65), (-34.60, -58.38)), "m") #aprox 278000m (278km)
print("Distancia Rosario-Centro:", distancia_metros(CENTRO_ROSARIO, CENTRO_ROSARIO), "m") #debe dar 0