import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


# blocks: 3次元int配列
def solve_blocks(height: int, width: int, blocks: list[list[list[int]]], setting: int = 0):
    solver = Solver()
    kind = solver.int_array((height, width), 0, len(blocks))
    has_block = solver.bool_array((height, width))
    solver.add_answer_key(kind)

    # ポリオミノの条件
    for i in range(len(blocks)):
        block = blocks[i]
        # 0のみの行を削除
        block = [row for row in block if any(row)]
        # 0のみの列を削除
        block = list(map(list, zip(*[col for col in zip(*block) if any(col)])))

        b_height = len(block)
        b_width = len(block[0])

        i = i + 1

        conditions = []
        for y in range(height - b_height + 1):
            for x in range(width - b_width + 1):

                b = [[0] * width for _ in range(height)]
                for yy in range(b_height):
                    for xx in range(b_width):
                        if block[yy][xx] == 1:
                            b[y + yy][x + xx] = 1
                # iのマスとbのマスが一致するか

                conditions.append(
                    fold_and((kind[Y, X] == i) == (b[Y][X] == 1) for Y in range(height) for X in range(width)))

        solver.ensure(count_true(conditions) == 1)

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
    #
    # # solve(0) or enumerate(1)
    # setting = 1
    #
    # height, width = 5, 5
    # blocks = [
    #     [
    #         [1, 0],
    #         [1, 1],
    #     ],
    #     [
    #         [1, 1, 1],
    #         [0, 1, 0],
    #     ],
    #     [
    #         [1, 1, 1],
    #         [1, 0, 1],
    #         [1, 0, 1],
    #     ],
    #     [
    #         [1, 1, 1]
    #     ],
    #     [
    #         [0, 1],
    #         [1, 1],
    #         [1, 0],
    #     ]
    # ]

    # solve(0) or enumerate(1)
    setting = 1

    height, width = 5, 3
    blocks = [
        [
            [0, 0, 1],
            [0, 0, 1],
            [1, 1, 1],
        ],
        [
            [1, 1, 1],
        ],
        [
            [1, 1],
        ],

    ]

    is_sat, answer = solve_blocks(height, width, blocks, setting)

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
            print("no answer")
