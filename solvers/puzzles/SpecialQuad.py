import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D

from cspuz.puzzle import akari, nurimisaki, shakashaka
import TransformMatrix


# problem について、 -1は白、0は数字なし、1は0~3の数字に変わる

def solve_quad_puzzle(height, width, problem):
    problems = [
        [[-2] * width for _ in range(height)] for _ in range(4)
    ]

    for i in range(4):
        for j in range(height):
            for k in range(width):
                if problem[j][k] == -1:
                    problems[i][j][k] = -2
                elif problem[j][k] == 0:
                    problems[i][j][k] = -1
                elif problem[j][k] != -1:
                    problems[i][j][k] = i

    # 結合する -> (height*2 + 3) * (width*2 + 3) のマスになる
    final_problem = [[-2] * (width * 2 + 3) for _ in range(height * 2 + 3)]
    for y in range(2):
        for x in range(2):
            for i in range(height):
                for j in range(width):
                    final_problem[y * (height + 1) + i + 1][x * (width + 1) + j + 1] = problems[y * 2 + x][i][j]

    final_problem = TransformMatrix.transform_matrix_with_fixed_edges(final_problem, height)

    #
    # print()
    # for l in final_problem:
    #     print(l)

    is_sat, answer = akari.solve_akari(height * 2 + 3, width * 2 + 3, final_problem)
    return is_sat, answer


def to_link(height, width, problem):
    for y in range(height):
        for x in range(width):
            if problem[y][x] == -1:
                problem[y][x] = '_'
            if problem[y][x] == 0:
                problem[y][x] = '.'
            if problem[y][x] == 1:
                problem[y][x] = '?'

    final_problem = [['_'] * (width * 2 + 3) for _ in range(height * 2 + 3)]

    for y in range(2):
        for x in range(2):
            for i in range(height):
                for j in range(width):
                    final_problem[y * (height + 1) + i + 1][x * (width + 1) + j + 1] = problem[i][j] if problem[i][
                                                                                                            j] != '?' else y * 2 + x

    final_problem = TransformMatrix.transform_matrix_with_fixed_edges(final_problem, height)

    final_link = ""

    for i in range(height * 2 + 3):
        final_link += "".join(map(str, final_problem[i]))

    link = 'https://semiexp.net/pzprrt/p?lightup_edit/{}/{}/{}'.format(width * 2 + 3, height * 2 + 3, final_link)
    print(link)
    return


def generate_quad_puzzle(height, width, verbose=False, symmetry=False):
    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] != -1:
                    ret += 1
                    if problem[y][x] == 1:
                        ret += 1
        return ret

    generated = generate_problem(lambda problem: solve_quad_puzzle(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [-1, 0, 1], default=-1,
                                                                symmetry=symmetry,
                                                                disallow_adjacent=True#[(-1, -1), (-1, 1), (1, -1), (1, 1)]
                                                                ),
                                 clue_penalty=penalty,
                                 # score=compute_score,
                                 verbose=verbose,
                                 # pretest=pretest,
                                 initial_temperature=15.0,
                                 temperature_decay=0.995,
                                 )

    to_link(height, width, generated)

    return generated


import multiprocessing


def generatehxw(height, width):
    print("Generating")
    problem = generate_quad_puzzle(height, width, verbose=False, symmetry=False)

    for l in problem:
        print(l)


def parallel_generatehxw():
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(generatehxw_wrapper, range(8))
    return results


def generatehxw_wrapper(i):
    return generatehxw(2, 2)


if __name__ == '__main__':

    results = parallel_generatehxw()
    for result in results:
        print(result)
