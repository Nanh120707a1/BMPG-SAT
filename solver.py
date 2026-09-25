from pysat.solvers import Cadical195

from encoding import base_encoding, bandwidth_constraints


def check(n, edges, p):
    clauses = base_encoding(n)
    clauses += bandwidth_constraints(n, edges, p)

    with Cadical195(bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None

        return solver.get_model()


def solve(n, edges):
    start = 0 if not edges else 1
    for p in range(start, n):
        model = check(n, edges, p)

        if model is not None:
            return p, model

    return None, None
