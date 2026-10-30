from collections import deque


def make_adjacency(n, edges):
    adj = [[] for _ in range(n + 1)]

    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    return adj


def bandwidth_of_order(order, edges):
    position = {v: i for i, v in enumerate(order, start = 1)}

    return max((abs(position[u] - position[v]) for u, v in edges), default = 0)

def components(n, adj):
    seen = [False] * (n+1)
    result = []
    for s in range(1, n+1):
        if seen[s]:
            continue
        seen[s] = True
        queue = deque([s])
        comp = [s]
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    queue.append(v)
                    comp.append(v)
        result.append(comp)
    return result

def _bfs_dist(adj, s):
    dist = {s : 0}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist

def upper_bound(n, edges, adj = None):
    if adj is None:
        adj = make_adjacency(n, edges)

    deg = [len(a) for a in adj]
    neighbors = [sorted(a, key = lambda x: deg[x]) for a in adj]

    best_bw, best_order = None, None
    # thử cuthill - mckee xuất phát từ mọi đỉnh 1->n

    for start in range(1, n+1):
        seen = [False]*(n+1)
        seen[start] = True
        queue = deque([start])
        order = []
        while queue:
            u = queue.popleft()
            order.append(u)
            for v in neighbors[u]:
                if not seen[v]:
                    seen[v] = True
                    queue.append(v)
        bw = bandwidth_of_order(order, edges)
        if best_bw is None or bw < best_bw:
            best_bw, best_order = bw, order
    return best_bw, best_order

def lower_bound(n, edges, adj =None):
    if not edges:
        return 0

    if adj is None:
        adj = make_adjacency(n, edges)

    best, diameter = 0,0
    for v in range(1, n+1):
        dist = bfs_dist(adj, v)
        ecc = max(dist.values())
        diameter = max(diameter, ecc)
        count = [0]*(ecc + 1)
        for d in dist.values():
            count[d] += 1
        total = 0
        for r in range(ecc + 1):
            total += count[r]
            if r >= 1:
                # |B(v, r)| - 1 <= 2*r*bw
                # => bw >= ceil((|B(v, r) -1) / (2*r))
                best = max(best, -(-(total-1) // (2*r)))
    if diameter > 0:
        # bw >= ceil((n-1) / diameter)
        best = max(best, -(-(n-1) // diameter))
    return best
