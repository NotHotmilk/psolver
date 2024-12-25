from cspuz import Solver, graph
from cspuz.constraints import fold_or, fold_and, then, count_true
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.array import BoolArray2D, IntArray2D

from math import factorial
from colorist import ColorHSL, Effect, Color

BW_MAP = {True: f"{Effect.BOLD}#{Effect.OFF}", False: f"{Color.WHITE}.{Color.OFF}", 2: f"{Color.RED}o{Color.OFF}",
          None: "?"}

NUM_MAP = {None: "."}
upper_limit = 24
cycle = 35
NUM_MAP[0] = f"{ColorHSL(0, 0, 40)}.{ColorHSL.OFF}"
for i in range(1, 31):
    hue = ((i - 1) * 209) % 360  # 137, 97,211
    col = ColorHSL(hue, 50, 50)
    NUM_MAP[i] = f"{Effect.BOLD}{col}{i}{ColorHSL.OFF}{Effect.OFF}"
#
# for key, value in NUM_MAP.items():
#     print(f"{key}: {value}")

NUM_MAP_MANY = {None: "???"}
upper_limit = 120
cycle = 17
for i in range(upper_limit + 1):
    hue = ((i - 1) * cycle) % 360  # 色相を変化させる
    col = ColorHSL(hue, 50, 50)  # 色相(H), 彩度(S), 明度(L)を指定
    NUM_MAP_MANY[i] = f"{Effect.REVERSE}{Effect.BOLD}{col}{i:03d}{ColorHSL.OFF}{Effect.OFF}"  # 色を適用してNUM_MAPに追加


class Tetromino:
    I = [
        [1, 1, 1, 1]
    ]
    O = [
        [1, 1],
        [1, 1],
    ]
    L = [
        [1, 0],
        [1, 0],
        [1, 1],
    ]
    S = [
        [1, 0],
        [1, 1],
        [0, 1],
    ]
    T = [
        [1, 1, 1],
        [0, 1, 0],
    ]
    J = [
        [0, 1],
        [0, 1],
        [1, 1],
    ]
    Z = [
        [0, 1],
        [1, 1],
        [1, 0],
    ]
    ALL = [I, O, L, S, T, J, Z]
    ALL2 = [L, I, T, S, O]


class Pentomino:
    F = [
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0],
    ]
    I = [
        [1, 1, 1, 1, 1],
    ]
    L = [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
    ]
    N = [
        [1, 1, 1, 0],
        [0, 0, 1, 1],
    ]
    P = [
        [1, 1, 1],
        [1, 1, 0],
    ]
    T = [
        [1, 1, 1],
        [0, 1, 0],
        [0, 1, 0],
    ]
    U = [
        [1, 0, 1],
        [1, 1, 1],
    ]
    V = [
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1],
    ]
    W = [
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 1],
    ]
    X = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]
    Y = [
        [1, 1, 1, 1],
        [0, 1, 0, 0],
    ]
    Z = [
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 1],
    ]
    ALL = [F, I, L, N, P, T, U, V, W, X, Y, Z]


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


# # すべての黒マスのブロックが同じ面積
# def all_black_blocks_have_same_area(solver: Solver, is_black: BoolArray2D, height: int, width: int, area: int):
#     group_id, group_size = graph.connected_groups(solver, is_black)
#     for y in range(height):
#         for x in range(width):
#             solver.ensure(then(is_black[y, x], group_size[y, x] == area))


# すべての黒マスのブロックが２マス
def all_black_blocks_have_same_area_2(solver: Solver, is_black: BoolArray2D, problem, height: int, width: int):
    for y in range(height):
        for x in range(width):
            solver.ensure(then(is_black[y, x], count_true(
                is_black[max(0, y - 1):min(y + 2, height), x],
                is_black[y, max(0, x - 1):min(x + 2, width)]
            ) == 3))


# 黒マスが長方形を形成する
# 1 1
# 1 0 のパターンを許さない
def black_cells_form_rectangle(solver: Solver, is_black: BoolArray2D, height: int, width: int):
    for y in range(height - 1):
        for x in range(width - 1):
            solver.ensure(count_true(is_black[y:y + 2, x:x + 2]) != 3)


def rotate_block(block):
    """Blockを90度回転する"""
    return [list(row) for row in zip(*block[::-1])]


def reflect_block(block):
    """Blockを左右反転する"""
    return [row[::-1] for row in block]


def normalize_block(block):
    """0のみの行と列を削除して正規化する"""
    block = [row for row in block if any(row)]
    block = list(map(list, zip(*[col for col in zip(*block) if any(col)])))
    return block


def find_matching_polyominoes(blocks, allow_rotation: bool, allow_reflection: bool):
    normalized_blocks = []
    for block in blocks:
        unique_rotations = set()
        if allow_rotation or allow_reflection:
            for _ in range(4):  # 回転を考慮
                normalized_block = tuple(map(tuple, normalize_block(block)))
                unique_rotations.add(normalized_block)
                block = rotate_block(block)

            if allow_reflection:  # 反転を考慮
                block = reflect_block(block)
                for _ in range(4):
                    normalized_block = tuple(map(tuple, normalize_block(block)))
                    unique_rotations.add(normalized_block)
                    block = rotate_block(block)
        else:
            # 回転や反転を許さない場合は、最初の状態のみを使用
            normalized_block = tuple(map(tuple, normalize_block(block)))
            unique_rotations.add(normalized_block)

        normalized_blocks.append(unique_rotations)

    # 一致するグループを見つける
    groups = []
    visited = [False] * len(blocks)
    for i in range(len(blocks)):
        if visited[i]:
            continue
        group = [i + 1]
        visited[i] = True
        for j in range(i + 1, len(blocks)):
            if normalized_blocks[i] & normalized_blocks[j]:  # 共通の回転があれば一致
                group.append(j + 1)
                visited[j] = True
        if len(group) > 1:
            groups.append(tuple(group))

    # 各グループの並び替えの可能性を計算
    total_permutations = 1
    for group in groups:
        permutations = factorial(len(group))
        total_permutations *= permutations
        print(f"形が一致するポリオミノ： {group}")

    # 総並び替え数を表示
    if total_permutations > 1:
        print(f"本来の解の個数は {total_permutations} 倍になります。\n")

    return groups


def place_polyomino(solver: Solver, kind: IntArray2D, height: int, width: int, blocks: list[list[list[int]]],
                    rotation: bool = False, reflection: bool = False, check_isomorphism: bool = True):
    if reflection:
        rotation = True
    return _place_polyomino_with_rotation(solver, kind, height, width, blocks, [rotation] * len(blocks),
                                          [reflection] * len(blocks), check_isomorphism)


def place_polyomino_with_rotation(solver: Solver, kind: IntArray2D, height: int, width: int,
                                  blocks: list[list[list[int]]],
                                  rotation: list[bool], reflection: list[bool]):
    if len(blocks) != len(rotation) or len(blocks) != len(reflection):
        raise ValueError("ブロック・回転・反転の数が一致しません。")
    for i in range(len(blocks)):
        if reflection[i]:
            rotation[i] = True
    return _place_polyomino_with_rotation(solver, kind, height, width, blocks, rotation, reflection, False)


def _place_polyomino_with_rotation(solver: Solver, kind: IntArray2D, height: int, width: int,
                                   blocks: list[list[list[int]]], rotation: list[bool], reflection: list[bool],
                                   check_isomorphism: bool = True):
    if len(blocks) == 1:
        check_isomorphism = False

    if check_isomorphism:
        groups = find_matching_polyominoes(blocks, rotation[1], reflection[1])
        if groups:
            print("同型処理を行います。")
            if rotation[1] & reflection[1]:
                print("回転・反転して一致するブロックの並び替えを省略します。")
            elif rotation[1]:
                print("回転のみをして一致するブロックの並び替えを省略します。")
            else:
                print("回転・反転せず一致するブロックの並び替えを省略します。")
            print()

            x_vars = [solver.int_var(0, width - 1) for _ in range(len(blocks))]
            y_vars = [solver.int_var(0, height - 1) for _ in range(len(blocks))]
        else:
            check_isomorphism = False

    for i in range(len(blocks)):
        block = blocks[i]

        # 回転と反転を考慮したポリオミノの生成
        rotations = [block]
        if reflection[i]:  # 反転を考慮
            rotations.append(reflect_block(block))

        final_rotations = []
        for rotated_block in rotations:
            if rotation[i]:  # rotationがTrueなら、90度、180度、270度回転した形を追加
                for _ in range(4):
                    rotated_block = rotate_block(rotated_block)
                    final_rotations.append(rotated_block)
            else:
                final_rotations.append(rotated_block)

        unique_blocks = set()  # 重複する回転・反転状態を除外するためのセット
        normalized_rotations = []
        for rotated_block in final_rotations:
            normalized_block = tuple(map(tuple, normalize_block(rotated_block)))
            if normalized_block not in unique_blocks:
                unique_blocks.add(normalized_block)
                normalized_rotations.append(normalized_block)

        conditions = []
        for rotated_block in normalized_rotations:

            b_height = len(rotated_block)
            b_width = len(rotated_block[0])

            for y in range(height - b_height + 1):
                for x in range(width - b_width + 1):

                    b = [[0] * width for _ in range(height)]
                    for yy in range(b_height):
                        for xx in range(b_width):
                            if rotated_block[yy][xx] == 1:
                                b[y + yy][x + xx] = 1

                    condition = fold_and(
                        (kind[Y, X] == i + 1) == (b[Y][X] == 1) for Y in range(height) for X in range(width))

                    conditions.append(condition)

                    # 同型ポリオミノが存在する場合、数字が小さい方が左上に位置する制約
                    if check_isomorphism:
                        solver.ensure(
                            then(condition,
                                 fold_and(x_vars[i] == x, y_vars[i] == y))
                        )

        solver.ensure(count_true(fold_or(conditions)) == 1)

    if check_isomorphism:
        # 同型ポリオミノが存在する場合、番号が小さい方が左上に位置する制約
        for group in groups:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    solver.ensure(
                        (x_vars[group[i] - 1] < x_vars[group[j] - 1]) |
                        ((x_vars[group[i] - 1] == x_vars[group[j] - 1]) & (
                                y_vars[group[i] - 1] <= y_vars[group[j] - 1]))
                    )
