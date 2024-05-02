import math

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_majikiri(height, width, problem):
    solver = Solver()

    is_black = solver.bool_array((height * 2 + 1, width * 2 + 1))
    solver.add_answer_key(is_black)

    for y in range(height):
        for x in range(width):
            solver.ensure(~is_black[y * 2 + 1, x * 2 + 1])

    solver.ensure(is_black[:, 0], is_black[:, -1], is_black[0, :], is_black[-1, :])
    for y in range(height - 1):
        for x in range(width - 1):
            solver.ensure(is_black[y * 2 + 2, x * 2 + 2])

    #graph.active_vertices_connected(solver, is_black)
    graph.active_vertices_connected(solver, ~is_black)

    # 視界の制約
    to_up = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_up[0, :] == 0)
    for y in range(1, height):
        for x in range(width):
            solver.ensure(
                to_up[y, x] == is_black[y * 2, x * 2 + 1].cond(0, to_up[y - 1, x] + 1)
            )

    to_down = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_down[-1, :] == 0)
    for y in range(height - 2, -1, -1):
        for x in range(width):
            solver.ensure(
                to_down[y, x] == is_black[y * 2 + 2, x * 2 + 1].cond(0, to_down[y + 1, x] + 1)
            )

    to_left = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_left[:, 0] == 0)
    for y in range(height):
        for x in range(1, width):
            solver.ensure(
                to_left[y, x] == is_black[y * 2 + 1, x * 2].cond(0, to_left[y, x - 1] + 1)
            )

    to_right = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_right[:, -1] == 0)
    for y in range(height):
        for x in range(width - 2, -1, -1):
            solver.ensure(
                to_right[y, x] == is_black[y * 2 + 1, x * 2 + 2].cond(0, to_right[y, x + 1] + 1)
            )

    for y in range(height):
        for x in range(width):
            if problem[y][x] != 0:
                solver.ensure(to_up[y, x] + to_down[y, x] + to_left[y, x] + to_right[y, x] + 1 == problem[y][x])

    has_answer = solver.solve()
    return has_answer, is_black


def generate_majikiri(height, width, symmetry=False, verbose=False):
    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] != 0:
                    ret += 5
                    ret += problem[y][x] * 2
        return ret

    def compute_score(ans: graph.BoolArray2D):
        num_white = height * width
        num_black = 4 * height + 4 * width + (height - 1) * (width - 1)
        score = -(num_white + num_black)
        for a in ans:
            if a.sol is not None:
                score += 1
                # if a.sol:
                #     score += 2

        return score

    generated = generate_problem(lambda problem: solve_majikiri(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [i for i in range(height + width)],
                                                                default=0,
                                                                symmetry=symmetry),
                                 clue_penalty=penalty,
                                 score=compute_score,
                                 verbose=verbose)
    return generated


def generatehxw(height, width):
    print("Generating")
    problem = generate_majikiri(height, width, verbose=True)
    print(cspuz.puzzle.util.encode_array(problem, empty=0))
    print(stringify_array(problem, str))
    link = 'https://puzz.link/p?shikaku/{}/{}/{}'.format(width, height, encode_array(problem, empty=0))
    print(link)
    print(stringify_array(solve_majikiri(height, width, problem)[1], {True: '#', False: '.', None: '?'}))
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
