import csv
import json
from datetime import datetime
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from time import perf_counter

from graph import read_graph
from solver import solve
from check_result import decode_model, check_result


TIMEOUT = 300  # giới hạn mỗi testcase 300s


def solve_worker(n, edges, queue):
    try:
        result = solve(n, edges)
        queue.put(("OK", result))
    except Exception as e:
        queue.put(("ERROR", f"{type(e).__name__}: {e}"))


def solve_with_timeout(n, edges, timeout=TIMEOUT):
    queue = Queue()
    process = Process(
        target=solve_worker,
        args=(n, edges, queue)
    )

    started = False
    deadline = perf_counter() + timeout

    try:
        process.start()
        started = True

        while True:
            remaining = deadline - perf_counter()

            if remaining <= 0:
                return "TIMEOUT", None

            try:
                return queue.get(timeout=min(0.1, remaining))

            except Empty:
                if not process.is_alive():
                    return (
                        "ERROR",
                        f"Tien trinh dung ma khong tra ket qua "
                        f"(exitcode={process.exitcode})"
                    )

    finally:
        if started:
            process.join(timeout=0.2)

            if process.is_alive():
                process.terminate()
                process.join(timeout=1)

            if process.is_alive():
                process.kill()
                process.join()

            process.close()

        queue.close()
        queue.join_thread()


def main():
    base_dir = Path(__file__).resolve().parent
    testcase_dir = base_dir / "testcase"

    files = sorted(testcase_dir.glob("*.mtx"))

    if not files:
        print("Khong tim thay file .mtx trong:", testcase_dir)
        return

    # Mỗi lần chạy tạo môt mục kết quả riêng
    run_name = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = base_dir / "results" / run_name
    labels_dir = output_dir / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "summary.csv"

    columns = [
        "test",
        "n",
        "m",
        "status",
        "bandwidth",
        "time_seconds",
        "validation",
        "message",
    ]

    counts = {
        "OK": 0,
        "TIMEOUT": 0,
        "INVALID": 0,
        "ERROR": 0,
    }

    print(f"Tim thay {len(files)} testcase.")
    print("Ket qua luu tai:", output_dir)

    with summary_path.open(
            "w", newline="", encoding="utf-8-sig"
    ) as summary_file:
        writer = csv.DictWriter(summary_file, fieldnames=columns)
        writer.writeheader()
        summary_file.flush()

        for index, filename in enumerate(files, start=1):
            print(
                f"[{index}/{len(files)}] Dang chay: {filename.name}",
                flush=True
            )

            start_time = perf_counter()

            row = {
                "test": filename.name,
                "n": "",
                "m": "",
                "status": "ERROR",
                "bandwidth": "",
                "time_seconds": "",
                "validation": "NOT_CHECKED",
                "message": "",
            }

            try:
                # 1. đọc đồ thị
                n, m, edges = read_graph(filename)
                row["n"] = n
                row["m"] = m

                # 2. giải với timeout cho toàn bộ hàm solve
                status, result = solve_with_timeout(
                    n, edges, timeout=TIMEOUT
                )

                if status == "TIMEOUT":
                    row["status"] = "TIMEOUT"
                    row["message"] = f"Vuot {TIMEOUT} giay"

                elif status == "ERROR":
                    row["status"] = "ERROR"
                    row["message"] = result

                else:
                    p, model = result

                    if p is None or model is None:
                        raise ValueError("Solver khong tra ve nghiem")

                    row["bandwidth"] = p

                    # 3. giải mã model
                    try:
                        labels = decode_model(model, n)
                    except ValueError as e:
                        row["status"] = "INVALID"
                        row["validation"] = "INVALID"
                        row["message"] = str(e)

                    else:
                        # 4. kiểm tra nghiệm
                        valid = check_result(n, edges, labels, p)

                        row["validation"] = (
                            "VALID" if valid else "INVALID"
                        )
                        row["status"] = "OK" if valid else "INVALID"

                        if not valid:
                            row["message"] = (
                                "Gan nhan khong hop le hoac "
                                "bandwidth khong khop"
                            )

                        # 5. lưu cách gãn nhãn
                        label_path = labels_dir / (
                                filename.stem + ".json"
                        )

                        with label_path.open(
                                "w", encoding="utf-8"
                        ) as label_file:
                            json.dump(
                                {
                                    "test": filename.name,
                                    "bandwidth": p,
                                    "validation": row["validation"],
                                    "labels": labels,
                                },
                                label_file,
                                ensure_ascii=False,
                                indent=2,
                            )

            except Exception as e:
                row["status"] = "ERROR"
                row["message"] = f"{type(e).__name__}: {e}"

            row["time_seconds"] = round(
                perf_counter() - start_time, 3
            )

            # 6. ghi kết quả của testcase vừa chạy
            writer.writerow(row)
            summary_file.flush()

            counts[row["status"]] += 1

            print(
                f"  {row['status']} | "
                f"bandwidth={row['bandwidth']} | "
                f"{row['validation']} | "
                f"{row['time_seconds']} giay",
                flush=True
            )

            if row["message"]:
                print(" ", row["message"], flush=True)

    print("\nDa chay xong.")
    for status, count in counts.items():
        print(f"{status}: {count}")

    print("Bang ket qua:", summary_path)


if __name__ == "__main__":
    main()