import random

def swap_mutation(task_order):
    """Intercambia dos tareas aleatorias."""
    a, b = random.sample(range(len(task_order)), 2)
    task_order[a], task_order[b] = task_order[b], task_order[a]
    return task_order

def reverse_segment(task_order):
    """Invierte un segmento del cromosoma."""
    a, b = sorted(random.sample(range(len(task_order)), 2))
    task_order[a:b] = reversed(task_order[a:b])
    return task_order

def mutate_cuts(cuts, num_tasks):
    """Modifica levemente los cortes entre tareas de drones."""
    new_cuts = cuts[:]
    idx = random.randint(0, len(cuts)-1)
    delta = random.choice([-1, 1])
    new_cuts[idx] = max(1, min(num_tasks - 1, new_cuts[idx] + delta))
    return sorted(new_cuts)
