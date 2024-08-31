import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

from cspuz.puzzle import akari


def solve_quad_akari(height, width, problem):
    problems = []
    for i in range(4):
        p = [[-2 for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if problem[y][x] == -2:  # empty
                    p[y][x] = -2
                elif problem[y][x] == -1:  # black
                    p[y][x] = -1
                else:  # number
                    p[y][x] = i
        problems.append(p)

    is_sat = True
    answers = []

    for i in range(4):
        sat, ans = akari.solve_akari(height, width, problems[i])
        is_sat = is_sat and sat
        answers.append(ans)

    return is_sat, *answers


def generate_quad_akari(height, width, verbose=False, symmetry=False):
    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] == -1:
                    ret += 12
                elif problem[y][x] != -2:
                    ret += 10
        return ret

    def compute_score(*answers):
        score = 0

        for y in range(height):
            for x in range(width):
                for ans in answers:
                    if ans[y, x].sol is not None:
                        score += 1
                # if all(ans[y, x].sol is not None for ans in answers):
                #     score += 6

        return score

    generated = generate_problem(lambda problem: solve_quad_akari(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [-2, -1, 0], default=-2,
                                                                symmetry=symmetry,
                                                                # disallow_adjacent=[(-1, -1), (-1, 0), (-1, 1),
                                                                #                    (0, -1), (0, 1),
                                                                #                    (1, -1), (1, 0), (1, 1)]
                                                                # disallow_adjacent=[(-1, -1), (-1, 1), (1, -1), (1, 1)]
                                                                ),
                                 clue_penalty=penalty,
                                 score=compute_score,
                                 verbose=verbose,
                                 # pretest=pretest,
                                 initial_temperature=20.0,
                                 temperature_decay=0.995,

                                 )

    return generated


import multiprocessing


def generatehxw(height, width):
    print("Generating")
    problem = generate_quad_akari(height, width,verbose=False)

    for y in range(height):
        print(problem[y])

    for y in range(height):
        for x in range(width):
            if problem[y][x] == -1:
                problem[y][x] = '.'
            if problem[y][x] == -2:
                problem[y][x] = '_'
            if problem[y][x] == 0:
                problem[y][x] = '?'

    final_problem = [['.'] * (width * 2 + 3) for _ in range(height * 2 + 3)]
    final_problem[-1][-1] = '4'

    for i in range(2):
        for j in range(2):
            for y in range(height):
                for x in range(width):
                    final_problem[y + i * (height + 1) + 1][x + j * (width + 1) + 1] = problem[y][x] if problem[y][
                                                                                                            x] != '?' else i + j * 2

    final_link = ""

    for i in range(height * 2 + 3):
        final_link += "".join(map(str, final_problem[i]))

    link = 'https://puzz.link/p?lightup_edit/{}/{}/{}'.format(width * 2 + 3, height * 2 + 3, final_link)
    print(link)


def parallel_generatehxw():
    with multiprocessing.Pool(processes=12) as pool:
        results = pool.map(generatehxw_wrapper, range(12))
    return results


def generatehxw_wrapper(i):
    return generatehxw(8, 8)


if __name__ == '__main__':

    results = parallel_generatehxw()
    for result in results:
        print(result)
