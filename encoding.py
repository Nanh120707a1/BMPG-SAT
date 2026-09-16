def var(i, label, n):
    return (i - 1) * n + label

def base_encoding(n):
    clauses = []

    # Mỗi đỉnh có ít nhất một nhãn
    for i in range(1, n + 1):
        clauses.append([
            var(i, label, n)
            for label in range(1, n + 1)
        ])

    # Mỗi nhãn được nhiều nhất một đỉnh sử dụng
    for label in range(1, n + 1):
        for u in range(1, n):
            for v in range(u + 1, n + 1):
                clauses.append([
                    -var(u, label, n),
                    -var(v, label, n)
                ])

    return clauses

def bandwidth_constraints(n, edges, p):
    clauses = []

    for u, v in edges:
        for a in range(1, n + 1):
            for b in range(1, n + 1):
                if abs(a - b) > p:
                    clauses.append([
                        -var(u, a, n),
                        -var(v, b, n)
                    ])

    return clauses