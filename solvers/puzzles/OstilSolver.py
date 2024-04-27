import math
import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


# def solve_ostil(height, width, problem):
#     solver = Solver()
#     is_black = solver.bool_array((height, width))
#     solver.add_answer_key(is_black)
#
#     common_rules.all_black_blocks_have_same_area(solver, is_black, height, width, 4)
#     common_rules.creek_like_around_number(solver, is_black, problem, height, width)
#     common_rules.not_forming_2by2_square(solver, ~is_black)
#
#     has_answer = solver.solve()
#     return has_answer, is_black


def solve_ostil_2(height, width, problem):
    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)
    border = graph.BoolInnerGridFrame(solver, height, width)
    common_rules.creek_like_around_number(solver, is_black, problem, height, width)
    common_rules.not_forming_2by2_square(solver, ~is_black)

    size = solver.int_array((height, width), 1, height * width)
    solver.ensure(border.vertical == (is_black[:, :-1] != is_black[:, 1:]))
    solver.ensure(border.horizontal == (is_black[:-1, :] != is_black[1:, :]))
    graph.division_connected_variable_groups_with_borders(solver, group_size=size, is_border=border)

    for y in range(height):
        for x in range(width):
            solver.ensure(is_black[y, x].then(size[y, x] == 4))

    has_answer = solver.solve()
    return has_answer, is_black


def generate_ostil(height, width, symmetry=False, verbose=False):
    def penalty(problem):
        ret = 0
        for y in range(height + 1):
            for x in range(width + 1):
                if problem[y][x] == 4:
                    ret += 100
                elif problem[y][x] != -1:
                    ret += 10

        import max_rectangle
        max_area, (h, w) = max_rectangle.max_rectangle_area_with_dimensions(
            [[1 if problem[y][x] == -1 else 0 for x in range(width + 1)] for y in range(height + 1)])

        area_score = max_area // 1.5
        # print(f"{max_area}/{ret} -> {area_score}, final penalty -> {ret - area_score}")
        ret -= area_score
        ret = max(ret, 0)

        return ret

    def compute_score(ans: graph.BoolArray2D):
        score = 0
        for a in ans:
            if a.sol is not None:
                score += 1

        return score

    generated = generate_problem(lambda problem: solve_ostil_2(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height + 1, width + 1, [-1, 0, 1, 2, 3, 4], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=penalty,
                                 # lambda problem: count_non_default_values(problem, default=-1, weight=10),
                                 score=compute_score,
                                 verbose=verbose)
    return generated


def generatehxw(height, width):
    print("Generating")
    problem = generate_ostil(height, width, symmetry=False, verbose=True)
    print(cspuz.puzzle.util.encode_array(problem, empty=-1))
    print(stringify_array(problem, str))
    link = 'https://puzz.link/p?creek/{}/{}/{}'.format(width, height, encode_array(problem, empty=-1))
    print(link)
    print(stringify_array(solve_ostil_2(height, width, problem)[1], {True: '#', False: '.', None: '?'}))
    return link


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(generatehxw_wrapper, range(4))
    return results


def generatehxw_wrapper(_):
    return generatehxw(6, 6)


if __name__ == "__main__":
    results = parallel_generatehxw()
    print("Result")
    for result in results:
        print(result)

    # p = (8, 8,
    #                       [
    #                           [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    #                           [-1, -1, -1, -1,  3, -1, -1, -1,  1],
    #                           [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    #                           [-1,  2, -1,  3, -1,  3,  3, -1, -1],
    #                           [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    #                           [-1,  3,  1, -1,  3,  2, -1, -1,  1],
    #                           [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    #                           [-1, -1, -1,  1, -1,  1, -1, -1, -1],
    #                           [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    #                       ])
    # ans1 = solve_ostil(*p)
    # print("Answer1")
    # print(ans1[0])
    # print(stringify_array(ans1[1], {True: '#', False: '.', None: '?'}))
    # print("Answer1")
