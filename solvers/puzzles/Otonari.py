import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then, alldifferent
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
from collections import defaultdict, Counter
from cspuz.problem_serializer import Rooms, serialize_problem_as_url, deserialize_problem_as_url
import common_rules

LITS_COMBINATOR = Rooms()


def deserialize_lits(url):
    return deserialize_problem_as_url(LITS_COMBINATOR, url, return_size=True)


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


def solve_otonari(link, key):
    height, width, problem = deserialize_lits(link)
    adjacent_groups = find_adjacent_for_groups(height, width, problem)
    num_groups = len(problem)

    solver = Solver()
    numbers = solver.int_array((height, width), 1, num_groups)
    solver.add_answer_key(numbers)

    solver.ensure(numbers[0, 0] == 1)
    solver.ensure(numbers[height - 1, width - 1] == num_groups)

    solver.ensure(alldifferent([numbers[group[0]] for group in problem]))

    for i in range(num_groups):
        group = problem[i]
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
        result = stringify_array(numbers, common_rules.NUM_MAP_MANY)
        print(result)
    else:
        print("no solution")

    return


if __name__ == "__main__":
    link = "https://puzz.link/p?lits/10/10/94lbvvvvfuvvvvql4i7svv7sfumdfu7svv7s"
    key = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 50, 0, 0, 42, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 23, 0, 0, 10, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]


    solve_otonari(link, key)
