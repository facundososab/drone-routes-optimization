import os
import matplotlib.pyplot as plt

def plot_fitness_evolution(max_fitness, avg_fitness, min_fitness, generations, mejor_generacion=None, filename="evolucion_fitness.png"):
    """
    Genera una gráfica de la evolución del fitness y la guarda en la carpeta 'resultados'.

    Parámetros:
        max_fitness (list): Valores máximos de fitness por generación.
        avg_fitness (list): Valores promedio de fitness por generación.
        min_fitness (list): Valores mínimos de fitness por generación.
        generations (int): Número total de generaciones.
        filename (str): Nombre del archivo para guardar el gráfico.
    """
    # print("\n📊 Valores de fitness por generación:")
    # print("Máximos:", max_fitness)
    # print("Promedios:", avg_fitness)
    # print("Mínimos:", min_fitness)


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
        f'Max: {max_value:.4f}\nGen: {max_gen}',
        xy=(max_gen, max_value),
        xytext=(max_gen, max_value + (0.05 * max_value)),  # un poquito arriba
        arrowprops=dict(facecolor='black', shrink=0.05),
        ha='center'
    )

    # Si tenemos la información de la mejor solución global, la marcamos
    if mejor_generacion is not None and mejor_generacion <= len(max_fitness):
        plt.axvline(x=mejor_generacion, color='red', linestyle='--', alpha=0.7, linewidth=2)
        plt.text(mejor_generacion, max(max_fitness) * 0.8, f'Mejor\nSolución\nGen {mejor_generacion}', 
                ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))

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

def plot_energia_evolution(max_energy, avg_energy, min_energy, generations, mejor_generacion=None, filename="evolucion_energia.png"):
    """
    Genera una gráfica de la evolución de la energía y la guarda en la carpeta 'resultados'.

    Parámetros:
        max_energy (list): Valores máximos de energía por generación.
        avg_energy (list): Valores promedio de energía por generación.
        min_energy (list): Valores mínimos de energía por generación.
        generations (int): Número total de generaciones.
        mejor_generacion (int, opcional): Generación en la que se encontró la mejor solución global.
        filename (str): Nombre del archivo para guardar el gráfico.
    """

    generations_axis = list(range(1, generations + 1))

    plt.figure(figsize=(12, 6))
    plt.plot(generations_axis, max_energy, label='Máxima Energía', color='red')
    plt.plot(generations_axis, avg_energy, label='Promedio Energía', color='blue')
    plt.plot(generations_axis, min_energy, label='Mínima Energía', color='green')

    # Encontrar el valor mínimo de energía y su generación
    min_value = min(min_energy)
    min_gen = generations_axis[min_energy.index(min_value)]

    # Agregar etiqueta en el gráfico
    plt.annotate(
        f'Min: {min_value:.2f}\nGen: {min_gen}',
        xy=(min_gen, min_value),
        xytext=(min_gen, min_value * 1.05),  # un poquito arriba
        arrowprops=dict(facecolor='black', shrink=0.05),
        ha='center'
    )

    # Si tenemos la información de la mejor solución global, la marcamos
    if mejor_generacion is not None and mejor_generacion <= len(min_energy):
        plt.axvline(x=mejor_generacion, color='purple', linestyle='--', alpha=0.7, linewidth=2)
        plt.text(
            mejor_generacion,
            max(max_energy) * 0.8,
            f'Mejor\nSolución\nGen {mejor_generacion}',
            ha='center',
            va='center',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7)
        )

    plt.xlabel('Generación')
    plt.ylabel('Energía (MJ)')
    plt.title(f'Evolución de la Energía a lo largo de {generations} generaciones')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Crear carpeta si no existe
    output_dir = "resultados"
    os.makedirs(output_dir, exist_ok=True)

    # Guardar gráfico
    file_path = os.path.join(output_dir, filename)
    plt.savefig(file_path, dpi=300)
    plt.close()
    print(f"Gráfico de evolución de la energía guardado en '{file_path}'")

