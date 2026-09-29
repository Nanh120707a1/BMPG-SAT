from encoding import var

def decode_model(model, n):

    positive = {
        x for x in model
        if x > 0
    }

    labels = {}

    for v in range(1, n + 1):

        found = []

        for label in range(1, n + 1):

            if var(v, label, n) in positive:
                found.append(label)

        if not found:
            raise ValueError(
                f"Dinh {v} khong co label"
            )

        labels[v] = max(found)

    return labels

def check_result(n, edges, labels, bandwidth):
    # 1. Tất cả n đỉnh đều phải có nhãn
    if len(labels) != n:
        return False

    # 2. Nhãn phải nằm trong [1, n]
    for i in range(1, n + 1):
        if i not in labels:
            return False

        if labels[i] < 1 or labels[i] > n:
            return False

    # 3. Không có hai đỉnh nhận cùng một nhãn
    if len(set(labels.values())) != n:
        return False

    # 4. Kiểm tra bandwidth trên từng cạnh
    for u, v in edges:
        if abs(labels[u] - labels[v]) > bandwidth:
            return False

    return True