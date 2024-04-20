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

    common_rules.all_black_blocks_have_same_area_2(solver, is_black, problem, height, width)
    common_rules.minesweeper_like_around_number(solver, is_black, problem, height, width)
    common_rules.not_forming_2by2_square(solver, ~is_black)

    has_answer = solver.solve()
    return has_answer, is_black


def generate_original(height, width, symmetry=False, verbose=False):
    generated = generate_problem(lambda problem: solve_original(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [-1, 0, 1, 2, 3, 4, 5], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=10),
                                 verbose=verbose)
    return generated



def generatehxw(height, width):
    print("Generating")
    problem = generate_original(height, width, symmetry=False, verbose=True)
    print(stringify_array(problem, str))
    link = 'https://puzz.link/p?nurikabe/{}/{}/{}'.format(width, height, encode_array(
        list(map(lambda row: list(map(lambda x: '_' if x == -1 else x, row)), problem))
    ))
    print(link)
    print(stringify_array(solve_original(height, width, problem)[1], {True: '#', False: '.', None: '?'}))
    return link

import multiprocessing

def parallel_generatehxw():
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(generatehxw_wrapper, range(4))
    return results


def generatehxw_wrapper(_):
    return generatehxw(4, 4)


if __name__ == "__main__":
    results = parallel_generatehxw()
    print("Result")
    for result in results:
        print(result)