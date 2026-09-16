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
    left = 1
    right = n - 1

    best_p = None
    best_model = None

    while left <= right:
        mid = (left + right) // 2

        model = check(n, edges, mid)

        if model is not None:
            best_p = mid
            best_model = model
            right = mid - 1
        else:
            left = mid + 1

    return best_p, best_model