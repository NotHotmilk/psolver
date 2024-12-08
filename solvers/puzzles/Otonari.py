import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then, alldifferent
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
from collections import defaultdict, Counter


def group_by_symbols(height, width, problem):
    # 文字ごとに座標をグループ化するための辞書
    groups = defaultdict(list)

    # 各マスを走査して座標をグループに追加
    for y in range(height):
        for x in range(width):
            symbol = problem[y][x]
            groups[symbol].append((y, x))

    # 結果をリストとして返す
    return list(groups.values())


def get_adjacent_positions(y, x, width, height):
    # 上下左右の座標をリストにして返す。ただし盤面外は除外。
    adjacent = []
    if y > 0:
        adjacent.append((y - 1, x))  # 上
    if y < height - 1:
        adjacent.append((y + 1, x))  # 下
    if x > 0:
        adjacent.append((y, x - 1))  # 左
    if x < width - 1:
        adjacent.append((y, x + 1))  # 右
    return adjacent


def find_adjacent_for_groups(height, width, groups):
    # 結果を格納する辞書 (グループ -> 隣接する座標リスト)
    adjacent_positions = {}

    for group in groups:
        adjacent_set = set()  # 重複を避けるためセットを使用
        for (y, x) in group:
            # 4方向の隣接座標を取得
            adj_positions = get_adjacent_positions(y, x, width, height)
            for pos in adj_positions:
                # 隣接座標が現在のグループに含まれていない場合のみ追加
                if pos not in group:
                    adjacent_set.add(pos)
        adjacent_positions[tuple(group)] = list(adjacent_set)  # グループをキーとして保存
    return adjacent_positions


def solve_otonari(height, width, problem, key):
    groups = group_by_symbols(height, width, problem)
    adjacent_groups = find_adjacent_for_groups(height, width, groups)
    num_groups = len(groups)

    solver = Solver()
    numbers = solver.int_array((height, width), 1, num_groups)
    solver.add_answer_key(numbers)

    solver.ensure(numbers[0, 0] == 1)
    solver.ensure(numbers[height - 1, width - 1] == num_groups)

    solver.ensure(alldifferent([numbers[group[0]] for group in groups]))

    for i in range(num_groups):
        group = groups[i]
        num_of_this_group = numbers[group[0]]
        adjacent = adjacent_groups[tuple(group)]
        solver.ensure(fold_and([numbers[y, x] == num_of_this_group for y, x in group]))

        solver.ensure(
            (num_of_this_group == num_groups) |
            (count_true([numbers[y, x] == num_of_this_group + 1 for y, x in adjacent]) >= 1))
        solver.ensure(
            (num_of_this_group == 1) |
            (count_true([numbers[y, x] == num_of_this_group - 1 for y, x in adjacent]) >= 1))

    # 問題の制約を追加
    for y in range(height):
        for x in range(width):
            if key[y][x] != 0:
                solver.ensure(numbers[y, x] == key[y][x])

    # # 高速化
    # for y in range(height - 1):
    #     solver.ensure(numbers[y, 0] <= numbers[y + 1, 0])
    #     solver.ensure(numbers[y, width - 1] <= numbers[y + 1, width - 1])
    #
    # for x in range(width - 1):
    #     solver.ensure(numbers[0, x] <= numbers[0, x + 1])
    #     solver.ensure(numbers[height - 1, x] <= numbers[height - 1, x + 1])


    is_sat = solver.solve()
    if is_sat:
        result = stringify_array(numbers, lambda x: "???" if x is None else f"{x:>3}")
        print(result)
    else:
        print("no solution")

    return


if __name__ == "__main__":

    A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z = range(501, 501 + 26)

    width = 15
    height = 15

    problem = [
        [10000 + y * 100 + x for x in range(width)] for y in range(height)
    ]

    problem2 = [
        [101, 101, 102, 102, 103, 103, 104, 104, 104, 105, 105, 106, 106, 107, 107],
        [101, 108, 108, 109, 109, 110, 110, 100, 111, 111, 112, 112, 113, 113, 107],
        [114, 108, 108, 115, 116, 116, 117, 117, 117, 118, 118, 119, 113, 113, 120],
        [114, 121, 115, 115, 115, 122, 122, 123, 124, 124, 119, 119, 119, 125, 120],
        [126, 121, 127, 115, 100, 100, 100, 123, 100, 100, 100, 119, 128, 125, 129],
        [126, 130, 127, 131, 100, 100, 100, 123, 100, 100, 100, 132, 128, 133, 129],
        [134, 130, 135, 131, 100, 100, 100, 136, 100, 100, 100, 132, 137, 133, 138],
        [134, 100, 135, 139, 139, 139, 136, 136, 136, 140, 140, 140, 137, 100, 138],
        [134, 230, 135, 231, 100, 100, 100, 136, 100, 100, 100, 232, 137, 233, 138],
        [226, 230, 227, 231, 100, 100, 100, 223, 100, 100, 100, 232, 228, 233, 229],
        [226, 221, 227, 215, 100, 100, 100, 223, 100, 100, 100, 219, 228, 225, 229],
        [214, 221, 215, 215, 215, 222, 222, 223, 224, 224, 219, 219, 219, 225, 220],
        [214, 208, 208, 215, 216, 216, 217, 217, 217, 218, 218, 219, 213, 213, 220],
        [201, 208, 208, 209, 209, 210, 210, 100, 211, 211, 212, 212, 213, 213, 207],
        [201, 201, 202, 202, 203, 203, 204, 204, 204, 205, 205, 206, 206, 207, 207],

    ]
    key  = [
        [0, 0, 0, 0, 0, 85, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 101, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 97],
        [0, 0, 0, 0, 0, 0, 0, 62, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 71, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0],
        [34, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 29, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 46, 0, 0, 0, 0, 0],

    ]

    for y in range(height):
        for x in range(width):
            if problem2[y][x] != 0 and problem2[y][x] != 100:
                problem[y][x] = problem2[y][x]


    solve_otonari(height, width, problem, key)
