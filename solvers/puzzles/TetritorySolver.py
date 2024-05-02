import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_tetritory(height: int, width: int, problem: list[list[int]], y_key: list[int], x_key: list[int],
                    output_board: bool = False):


    solver = Solver()

    block_number = solver.int_array((height, width), 0, height * width // 4 - 1)

    # 軽量化
    solver.ensure(block_number[0, 0] == 0)
    solver.ensure(block_number[height - 1, width - 1] == height * width // 4 - 1)
    if height >= 5 and width >= 5:
        solver.ensure(block_number[0, width - 1] == 1)
        solver.ensure(block_number[height - 1, 0] == height * width // 4 - 2)
        solver.ensure(block_number[(height + 1) // 2, (width + 1) // 2] == 2)

    is_base = solver.bool_array((height, width))
    border = graph.BoolInnerGridFrame(solver, height, width)
    graph.division_connected_variable_groups_with_borders(solver, group_size=solver.int_array((height, width), 4, 4),
                                                          is_border=border)
    solver.add_answer_key(border.vertical, border.horizontal)
    solver.add_answer_key(is_base)

    # 盤面の数字の条件
    for y in range(height + 1):
        for x in range(width + 1):
            if problem[y][x] != 0:
                borders = []
                # up
                if (0 < x < width) and (0 < y):
                    borders.append(border.vertical[y - 1, x - 1])
                # down
                if (0 < x < width) and (y < height):
                    borders.append(border.vertical[y, x - 1])
                # left
                if (0 < y < height) and (0 < x):
                    borders.append(border.horizontal[y - 1, x - 1])
                # right
                if (0 < y < height) and (x < width):
                    borders.append(border.horizontal[y - 1, x])

                if problem[y][x] == 1:
                    solver.ensure(count_true(borders) == 0)
                elif problem[y][x] == 2:
                    if (x == 0) or (x == width) or (y == 0) or (y == height):
                        solver.ensure(count_true(borders) == 1)
                    else:
                        solver.ensure(count_true(borders) == 2)
                else:
                    solver.ensure(count_true(borders) == problem[y][x])

    # キーの条件
    for y in range(height):
        if y_key[y] >= 0:
            solver.ensure(count_true(is_base[y, :]) == y_key[y])
    for x in range(width):
        if x_key[x] >= 0:
            solver.ensure(count_true(is_base[:, x]) == x_key[x])

    # block_numberが異なるときに限ってはborderが存在
    solver.ensure(border.vertical == (block_number[:, :-1] != block_number[:, 1:]))
    solver.ensure(border.horizontal == (block_number[:-1, :] != block_number[1:, :]))

    # それぞれのテトロミノには1つのbaseが存在
    for i in range(height * width // 4):
        solver.ensure(count_true((block_number == i) & (is_base)) == 1)

    # baseは隣り合わない
    graph.active_vertices_not_adjacent(solver, is_base)

    # 表示用
    if (output_board):
        new_grid_frame = graph.BoolGridFrame(solver, height, width)
        for y in range(height - 1):
            for x in range(width):
                solver.ensure(new_grid_frame.horizontal[y + 1, x] == border.horizontal[y, x])

        for y in range(height):
            for x in range(width - 1):
                solver.ensure(new_grid_frame.vertical[y, x + 1] == border.vertical[y, x])

        solver.ensure(new_grid_frame.vertical[:, 0] == True)
        solver.ensure(new_grid_frame.vertical[:, -1] == True)
        solver.ensure(new_grid_frame.horizontal[0, :] == True)
        solver.ensure(new_grid_frame.horizontal[-1, :] == True)

        solver.add_answer_key(new_grid_frame)

    has_answer = solver.solve()

    if (output_board):
        grid = stringify_grid_frame(new_grid_frame)
        base = stringify_array(is_base, {True: '#', False: '.', None: '?'})
        print(grid)
        print(base)

    return has_answer, (border, is_base)


if __name__ == "__main__":
    # height = 6
    # width = 6
    # problem = (
    #     [-1, -1, 3, 3, -1, -1],
    #     [-1, -1, -1, -1, -1, -1],
    #     [
    #         [0, 0, 0, 0, 0, 0, 0],
    #         [0, 3, 0, 0, 4, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0],
    #         [0, 1, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 2, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0],
    #
    #     ]
    # )

    # height = 6
    # width = 6
    # problem = (
    #     [3, -1, 1, 2, -1, 0],
    #     [1, -1, 1, -1, 1, -1],
    #     [
    #         [0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0],
    #         [0, 2, 2, 0, 0, 4, 0],
    #         [0, 2, 0, 4, 0, 0, 0],
    #         [0, 2, 2, 2, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0],
    #     ]
    # )

    height = 6
    width = 6

    y_key = [0, 0, -1, -1, -1, 1]
    x_key = [-1, 0, -1, -1, -1, 1]

    problem = [
        [0, 0, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
    ]

    import time

    start_time = time.time()
    is_sat = solve_tetritory(height, width, problem, y_key, x_key, output_board=True)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(is_sat)
    print(round(elapsed_time, 4), "s")
