import json

from pysat.solvers import Cadical300

from encoding import build_static_encoding, add_bandwidth_bound
from bounds import lower_bound, upper_bound
from check_result import decode_model


def write_progress(path, data):
    if path is None:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def solve(n, edges, progress_path=None):

    lb = lower_bound(n, edges)
    ub = upper_bound(n, edges)

    solver = Cadical300()

    try:
        _, _, static_clauses = build_static_encoding(
            n,
            solver
        )

        best_bandwidth = None
        best_model = None

        target = ub
        check_index = 0

        while target >=lb:
            check_index += 1

            write_progress(
                progress_path,
                {
                    "status": "SOLVING",
                    "current_bandwidth": target,
                    "check_index": check_index,
                    "lower_bound": lb,
                    "upper_bound": ub,
                    "best_sat_bandwidth": best_bandwidth
                }
            )

            add_bandwidth_bound(
                n,
                edges,
                target,
                solver
            )

            sat = solver.solve()

            if sat:
                model = solver.get_model()
                labels = decode_model(model, n)
                # Tính bandwidth thực tế của nghiệm
                real_bw = max(
                    (
                        abs(labels[u] - labels[v])
                        for u, v in edges
                    ),
                    default = 0
                )

                if real_bw > target:
                    raise RuntimeError(
                        "Nghiem SAT khong thoa man bandwidth target"
                    )

                best_bandwidth = real_bw
                best_model = model

                write_progress(
                    progress_path,
                    {
                        "status": "SAT",
                        "current_bandwidth": target,
                        "real_bandwidth" : real_bw,
                        "check_index": check_index,
                        "lower_bound": lb,
                        "upper_bound": ub,
                        "best_sat_bandwidth": best_bandwidth
                    }
                )
                target = real_bw - 1

            else:
                write_progress(
                    progress_path,
                    {
                        "status": "UNSAT",
                        "current_bandwidth": target,
                        "check_index": check_index,
                        "lower_bound": lb,
                        "upper_bound": ub,
                        "best_sat_bandwidth": best_bandwidth
                    }
                )
                break

        if best_bandwidth is None:
            raise RuntimeError(
                "Khong tim thay nghiem SAT trong"
                "pham vi lower bound va upper bound"
            )

        return {
            "bandwidth": best_bandwidth,
            "model": best_model,
            "lower_bound": lb,
            "upper_bound": ub,
            "static_clauses": static_clauses,
        }

    finally:
        solver.delete()