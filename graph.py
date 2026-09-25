from scipy.io import mmread


def read_graph(filename):
    A = mmread(filename).tocoo()

    if A.shape[0] != A.shape[1]:
        raise ValueError("Ma tran do thi phai la ma tran vuong")

    n = A.shape[0]
    edge_set = set()

    for row, col in zip(A.row, A.col):
        u = int(row) + 1
        v = int(col) + 1

        # Bỏ khuyên
        if u == v:
            continue

        if u > v:
            u, v = v, u

        edge_set.add((u, v))

    edges = sorted(edge_set)
    m = len(edges)

    return n, m, edges