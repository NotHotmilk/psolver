import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


# blocks: 3次元int配列
def solve_kabemimi(height: int, width: int, problem: list[list[bool]], blocks: list[list[list[int]]], setting: int = 0):
    from time import time
    start = time()

    solver = Solver()
    kind = solver.int_array((height, width), 0, len(blocks))
    solver.add_answer_key(kind)

    common_rules.place_polyomino(solver, kind, height, width, blocks, True, True)

    for y in range(height):
        for x in range(width):
            if problem[y][x] == 1:
                solver.ensure(kind[y, x] != 0)
            elif problem[y][x] == 2:
                solver.ensure(kind[y, x] == 0)

    # for y in range(height):
    #     for x in range(width):
    #         if x < width - 1:
    #             solver.ensure(
    #                 (kind[y, x] == kind[y, x + 1]) | ((kind[y, x] == 0) | (kind[y, x + 1] == 0))
    #             )
    #         if y < height - 1:
    #             solver.ensure(
    #                 (kind[y, x] == kind[y + 1, x]) | ((kind[y, x] == 0) | (kind[y + 1, x] == 0))
    #             )

    # モード
    if setting == 0:
        is_sat = solver.solve()
        return is_sat, kind

    else:
        from copy import deepcopy
        from colorize import Color as C

        count = 0
        is_sat = solver.find_answer()
        while is_sat:
            # if count >= 16:
            #     print("16個を超えて解が存在します。探索を終了します。")
            #     break

            k = deepcopy(kind)
            count += 1
            print(C.BG_BLACK + C.BOLD + str(count) + "." + C.RESET + " "
                  + C.WHITE + str(round(time() - start, 2)) + "s" + C.RESET)
            print(stringify_array(kind, common_rules.NUM_MAP))
            solver.ensure(~fold_and(kind[y, x] == k[y, x].sol for y in range(height) for x in range(width)))
            print()
            is_sat = solver.find_answer()

        return is_sat, kind


from common_rules import Pentomino as P
from common_rules import Tetromino as T
import random

if __name__ == "__main__":
    # solve(0) or enumerate(1)
    setting = 1

    problem = [
        [1, 1, 0, 1, 1, 0, 0],
        [0, 2, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 1, 1, 1, 0],
        [0, 0, 2, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0],
    ]

    height, width = len(problem), len(problem[0])

    print(stringify_array(problem, common_rules.BW_MAP) + "\n")

    blocks = T.ALL
    # blocks = []
    # for i in range(6):
    #     blocks.append(P.ALL[random.randint(0, 11)])

    is_sat, answer = solve_kabemimi(height, width, problem, blocks, setting)

if setting == 0:
    if is_sat:
        print("sat")
        print(stringify_array(answer, common_rules.NUM_MAP))

    else:
        print("no answer")

else:
    print("探索終了")
