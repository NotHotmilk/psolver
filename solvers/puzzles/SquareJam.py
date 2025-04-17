import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array


def solve(problem: list[list[int]], torus: bool = False):
    height, width = len(problem), len(problem[0])

    solver = Solver()

    border = graph.BoolGridFrame(solver, height, width)
    solver.add_answer_key(border)

    to_up = solver.int_array((height, width), 0, height - 1)
    to_down = solver.int_array((height, width), 0, height - 1)
    to_left = solver.int_array((height, width), 0, width - 1)
    to_right = solver.int_array((height, width), 0, width - 1)

    if not torus:
        solver.ensure(border.vertical[:, 0])
        solver.ensure(border.vertical[:, -1])
        solver.ensure(border.horizontal[0, :])
        solver.ensure(border.horizontal[-1, :])

        solver.ensure(to_up[0, :] == 0)
        solver.ensure(to_up[1:, :] == border.horizontal[1:-1, :].cond(0, to_up[:-1, :] + 1))
        solver.ensure(to_down[-1, :] == 0)
        solver.ensure(to_down[:-1, :] == border.horizontal[1:-1, :].cond(0, to_down[1:, :] + 1))
        solver.ensure(to_left[:, 0] == 0)
        solver.ensure(to_left[:, 1:] == border.vertical[:, 1:-1].cond(0, to_left[:, :-1] + 1))
        solver.ensure(to_right[:, -1] == 0)
        solver.ensure(to_right[:, :-1] == border.vertical[:, 1:-1].cond(0, to_right[:, 1:] + 1))

    else:
        solver.ensure(border.vertical[:, 0] == border.vertical[:, -1])
        solver.ensure(border.horizontal[0, :] == border.horizontal[-1, :])

        solver.ensure(to_up[1:, :] == border.horizontal[1:-1, :].cond(0, to_up[:-1, :] + 1))
        solver.ensure(to_down[:-1, :] == border.horizontal[1:-1, :].cond(0, to_down[1:, :] + 1))
        solver.ensure(to_left[:, 1:] == border.vertical[:, 1:-1].cond(0, to_left[:, :-1] + 1))
        solver.ensure(to_right[:, :-1] == border.vertical[:, 1:-1].cond(0, to_right[:, 1:] + 1))

        solver.ensure(to_up[0, :] == border.horizontal[0, :].cond(0, to_up[-1, :] + 1))
        solver.ensure(to_down[-1, :] == border.horizontal[0, :].cond(0, to_down[0, :] + 1))
        solver.ensure(to_left[:, 0] == border.vertical[:, 0].cond(0, to_left[:, -1] + 1))
        solver.ensure(to_right[:, -1] == border.vertical[:, 0].cond(0, to_right[:, 0] + 1))

    for y in range(height - 1):
        for x in range(width - 1):
            u, d, l, r = border.vertex_neighbors(y + 1, x + 1)
            solver.ensure(~fold_and(u, d, l, r))
            solver.ensure(~((u ^ d) & (l ^ r)))
            solver.ensure(count_true(u, d, l, r) != 1)

    if torus:
        for y in range(height - 1):
            u = border.vertical[y, 0]
            d = border.vertical[y + 1, 0]
            l = border.horizontal[y + 1, -1]
            r = border.horizontal[y + 1, 0]
            solver.ensure(~fold_and(u, d, l, r))
            solver.ensure(~((u ^ d) & (l ^ r)))
        for x in range(width - 1):
            u = border.vertical[-1, x + 1]
            d = border.vertical[0, x + 1]
            l = border.horizontal[0, x]
            r = border.horizontal[0, x + 1]
            solver.ensure(~fold_and(u, d, l, r))
            solver.ensure(~((u ^ d) & (l ^ r)))
        uu = border.vertical[-1, -1]
        dd = border.vertical[0, 0]
        ll = border.horizontal[-1, -1]
        rr = border.horizontal[0, 0]
        solver.ensure(~fold_and(uu, dd, ll, rr))
        solver.ensure(~((uu ^ dd) & (ll ^ rr)))

    for y in range(height):
        for x in range(width):
            solver.ensure((to_up[y, x] + to_down[y, x]) == (to_left[y, x] + to_right[y, x]))
            if problem[y][x] != -1:
                solver.ensure((to_up[y, x] + to_down[y, x] == problem[y][x] - 1))
                solver.ensure((to_left[y, x] + to_right[y, x] == problem[y][x] - 1))

    is_sat = solver.solve()
    return is_sat, border


if __name__ == "__main__":
    _ = -1
    problem = [
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _],

    ]
    is_sat, border = solve(problem, torus=True)
    print(is_sat)
    print(stringify_grid_frame(border))
