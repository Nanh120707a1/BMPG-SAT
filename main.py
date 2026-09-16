from graph import read_graph
from solver import solve
from check_result import decode_model, check_result

def main():
    filename = "dataset/test1.txt"

    n, m, edges = read_graph(filename)

    bandwidth, model = solve(n, edges)

    if bandwidth is None:
        print("No solution")
        return

    labels = decode_model(model, n)

    print("Bandwidth:", bandwidth)
    print("Labels:", labels)

    if check_result(n, edges, labels, bandwidth):
        print("Result: VALID")
    else:
        print("Result: INVALID")


if __name__ == "__main__":
    main()