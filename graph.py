def read_graph(filename):
    with open(filename, "r") as f:
        n = int(f.readline())
        m = int(f.readline())

        edges = []

        for _ in range(m):
            u, v = map(int, f.readline().split())
            edges.append((u, v))

    return n, m, edges