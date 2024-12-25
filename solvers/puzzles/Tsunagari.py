import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_tsunagari(height, width, problem):
    size = [int(1 / 2 * i * (i + 1)) for i in range(30)]
    # 0 1 3 6 10 15 21 28 36 45 55 66 78 91 105 120 136 153 171 190 210 231 253 276
    size_index = size.index(int(height * width))
    print(f"numbers: 1-{size_index}")

    solver = Solver()
    number = solver.int_array((height, width), 1, size_index)
    solver.add_answer_key(number)

    for y in range(height):
        for x in range(width):
            if problem[y][x] != 0:
                solver.ensure(number[y, x] == problem[y][x])

    for i in range(size_index):
        solver.ensure(count_true(number == i + 1) == i + 1)
        graph.active_vertices_connected(solver, number == i + 1)

    is_sat = solver.solve()
    return is_sat, number


if __name__ == "__main__":
    problem = [
        [0, 0, 0, 0, 0, 0, 7, 0, 0],
        [0, 0, 7, 0, 8, 0, 0, 0, 0],
        [0, 2, 0, 9, 0, 9, 4, 0, 0],
        [6, 0, 3, 0, 8, 0, 0, 0, 4],
        [0, 1, 0, 0, 0, 0, 0, 0, 0],
    ]

    is_sat, answer = solve_tsunagari(len(problem), len(problem[0]), problem)

    if is_sat:
        print(stringify_array(answer, common_rules.NUM_MAP))
    else:
        print("no solution")