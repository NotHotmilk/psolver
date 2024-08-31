import copy

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

EMPTY = 0
STAR = 1
BLACKHOLE = 2


def edit_problem(problem, height, width):
    # pos = [
    #     (7, 2), (7, 3), (7, 4),
    #     (8, 2), (8, 4),
    #     (9, 2), (9, 3), (9, 4),
    #
    #     (6, 6), (6, 7), (6, 8), (6, 9),
    #     (7, 6), (7, 9),
    #     (8, 6), (8, 9),
    #     (9, 6), (9, 7), (9, 8), (9, 9),
    # ]
    #
    # pos2 = [
    #     (8, 3),
    #     (7, 7), (7, 8),
    #     (8, 7), (8, 8),
    # ]
    #
    # for y, x in pos:
    #     problem[y - 1][x] = STAR
    #
    # for y, x in pos2:
    #     problem[y - 1][x] = EMPTY

    return problem


def solve_blackholes(height: int, width: int, problem: list[list[int]]):
    solver = Solver()
    kind = solver.int_array((height, width), 0, 2)
    solver.add_answer_key(kind)

    problem = edit_problem(problem, height, width)

    # 問題の条件を追加
    for y in range(height):
        for x in range(width):
            solver.ensure((kind[y, x] == STAR) == (problem[y][x] == STAR))

    # どのマスの周囲９マスにもBLACKHOLEが１つ以下
    for y in range(height):
        for x in range(width):
            cells = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if 0 <= y + dy < height and 0 <= x + dx < width:
                        cells.append(kind[y + dy, x + dx] == BLACKHOLE)
            solver.ensure(count_true(cells) <= 1)

    # STARの周りにはBLACKHOLEが１つ
    for y in range(height):
        for x in range(width):
            if problem[y][x] == STAR:
                cells = []
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if 0 <= y + dy < height and 0 <= x + dx < width:
                            cells.append(kind[y + dy, x + dx] == BLACKHOLE)
                solver.ensure(count_true(cells) == 1)

    is_sat = solver.solve()

    return is_sat, kind


def generate_blackholes(height: int, width: int, verbose=False):
    def pretest(problem):
        for y in range(height):
            if problem[y][0] != 0 or problem[y][-1] != 0:
                return False
        for x in range(width):
            if problem[0][x] != 0 or problem[-1][x] != 0:
                return False

        return True

    def compute_score(kind: cspuz.solver.IntArray2D):
        score = 0

        for y in range(height):
            for x in range(width):
                if kind[y, x].sol is not None:
                    score += 1

        if kind[8, 3].sol == STAR:
            score -= 100

        return score

    generated = generate_problem(lambda problem: solve_blackholes(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [EMPTY, STAR], default=EMPTY),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=EMPTY,
                                                                                       weight=4),
                                 verbose=verbose,
                                 pretest=pretest,
                                 score=compute_score,
                                 )
    return generated


def generatehxw(height, width):
    print("Generating")

    problem = generate_blackholes(height, width, verbose=True)

    is_sat, kind = solve_blackholes(height, width, problem)
    print(stringify_array(kind, {0: " ", 1: "X", 2: "@", None: "?"}))


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(generatehxw_wrapper, range(8))
    return results


def generatehxw_wrapper(i):
    return generatehxw(12, 12)


if __name__ == "__main__":
    problem = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
        [0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0],
        [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    height = len(problem)
    width = len(problem[0])

    # height = 12
    # width = 12
    # problem = generate_blackholes(height, width, verbose=True)
    #

    from colorize import Color as cc

    is_sat, kind = solve_blackholes(height, width, problem)
    # print(stringify_array(kind, {0: ".", 1: "X", 2: "@", None: "?"}))
    print(is_sat)
    print(stringify_array(kind, {0: cc.WHITE + "." + cc.RESET, 1: "X", 2: cc.RED + '@' + cc.RESET, None: "?"}))

    # count1 = []
    # for y in range(height):
    #     for x in range(width):
    #         if problem[y][x] == 1:
    #             count1.append((y, x))
    #
    # for y, x in count1:
    #     p = copy.deepcopy(problem)
    #     p[y][x] = 0
    #     is_sat, kind = solve_blackholes(height, width, p)
    #     print(stringify_array(kind, {0: " ", 1: "X", 2: "@", None: "?"}))
    #

    #
    #
    # results = parallel_generatehxw()
    # for result in results:
    #     print(result)
