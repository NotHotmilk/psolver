import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_original(height, width, problem):
    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    common_rules.creek_like_around_number(solver, is_black, problem, height, width)
    common_rules.not_forming_2by2_square(solver, ~is_black)
    graph.active_vertices_connected(solver, ~is_black)
    # common_rules.black_cells_form_rectangle(solver, ~is_black, height, width)

    has_answer = solver.solve()
    return has_answer, is_black


def generate_original(height, width, symmetry=False, verbose=False):
    # def compute_score(ans):
    #     score = 0
    #     sol = [[ans[y, x].sol for x in range(width)] for y in range(height)]
    #
    #     for v in sol:
    #         if v is not None:
    #             score += 1
    #
    #     for y in range(height - 1):
    #         for x in range(width - 1):
    #             if all(sol[y + dy][x + dx] != -1 for dy, dx in [(0, 0), (1, 0), (0, 1), (1, 1)]):
    #                 if sol[y][x] != sol[y + 1][x] and sol[y][x] != sol[y][x + 1] and sol[y][x] == sol[y + 1][x + 1]:
    #                     score += 5
    #
    #     return score

    generated = generate_problem(lambda problem: solve_original(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height + 1, width + 1, [-1, 0, 1, 2, 3, 4], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=10),
                                 # score=compute_score,
                                 verbose=verbose)
    return generated


def generatehxw(height, width):
    print("Generating")
    problem = generate_original(height, width, symmetry=False, verbose=True)
    print(stringify_array(problem, str))
    link = 'https://puzz.link/p?creek/{}/{}/{}'.format(width, height, encode_array(
        list(map(lambda row: list(map(lambda x: '_' if x == -1 else x, row)), problem))
    ))
    print(link)
    print(stringify_array(solve_original(height, width, problem)[1], {True: '#', False: '.', None: '?'}))
    return link


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=2) as pool:
        results = pool.map(generatehxw_wrapper, range(2))
    return results


def generatehxw_wrapper(_):
    return generatehxw(10, 10)


if __name__ == "__main__":
    results = parallel_generatehxw()
    print("Result")
    for result in results:
        print(result)
