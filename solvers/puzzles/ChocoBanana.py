import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_choco(height: int, width: int, problem: list[list[int]]):
    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    is_border = graph.BoolInnerGridFrame(solver, (height, width))
    solver.ensure(is_border.vertical == (is_black[:, :-1] != is_black[:, 1:]))
    solver.ensure(is_border.horizontal == (is_black[:-1, :] != is_black[1:, :]))

    sizes = []
    for y in range(height):
        for x in range(width):
            if problem[y][x] != -1:
                sizes.append(solver.int(problem[y][x], problem[y][x], name=f'sizes[{y},{x}]'))
