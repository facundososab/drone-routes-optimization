import os
import matplotlib.pyplot as plt

def plot_fitness_evolution(max_fitness, avg_fitness, min_fitness, generations, filename="evolucion_fitness.png"):
    """
    Genera una gráfica de la evolución del fitness y la guarda en la carpeta 'resultados'.

    Parámetros:
        max_fitness (list): Valores máximos de fitness por generación.
        avg_fitness (list): Valores promedio de fitness por generación.
        min_fitness (list): Valores mínimos de fitness por generación.
        generations (int): Número total de generaciones.
        filename (str): Nombre del archivo para guardar el gráfico.
    """
    print("\n📊 Valores de fitness por generación:")
    print("Máximos:", max_fitness)
    print("Promedios:", avg_fitness)
    print("Mínimos:", min_fitness)


    generations_axis = list(range(1, generations + 1))

    plt.figure(figsize=(12, 6))
    plt.plot(generations_axis, max_fitness, label='Máximo Fitness', color='orange')
    plt.plot(generations_axis, avg_fitness, label='Promedio Fitness', color='blue')
    plt.plot(generations_axis, min_fitness, label='Mínimo Fitness', color='green')

    # Encontrar el valor máximo de fitness y su generación
    max_value = max(max_fitness)
    max_gen = generations_axis[max_fitness.index(max_value)]

    # Agregar etiqueta en el gráfico
    plt.annotate(
        f'Max: {max_value:.2f}\nGen: {max_gen}',
        xy=(max_gen, max_value),
        xytext=(max_gen, max_value + (0.05 * max_value)),  # un poquito arriba
        arrowprops=dict(facecolor='black', shrink=0.05),
        ha='center'
    )

    plt.xlabel('Generación')
    plt.ylabel('Fitness')
    plt.title(f'Evolución del Fitness a lo largo de {generations} generaciones')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Crear carpeta si no existe
    output_dir = "resultados"
    os.makedirs(output_dir, exist_ok=True)

    # Guardar gráfico
    file_path = os.path.join(output_dir, filename)
    plt.savefig(file_path)
    plt.close()
    print(f"Gráfico de evolución del fitness guardado en '{file_path}'")
