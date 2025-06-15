def parse_equation(equation):
    left, right = equation.split("->")
    reactants = _parse_side(left)
    products = _parse_side(right)
    return reactants, products

def _parse_side(side):
    parts = side.split("+")
    species = {}
    for part in parts:
        part = part.strip()
        tokens = part.split(" ")
        if len(tokens) == 1:
            coeff = 1
            formula = tokens[0]
        else:
            try:
                coeff = float(tokens[0])
                formula = tokens[1]
            except ValueError:
                coeff = 1
                formula = part
        species[formula] = coeff
    return species

