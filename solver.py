import json

from pysat.solvers import Cadical300

from encoding import build_static_encoding, add_bandwidth_bound, add_symmetry_breaking
from bounds import lower_bound, upper_bound, make_adjacency, components
from check_result import decode_model


def write_progress(path, data):
    if path is None:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def solve_connected(n, edges, order0, ub, lb, progress, tag):
    """
    Giải bandwidth tối ưu cho một thành phần liên thông n đỉnh
    - order0: thứ tự gán nhãn đạt bandwidth = ub (nghiệm dự phòng hợp lệ)
    """
    best_bw = ub
    best_labels = {v: i for i, v in enumerate(order0, start = 1)}

    if lb >= ub: # cận dưới chạm hoặc vượt cận trên -> tối ưu ngay, ko gọi SAT
        return best_bw, best_labels

    solver = Cadical300()
    try:
        build_static_encoding(n, solver)
        add_symmetry_breaking(n, edges, solver)

        target = ub -  1 # ub đã đạt được bởi order0, probe đầu tiên là ub -1
        check_index = 0
        while target >= lb:
            check_index += 1
            progress({
                "status" : "SOLVING",
                "component" : tag,
                "current_bandwidth" : target,
                "check_index" : check_index,
                "lower_bound" :  lb,
                "upper_bound" : ub,
                "best_sat_bandwidth" : best_bw
            })

            # bound chỉ siết chặt dần -> thêm clause vĩnh viễn
            add_bandwidth_bound(n, edges, target, solver)

            if not solver.solve():
                progress({
                    "status" : "UNSAT",
                    "component" : tag,
                    "current_bandwidth" : target,
                    "check_index" : check_index,
                    "lower_bound" : lb,
                    "upper_bound" : ub,
                    "best_sat_bandwidth" : best_bw
                })
                break # Gặp UNSAT -> best_bw trước đó là tối ưu

            labels = decode_model(solver.get_model(), n)
            real_bw = max(abs(labels[u] - labels[v]) for u, v in edges)
            best_bw, best_labels = real_bw, labels
            progress({
                "status": "SAT",
                "component": tag,
                "current_bandwidth": target,
                "real_bandwidth": real_bw,
                "check_index": check_index,
                "lower_bound": lb,
                "upper_bound": ub,
                "best_sat_bandwidth": best_bw
            })
            target = real_bw - 1
        return best_bw, best_labels
    finally:
        solver.delete()


def solve(n, edges, progress_path=None):
    adj = make_adjacency(n, edges)
    progress = lambda d: write_progress(progress_path, d)

    labels = {}
    next_label = 1
    total_bw = 0
    lbs, ubs = [], []

    # tách thành phần liên thông, bandwidth(G) = max(bandwidth(C_i))
    for ci, comp in enumerate(sorted(components(n, adj), key = len)):
        nc = len(comp)
        if nc == 1: # Đỉnh cô lập -> gán nhãn nối tiếp, bw = 0
            labels[comp[0]] = next_label
            next_label += 1
            continue

        comp = sorted(comp)
        idx = {v: i+1 for i, v in enumerate(comp)}
        c_edges = [(idx[u], idx[v]) for u, v in edges if u in idx]
        c_adj = make_adjacency(nc, c_edges)

        ub, order0 = upper_bound(nc, c_edges, c_adj)
        lb = lower_bound(nc, c_edges, c_adj)
        lbs.append(lb)
        ubs.append(ub)

        bw, c_labels = solve_connected(nc, c_edges, order0, ub, lb, progress, ci)
        total_bw = max(total_bw, bw)
        for v in comp:
            labels[v] = next_label + c_labels[idx[v]] -1
        next_label += nc

    return {
        "bandwidth" : total_bw,
        "labels" : labels,
        "lower_bound" : max(lbs, default = 0),
        "upper_bound" : max(ubs, default = 0),
    }