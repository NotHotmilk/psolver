from cspuz import Solver, graph
from cspuz.constraints import fold_or, fold_and, then, count_true
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.array import BoolArray2D


# 2*2禁
def not_forming_2by2_square(solver: Solver, is_black: BoolArray2D):
    solver.ensure(~(
            is_black[:-1, :-1] & is_black[:-1, 1:] & is_black[1:, :-1] & is_black[1:, 1:]
    ))


# 全部の列・行にある黒マスの数が等しい
def equal_black_cells_in_each_row_and_column(solver: Solver, is_black: BoolArray2D, height: int, width: int,
                                             counts=None):
    if counts is None:
        same_count = solver.int_var(0, max(height, width))
        solver.add_answer_key(same_count)
    else:
        same_count = counts

    for y in range(height):
        solver.ensure(count_true(is_black[y]) == same_count)
    for x in range(width):
        solver.ensure(count_true(is_black[:, x]) == same_count)
    return same_count


# 数字の周囲８マスに黒マスがちょうどその数だけある マインスイーパーの制約 数字は白マス
def minesweeper_like_around_number(solver: Solver, is_black: BoolArray2D, problem, height, width):
    for y in range(height):
        for x in range(width):
            if problem[y][x] != -1:
                solver.ensure(is_black[y, x] == False)
                solver.ensure(count_true(
                    is_black[max(0, y - 1):min(y + 2, height), max(0, x - 1):min(x + 2, width)]
                ) == problem[y][x])


# 数字の周囲４マスに黒マスがちょうどその数だけある クリークの制約
def creek_like_around_number(solver: Solver, is_black: BoolArray2D, problem, height, width):
    for y in range(height + 1):
        for x in range(width + 1):
            if problem[y][x] != -1:
                solver.ensure(
                    count_true(
                        is_black[max(0, y - 1):min(y + 1, height), max(0, x - 1):min(x + 1, width)]
                    )
                    == problem[y][x])


# すべての黒マスのブロックが同じ面積
def all_black_blocks_have_same_area(solver: Solver, is_black: BoolArray2D, height: int, width: int, area: int):
    group_id, group_size = graph.connected_groups(solver, is_black)
    for y in range(height):
        for x in range(width):
            solver.ensure(then(is_black[y, x], group_size[y, x] == area))


# すべての黒マスのブロックが２マス
def all_black_blocks_have_same_area_2(solver: Solver, is_black: BoolArray2D, problem, height: int, width: int):
    for y in range(height):
        for x in range(width):
            solver.ensure(then(is_black[y, x], count_true(
                is_black[max(0, y - 1):min(y + 2, height), x],
                is_black[y, max(0, x - 1):min(x + 2, width)]
            ) == 3))
