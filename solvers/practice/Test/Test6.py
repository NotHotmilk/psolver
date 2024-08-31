import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true
from cspuz.puzzle import util
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D


def solve_onetwothree(problem):
    solver = Solver()
    num = solver.int_array((6, 6), 1, 3)
    solver.add_answer_key(num)

    for y in range(6):
        for x in range(6):
            if problem[y][x] != 0:
                solver.ensure(num[y, x] == problem[y][x])

    # 1. Each row and column contains exactly one 1, two 2s, and three 3s.
    # 2. Each 6-cell region contains exactly one 1, two 2s, and three 3s.

    for i in range(6):
        solver.ensure(count_true(num[i, :] == 1) == 1)
        solver.ensure(count_true(num[i, :] == 2) == 2)
        solver.ensure(count_true(num[i, :] == 3) == 3)
        solver.ensure(count_true(num[:, i] == 1) == 1)
        solver.ensure(count_true(num[:, i] == 2) == 2)
        solver.ensure(count_true(num[:, i] == 3) == 3)

    for y in range(3):
        for x in range(2):
            region = num[y * 2:y * 2 + 2, x * 3:x * 3 + 3]
            solver.ensure(count_true(region == 1) == 1)
            solver.ensure(count_true(region == 2) == 2)
            solver.ensure(count_true(region == 3) == 3)

    is_sat = solver.solve()
    return is_sat, num


def generate_onetwothree(verbose=False, symmetry=False):
    generated = generate_problem(lambda problem: solve_onetwothree(problem),
                                 builder_pattern=ArrayBuilder2D(6, 6, [0, 1, 2, 3], default=0, symmetry=symmetry),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=0,
                                                                                       weight=7),
                                 verbose=verbose,

                                 )
    return generated


if __name__ == '__main__':
    # problem = [
    #     [1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 3, 0, 3],
    #     [0, 0, 3, 0, 2, 0],
    #     [0, 0, 0, 0, 2, 0],
    #     [0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0],
    # ]

    problem = generate_onetwothree(verbose=True)

    is_sat, answer = solve_onetwothree(problem)

    print(util.stringify_array(problem, lambda x: "_" if x is 0 else str(x)))

    print("has answer:", is_sat)
    print(util.stringify_array(answer, lambda x: "?" if x is None else str(x)))
