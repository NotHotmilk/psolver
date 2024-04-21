import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_ostil(height, width, problem):
    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    common_rules.all_black_blocks_have_same_area(solver, is_black, height, width, 4)
    common_rules.creek_like_around_number(solver, is_black, problem, height, width)
    common_rules.not_forming_2by2_square(solver, ~is_black)

    has_answer = solver.solve()
    return has_answer, is_black


def generate_ostil(height, width, symmetry=False, verbose=False):
    def penalty(problem):
        ret = 0
        least_count = 0
        for y in range(height + 1):
            for x in range(width + 1):
                if problem[y][x] == 4:
                    ret += 20
                    least_count += 1
                elif problem[y][x] == 3:
                    ret += 4
                    least_count += 1
                elif problem[y][x] != -1:
                    ret += 10
                    least_count += 1

        # ret += max(0, min(height, width) - least_count) * 250
        # 
        # import max_rectangle
        # max_area, (h, w) = max_rectangle.max_rectangle_area_with_dimensions(
        #     [[1 if problem[y][x] == -1 else 0 for x in range(width + 1)] for y in range(height + 1)])
        # ret -= max_area * min(h, w) * 4

        return ret

    generated = generate_problem(lambda problem: solve_ostil(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height + 1, width + 1, [-1, 0, 1, 2, 3, 4], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=penalty,
                                 # lambda problem: count_non_default_values(problem, default=-1, weight=10),
                                 verbose=verbose)
    return generated


def generatehxw(height, width):
    print("Generating")
    problem = generate_ostil(height, width, symmetry=False, verbose=True)
    print(stringify_array(problem, str))
    link = 'https://puzz.link/p?creek/{}/{}/{}'.format(width, height, encode_array(
        list(map(lambda row: list(map(lambda x: '_' if x == -1 else x, row)), problem))
    ))
    print(link)
    print(stringify_array(solve_ostil(height, width, problem)[1], {True: '#', False: '.', None: '?'}))
    return link


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(generatehxw_wrapper, range(8))
    return results


def generatehxw_wrapper(_):
    return generatehxw(8, 8)


if __name__ == "__main__":
    results = parallel_generatehxw()
    print("Result")
    for result in results:
        print(result)
