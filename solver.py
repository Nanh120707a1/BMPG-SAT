import json

from pysat.solvers import Cadical195

from encoding import build_static_encoding, add_bandwidth_bound
from bounds import lower_bound, upper_bound


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

    solver = Cadical195()

    try:
        _, _, static_clauses = build_static_encoding(
            n,
            solver
        )

        best_bandwidth = None
        best_model = None

        for check_index, bandwidth in enumerate(
                range(ub, lb - 1, -1),
                start=1
        ):
            write_progress(
                progress_path,
                {
                    "status": "SOLVING",
                    "current_bandwidth": bandwidth,
                    "check_index": check_index,
                    "lower_bound": lb,
                "upper_bound": ub,
                "best_sat_bandwidth": best_bandwidth
                }
            )

            add_bandwidth_bound(
                n,
                edges,
                bandwidth,
                solver
            )

            sat = solver.solve()

            if sat:
                best_bandwidth = bandwidth
                best_model = solver.get_model()

                write_progress(
                progress_path,
                {
                    "status": "SAT",
                    "current_bandwidth": bandwidth,
                    "check_index": check_index,
                    "lower_bound": lb,
                    "upper_bound": ub,
                    "best_sat_bandwidth": best_bandwidth
                }
            )

            else:
                write_progress(
                    progress_path,
                    {
                        "status": "UNSAT",
                        "current_bandwidth": bandwidth,
                        "check_index": check_index,
                        "lower_bound": lb,
                        "upper_bound": ub,
                        "best_sat_bandwidth": best_bandwidth
                    }
                )

                break

        if best_bandwidth is None:
            raise RuntimeError(
                "Upper bound khong SAT."
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