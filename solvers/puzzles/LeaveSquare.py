import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


# blocks: 3次元int配列
def solve_leave_square(height: int, width: int, blocks: list[list[list[int]]], setting: int = 0):
    solver = Solver()
    kind = solver.int_array((height, width), 0, len(blocks))
    has_block = solver.bool_array((height, width))
    solver.add_answer_key(kind)

    common_rules.place_polyomino(solver, kind, height, width, blocks)

    # # 正方形の条件
    solver.ensure((kind == 0) == (~has_block))

    to_up = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_up[0, :] == 0)
    solver.ensure(to_up[1:, :] == has_block[:-1, :].cond(0, to_up[:-1, :] + 1))

    to_down = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_down[-1, :] == 0)
    solver.ensure(to_down[:-1, :] == has_block[1:, :].cond(0, to_down[1:, :] + 1))

    to_left = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_left[:, 0] == 0)
    solver.ensure(to_left[:, 1:] == has_block[:, :-1].cond(0, to_left[:, :-1] + 1))

    to_right = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_right[:, -1] == 0)
    solver.ensure(to_right[:, :-1] == has_block[:, 1:].cond(0, to_right[:, 1:] + 1))

    for y in range(height):
        for x in range(width):
            solver.ensure((kind[y, x] == 0).then(to_up[y, x] + to_down[y, x] == to_left[y, x] + to_right[y, x]))

    # 補助. 長方形条件
    for y in range(height - 1):
        for x in range(width - 1):
            solver.ensure(count_true(kind[y:y + 2, x:x + 2] == 0) != 3)

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
            k = deepcopy(kind)
            count += 1
            print(C.BG_BLACK + C.BOLD + str(count) + "." + C.RESET)
            print(stringify_array(kind, common_rules.NUM_MAP))
            solver.ensure(~fold_and(kind[y, x] == k[y, x].sol for y in range(height) for x in range(width)))
            print()
            is_sat = solver.find_answer()

        return is_sat, kind


if __name__ == "__main__":

    P1 = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P2 = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P3 = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P4 = [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P5 = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P6 = [
        [0, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P7 = [
        [0, 0, 1, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P8 = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P9 = [
        [0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P10 = [
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    P11 = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]

    # solve(0) or enumerate(1)
    setting = 1

    from common_rules import Pentomino as P

    height, width = 7, 7
    blocks = [
        P1, P2, P3, P4, P7, P9
    ]

    is_sat, answer = solve_leave_square(height, width, blocks, setting)




    if setting == 0:
        if is_sat:
            print("sat")
            # print(stringify_array(answer, lambda x: "?" if x is None else str(x)))
            print(stringify_array(answer, common_rules.NUM_MAP))

        else:
            print("no answer")

    else:
        if is_sat:
            print("sat")
        else:
            print("探索終了")
