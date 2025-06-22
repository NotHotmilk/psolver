import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.generator import generate_problem, ArrayBuilder2D, count_non_default_values
import common_rules

def solve(v_keys_p: list[list[int]], h_keys_p: list[list[int]]):
    if len(v_keys_p) != len(h_keys_p):
        raise ValueError("The number of vertical keys must match the number of horizontal keys.")
    
    N = len(v_keys_p)
   

    solver = Solver()
    
    v_keys = solver.int_array((N, 3), 0, 9)
    h_keys = solver.int_array((N, 3), 0, 9)
    
    num = solver.int_array((N, N), -1, 9)
    solver.add_answer_key(num, v_keys, h_keys)
    
    for n in range(N):
        for k in range(3):
            if v_keys_p[n][k] != -1:
                solver.ensure(v_keys[n, k] == v_keys_p[n][k])
            if h_keys_p[n][k] != -1:
                solver.ensure(h_keys[n, k] == h_keys_p[n][k])

    
    for n in range(N):
        solver.ensure(count_true(num[n, :] != -1) == 3)
        solver.ensure(count_true(num[:, n] != -1) == 3)

    for x in range(N):
        rank = solver.int_array(N, 0, 3)
        for y in range(N):
            if y == 0:
                solver.ensure(rank[y] == (num[y, x] == -1).cond(0, 1))
            else:
                solver.ensure(rank[y] == (num[y, x] == -1).cond(rank[y - 1], rank[y - 1] + 1))

            solver.ensure(((rank[y] == 1) & (num[y, x] != -1)).then(num[y, x] == v_keys[x][0]))
            solver.ensure(((rank[y] == 2) & (num[y, x] != -1)).then(num[y, x] == v_keys[x][1]))
            solver.ensure(((rank[y] == 3) & (num[y, x] != -1)).then(num[y, x] == v_keys[x][2]))

    for y in range(N):
        rank = solver.int_array(N, 0, 3)
        for x in range(N):
            if x == 0:
                solver.ensure(rank[x] == (num[y, x] == -1).cond(0, 1))
            else:
                solver.ensure(rank[x] == (num[y, x] == -1).cond(rank[x - 1], rank[x - 1] + 1))

            solver.ensure(((rank[x] == 1) & (num[y, x] != -1)).then(num[y, x] == h_keys[y][0]))
            solver.ensure(((rank[x] == 2) & (num[y, x] != -1)).then(num[y, x] == h_keys[y][1]))
            solver.ensure(((rank[x] == 3) & (num[y, x] != -1)).then(num[y, x] == h_keys[y][2]))

    is_sat = solver.solve()
    return is_sat, num, v_keys, h_keys


if __name__ == "__main__":
    # Example usage
    v_keys = [
        [3, 4, 4],
        [1, 2, 3],
        [1, 2, 2],
        [2, 3, 4],
        [3, 2, 1],
        [3, 4, 3],
    ]
    h_keys = [
        [1, 2, 3],
        [3, 2, 3],
        [2, 3, -1],
        [4, 3, -1],
        [2, 4, -1],
        [4, 2, -1],
    ]
    is_sat, num, v_keys, h_keys = solve(v_keys, h_keys)
    if is_sat:
        print("Solution found:")
        print(stringify_array(num, common_rules.NUM_MAP))
    else:
        print("No solution exists.")
