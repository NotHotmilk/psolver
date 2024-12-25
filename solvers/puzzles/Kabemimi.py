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

    common_rules.place_polyomino(solver, kind, height, width, blocks, True)

    for y in range(height):
        for x in range(width):
            if problem[y][x]:
                solver.ensure(kind[y, x] != 0)

    # モード
    if setting == 0:
        is_sat = solver.solve()
        return is_sat, kind

    elif setting == 1:
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
            print(C.BG_BLACK + C.BOLD + str(count) + "." + C.RESET + " " + str(round(time() - start, 2)) + "s")
            print(stringify_array(kind, common_rules.NUM_MAP))
            solver.ensure(~fold_and(kind[y, x] == k[y, x].sol for y in range(height) for x in range(width)))
            print()
            is_sat = solver.find_answer()

        return is_sat, kind

    elif setting == 2:
        is_sat = solver.solve()

        for y in range(height):
            for x in range(width):
                if kind[y, x].sol is None:
                    return False, None

        return is_sat, kind


if __name__ == "__main__":
    # solve(0) or enumerate(1) or unique(2)
    setting = 1

    problem = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    ]

    height, width = len(problem), len(problem[0])

    from common_rules import Pentomino as P
    from common_rules import Tetromino as T

    blocks = [
        [
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
        ],
        [
            [0, 0, 1, 1, 1],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1],
            [0, 0, 1, 1, 1],
        ],
        [
            [1, 1, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 1, 1],
        ],
        [
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 1, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 1, 1],
        ],
        [
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
        ],

    ]

    print(stringify_array(problem, common_rules.BW_MAP) + "\n")

    is_sat, answer = solve_kabemimi(height, width, problem, blocks, setting)

    if setting == 0:
        if is_sat:
            print("sat")
            print(stringify_array(answer, common_rules.NUM_MAP))

        else:
            print("no answer")

    else:
        print("探索終了")
