from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def var(vertex, label, n):
    """
    L(vertex, label): label(vertex) >= label
    """
    return (vertex - 1) * n + label


def build_static_encoding(n, solver):
    """
    Xây các ràng buộc SAT không phụ thuộc bandwidth.
    Sử dụng transition representation.
    """

    vpool = IDPool(start_from=n * n + 1)
    transition_vars = {}
    clause_count = 0

    # Mọi đỉnh có label >= 1
    for v in range(1, n + 1):
        solver.add_clause([var(v, 1, n)])
        clause_count += 1

    # Tính đơn điệu: L(v,k) -> L(v,k-1)
    for v in range(1, n + 1):
        for k in range(2, n + 1):
            solver.add_clause([
                -var(v, k, n),
                var(v, k - 1, n)
            ])
            clause_count += 1

    # T(v,k) <-> L(v,k-1) AND NOT L(v,k)
    for k in range(2, n + 1):
        transitions = []

        for v in range(1, n + 1):
            t = vpool.id()
            transition_vars[(v, k)] = t

            prev = var(v, k - 1, n)
            curr = var(v, k, n)

            solver.add_clause([-t, prev])
            solver.add_clause([-t, -curr])
            solver.add_clause([-prev, curr, t])

            clause_count += 3
            transitions.append(t)

        # Mỗi boundary có đúng một transition
        enc = CardEnc.equals(
            lits=transitions,
            bound=1,
            vpool=vpool,
            encoding=EncType.seqcounter
        )

        for clause in enc.clauses:
            solver.add_clause(clause)

        clause_count += len(enc.clauses)

    # Chính xác một đỉnh có label n
    last_label = [
        var(v, n, n)
        for v in range(1, n + 1)
    ]

    enc = CardEnc.equals(
        lits=last_label,
        bound=1,
        vpool=vpool,
        encoding=EncType.seqcounter
    )

    for clause in enc.clauses:
        solver.add_clause(clause)

    clause_count += len(enc.clauses)

    return vpool, transition_vars, clause_count
def add_bandwidth_bound(n, edges, bandwidth, solver):
    """
    Thêm constraint |label(u) - label(v)| <= bandwidth cho mọi cạnh (u,v).
    L(v,k) -> label(v) >= k
    => L(u,k) -> L(v,k-bandwidth)
    """

    clause_count = 0

    for u, v in edges:

        for k in range(bandwidth + 1, n + 1):

            solver.add_clause([
                -var(u, k, n),
                var(v, k - bandwidth, n)
            ])

            solver.add_clause([
                -var(v, k, n),
                var(u, k - bandwidth, n)
            ])

            clause_count += 2

    return clause_count