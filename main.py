from multiprocessing import Process, Queue
from queue import Empty

from graph import read_graph
from solver import solve


def solve_worker(n, edges, queue):
    try:
        result = solve(n, edges)
        queue.put(("OK", result))
    except Exception as e:
        queue.put(("ERROR", str(e)))


def solve_with_timeout(n, edges, timeout=300):
    queue = Queue()

    process = Process(
        target=solve_worker,
        args=(n, edges, queue)
    )

    process.start()

    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()

        return "TIMEOUT"

    try:
        status, result = queue.get_nowait()
    except Empty:
        return "ERROR"

    if status == "ERROR":
        print("Solver error:", result)
        return "ERROR"

    return result


def main():
    filename = "dataset/test1.txt"

    n, m, edges = read_graph(filename)

    result = solve_with_timeout(n, edges, timeout=300)

    if result == "TIMEOUT":
        print("TIMEOUT")

    elif result == "ERROR":
        print("ERROR")

    elif result is None:
        print("No result")

    else:
        p, model = result

        print("Bandwidth:", p)
        print("Model:", model)


if __name__ == "__main__":
    main()