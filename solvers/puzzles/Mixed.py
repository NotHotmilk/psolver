import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

from cspuz.puzzle import akari, nurimisaki, shakashaka
import Shugaku, Koburin


def solve_mixed_puzzle(height, width, problem):
    akari_problem = [[0] * width for _ in range(height)]
    nuri_problem = [[0] * width for _ in range(height)]
    shaka_problem = [[0] * width for _ in range(height)]
    shugaku_problem = [[0] * width for _ in range(height)]
    koburin_problem = [[0] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if problem[y][x] == -2:  # ヒントなし
                akari_problem[y][x] = -2
                nuri_problem[y][x] = -1
                shaka_problem[y][x] = None
                shugaku_problem[y][x] = -1
                koburin_problem[y][x] = -1
            elif problem[y][x] == -1:  # 黒マス・柱・数字なし
                akari_problem[y][x] = -1
                nuri_problem[y][x] = 0
                shaka_problem[y][x] = -1
                shugaku_problem[y][x] = 5
                koburin_problem[y][x] = 5
            else:
                p = problem[y][x]
                akari_problem[y][x] = p
                nuri_problem[y][x] = p
                shaka_problem[y][x] = p
                shugaku_problem[y][x] = p
                koburin_problem[y][x] = p


    is_sat_akari, is_sat_nurimisaki, is_sat_shakashaka, is_sat_shugaku, is_sat_koburin = True, True, True, True, True

    is_sat_akari, has_light = akari.solve_akari(height, width, akari_problem)
    #is_sat_nurimisaki, is_white = nurimisaki.solve_nurimisaki(height, width, nuri_problem)
    is_sat_shakashaka, answer = shakashaka.solve_shakashaka(height, width, shaka_problem)
    is_sat_shugaku, kind, direction = Shugaku.solve_shugaku(height, width, shugaku_problem)
    is_sat_koburin, grid_frame, black_cell = Koburin.solve_koburin(height, width, koburin_problem)

    is_sat = is_sat_akari and  is_sat_nurimisaki and is_sat_shakashaka and is_sat_shugaku and is_sat_koburin

    return is_sat, has_light, answer, kind, direction, grid_frame, black_cell


def generate_mixed_puzzle(height, width, verbose=False, symmetry=False):
    def penalty(problem):
        ret = 0
        # for y in range(height):
        #     for x in range(width):
        #         if problem[y][x] == -1:
        #             ret += 2
        #         elif problem[y][x] != -2:
        #             ret += 2
        return ret

    def compute_score(*answers):
        score = 0

        for y in range(height):
            for x in range(width):
                for ans in answers:
                    if ans[y, x].sol is not None:
                        score += 1

        # if score == height * width * 4:
        #     print("Full score")

        return score

    generated = generate_problem(lambda problem: solve_mixed_puzzle(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [-2, -1, 0, 1, 2, 3, 4], default=-2,
                                                                symmetry=symmetry,
                                                                #disallow_adjacent=True
                                                                ),
                                 clue_penalty=penalty,
                                 # score=compute_score,
                                 verbose=verbose,
                                 # pretest=pretest,
                                 initial_temperature=15.0,
                                 temperature_decay=0.995,

                                 )

    return generated


import multiprocessing


def generatehxw(height, width):
    print("Generating")
    problem = generate_mixed_puzzle(height, width, verbose=True)

    for y in range(height):
        print(problem[y])


def parallel_generatehxw():
    with multiprocessing.Pool(processes=12) as pool:
        results = pool.map(generatehxw_wrapper, range(12))
    return results


def generatehxw_wrapper(i):
    return generatehxw(7, 7)


if __name__ == '__main__':

    results = parallel_generatehxw()
    for result in results:
        print(result)
