import random

def swap_mutation(task_order):
    """Intercambia dos tareas aleatorias."""
    a, b = random.sample(range(len(task_order)), 2) ##Selecciona dos posiciones aleatorias en la lista task_order.
    task_order[a], task_order[b] = task_order[b], task_order[a] ##Intercambia las tareas en esas posiciones.
    return task_order

def reverse_segment(task_order):
    """Invierte un segmento del cromosoma."""
    a, b = sorted(random.sample(range(len(task_order)), 2)) ## Selecciona dos posiciones aleatorias y define un segmento entre ellas.
    task_order[a:b] = reversed(task_order[a:b]) ## Invierte el orden de las tareas en ese segmento.
    return task_order

def cuts_mutation(cuts, num_tasks):
    """Modifica levemente los cortes entre tareas de drones."""
    new_cuts = cuts[:] ##Copia la lista de cortes para no modificar la original.
    idx = random.randint(0, len(cuts)-1) ##Selecciona un índice aleatorio en la lista de cortes.
    delta = random.choice([-1, 1]) ##Decide si aumentar o disminuir el corte.
    new_cuts[idx] = max(1, min(num_tasks - 1, new_cuts[idx] + delta)) ##Ajusta el corte, asegurándose de que esté dentro de los límites válidos.
    return sorted(new_cuts)
