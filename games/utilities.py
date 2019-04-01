import math

def all_permutations(items):
    """
    Build all the possible permutations of a set of items.
    """

    if(len(items) == 0):
        return [[]]

    permutations = []

    for item in items:
        other_items = list(filter(lambda el: el != item, items))
        permutations_of_other = all_permutations(other_items)
        for p in permutations_of_other:
            p.append(item)
            permutations.append(p)

    return permutations

def pair_to_number(x, y):
    """
    Implementation of the Cantor Pairing Function.
    """

    return (x + y + 1) * (x + y) / 2 + y

def number_to_pair(z):
    """
    Inverse of the Cantor Pairing Function.
    """

    w = math.floor((math.sqrt(8 * z + 1) - 1) / 2)
    t = (w * w + w) / 2
    y = z - t
    x = w - y
    return (x, y)