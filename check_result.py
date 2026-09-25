def decode_model(model, n):
    labels = {}

    for x in model:
        if 1 <= x <= n * n:
            vertex = (x - 1) // n + 1
            label = (x - 1) % n + 1

            if vertex in labels and labels[vertex] != label:
                raise ValueError(
                    f"Dinh {vertex} nhan nhieu nhan"
                )

            labels[vertex] = label

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