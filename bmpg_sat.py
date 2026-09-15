from pysat.solvers import Glucose3
import os
def solve_test(filename):
    with open(filename, "r") as f:
        n = int(f.readLine())
        m = int(f.readLine())

        edge = []
        for i in range(m):
            u, v = map(int, f.readline().split())
            edge.append([u,v])

        clauses = []

    def var(i, j):
        return (i-1)*n +j

    def solve():
        l, r, ans = 1, n-1, n-1
        while (l<=r):
            mid = (l+r)//2
            if check(mid):
                r = mid - 1
                ans = mid
            else: l = mid + 1
        return ans

    def check(p):
        # Cạnh(i,j) không thể nhận nhãn a và b nếu |a-b| > p
        clause1 = clauses.copy()
        for i, j in edge:
            for a in range (1, n+1):
                for b in range (1, n+1):
                    if abs(a-b) > p :
                        clause1.append([-var(i,a), -var(j,b)])

        with Glucose3() as solver:
            for clause in clause1:
                solver.add_clause(clause)
            return solver.solve()

    # mỗi đỉnh có ít nhất một nhãn
    for i in range(1, n+1):
        clause = []
        for j in range (1, n+1):
            clause.append(var(i,j))
        clauses.append(clause)

    # mỗi nhãn được dùng nhiều nhất bởi một đỉnh
    for e in range(1, n+1):
        for i in range (1, n):
            for j in range (i+1, n+1):
                clauses.append([-var(i,e) , -var(j, e)])

    return solve()

test_folder = "tests"
for filename in sorted (os.listdir(test_folder)):
    if filename.endswith(".txt"):
        path = os.path.join(test_folder, filename)
        result = solve_test(path)
        print(filename, "->", result)









