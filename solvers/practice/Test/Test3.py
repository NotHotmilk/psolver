import solvers.puzzles.common_rules as common_rules

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, stringify_grid_frame_with_array2D
from cspuz.generator import generate_problem, ArrayBuilder2D, count_non_default_values


def solve(height, width, problem_tuple):
    solver = Solver()

    problem, blocks = problem_tuple

    count = 0
    for b in blocks:
        for y in range(len(b)):
            for x in range(len(b[0])):
                if b[y][x] == 1:
                    count += 1
    for y in range(height):
        for x in range(width):
            if problem[y][x] == 1:
                count += 1
    if (height * width - count) % 2 == 1:
        return False, None, None


    grid_frame = graph.BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(grid_frame)

    kind = solver.int_array((height, width), 0, len(blocks) + 1)
    solver.add_answer_key(kind)

    common_rules.place_polyomino(solver, kind, height, width, blocks, True, True)

    u = kind[:-1, :]
    d = kind[1:, :]
    l = kind[:, :-1]
    r = kind[:, 1:]

    def ban(f):
        return (f == 0) | (f == len(blocks) + 1)

    solver.ensure((u == d) | ban(u) | ban(d))
    solver.ensure((l == r) | ban(l) | ban(r))

    for y in range(height):
        for x in range(width):
            if problem[y][x] == 1:
                solver.ensure(kind[y, x] == len(blocks) + 1)
            else:
                solver.ensure(kind[y, x] != len(blocks) + 1)

    is_passed = graph.active_edges_single_cycle(solver, grid_frame)
    solver.ensure(is_passed == (kind == 0))

    is_sat = solver.solve()

    return is_sat, kind, grid_frame


if __name__ == '__main__':
    _ = 0
    problem = [
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _],
    ]
    height = len(problem)
    width = len(problem[0])

    m = [[1]]
    m4 = [[1, 1], [1, 1]]
    m9 = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    blocks = [m, m, m4, m4, m9, m9]

    is_sat, kind, grid_frame = solve(height, width, (problem, blocks))
    if is_sat:
        print(stringify_array(kind, common_rules.NUM_MAP))
        print(stringify_grid_frame(grid_frame))
    else:
        print('no solution')

