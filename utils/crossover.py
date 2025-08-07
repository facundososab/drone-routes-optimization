import random

def pmx(parent1, parent2):
    """Partial Mapped Crossover para orden de tareas."""
    size = len(parent1)
    p1, p2 = parent1[:], parent2[:]

    cxpoint1 = random.randint(0, size - 2)
    cxpoint2 = random.randint(cxpoint1 + 1, size - 1)

    child = [None]*size
    child[cxpoint1:cxpoint2+1] = p1[cxpoint1:cxpoint2+1]

    for i in range(cxpoint1, cxpoint2+1):
        if p2[i] not in child:
            val = p2[i]
            pos = i
            while True:
                val_in_p1 = p1[pos]
                pos = p2.index(val_in_p1)
                if child[pos] is None:
                    break
            child[pos] = val

    for i in range(size):
        if child[i] is None:
            child[i] = p2[i]

    return child
