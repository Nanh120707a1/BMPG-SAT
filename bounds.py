from collections import deque


def make_adjacency(n, edges):
    adj = [[] for _ in range(n + 1)]

    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    return adj


def bandwidth_of_order(order, edges):
    position = {}

    for label, vertex in enumerate(order, start=1):
        position[vertex] = label

    bandwidth = 0

    for u, v in edges:
        bandwidth = max(
            bandwidth,
            abs(position[u] - position[v])
        )

    return bandwidth

def upper_bound(n, edges):
    adj = make_adjacency(n, edges)

    visited = [False] * (n + 1)
    order = []

    starts = sorted(
        range(1, n + 1),
        key=lambda v: len(adj[v])
    )

    for start in starts:

        if visited[start]:
            continue

        queue = deque([start])
        visited[start] = True

        while queue:

            u = queue.popleft()
            order.append(u)

            neighbors = sorted(
                adj[u],
                key=lambda v: len(adj[v])
            )

            for v in neighbors:

                if not visited[v]:
                    visited[v] = True
                    queue.append(v)

    return bandwidth_of_order(order, edges)

def lower_bound(n, edges):
    if not edges:
        return 0

    degree = [0] * (n + 1)

    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    max_degree = max(degree)

    # ceil(max_degree / 2)
    return (max_degree + 1) // 2