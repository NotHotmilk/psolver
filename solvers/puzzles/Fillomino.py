import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.puzzle import util
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D


def solve_fillomino(height, width, problem, checkered=False):
    solver = Solver()
    size = solver.int_array((height, width), 1, height * width)
    solver.add_answer_key(size)
    border = graph.BoolInnerGridFrame(solver, height, width)
    graph.division_connected_variable_groups_with_borders(
        solver, group_size=size, is_border=border
    )
    solver.ensure(border.vertical == (size[:, :-1] != size[:, 1:]))
    solver.ensure(border.horizontal == (size[:-1, :] != size[1:, :]))
    for y in range(height):
        for x in range(width):
            if problem[y][x] >= 1:
                solver.ensure(size[y, x] == problem[y][x])
    if checkered:
        color = solver.bool_array((height, width))
        solver.ensure(border.vertical == (color[:, :-1] != color[:, 1:]))
        solver.ensure(border.horizontal == (color[:-1, :] != color[1:, :]))
    is_sat = solver.solve()
    return is_sat, size


def generate_fillomino(
    height, width, checkered=False, disallow_adjacent=False, symmetry=False, verbose=False
):
    generated = generate_problem(
        lambda problem: solve_fillomino(height, width, problem, checkered=checkered),
        builder_pattern=ArrayBuilder2D(
            height,
            width,
            range(0, 9),
            default=0,
            disallow_adjacent=disallow_adjacent,
            symmetry=symmetry,
        ),
        clue_penalty=lambda problem: count_non_default_values(problem, default=0, weight=5),
        verbose=verbose,
    )
    return generated

import common_rules


if __name__ == "__main__":
    # height = 8
    # width = 8
    problem = [
        [0, 0, 4, 0, 0, 4],
        [1, 0, 0, 0, 0, 3],
        [0, 0, 0, 3, 0, 0],
        [0, 0, 2, 0, 0, 0],
        [3, 0, 0, 0, 0, 3],
        [4, 0, 0, 4, 0, 1],

    ]
    height = len(problem)
    width = len(problem[0])
    is_sat, answer = solve_fillomino(height, width, problem)
    if is_sat:
        print(util.stringify_array(answer, common_rules.NUM_MAP))
    else:
        print("no answer")