import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

# 0: pillar, 1: aisle, 2: pillow, 3: futon(not pillow)
PILLAR = 0
AISLE = 1
PILLOW = 2
FUTON = 3

# 布団の方角 AISLEとPILLARはNONE
# -1: none, 0: north, 1: south, 2: west, 3: east
NONE = -1
NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3

V_西枕禁 = 1
V_添い寝厳禁 = 2
V_添い寝厳守 = 3
V_布団ひとつながり = 4
V_通路へび = 5
V_縦横枕同個数 = 6
V_枕ひとつながり = 7
V_通路長さ4禁 = 8


def solve_shugaku(height: int, width: int, problem: list[list[int]], variant=0):
    solver = Solver()
    kind = solver.int_array((height, width), 0, 3)
    direction = solver.int_array((height, width), -1, 3)
    solver.add_answer_key(kind)
    solver.add_answer_key(direction)

    graph.active_vertices_connected(solver, kind == AISLE)
    common_rules.not_forming_2by2_square(solver, kind == AISLE)

    # DIRECTIONの条件を追加 PILLARまたはAISLEである <=> 方向がNONE
    solver.ensure(((kind == PILLAR) | (kind == AISLE)) == (direction == NONE))

    # 問題の条件を追加 5 -1 は柱 それ以外は柱でない 数字は周囲の枕の数
    for y in range(height):
        for x in range(width):
            if problem[y][x] == 5:
                solver.ensure(kind[y, x] == PILLAR)
            elif problem[y][x] != -1:
                solver.ensure(kind[y, x] == PILLAR)
                solver.ensure(count_true(kind.four_neighbors(y, x) == PILLOW) == problem[y][x])
            else:
                solver.ensure(kind[y, x] != PILLAR)

    # 布団の条件を追加
    for y in range(height):
        for x in range(width):
            if (y < height - 1):
                solver.ensure(
                    ((kind[y, x] == PILLOW) & (direction[y, x] == NORTH)) ==
                    ((kind[y + 1, x] == FUTON) & (direction[y + 1, x] == NORTH))
                )
            else:
                solver.ensure(~((kind[y, x] == PILLOW) & (direction[y, x] == NORTH)))
                solver.ensure(~((kind[y, x] == FUTON) & (direction[y, x] == SOUTH)))

            if (y > 0):
                solver.ensure(
                    ((kind[y, x] == PILLOW) & (direction[y, x] == SOUTH)) ==
                    ((kind[y - 1, x] == FUTON) & (direction[y - 1, x] == SOUTH))
                )
            else:
                solver.ensure(~((kind[y, x] == PILLOW) & (direction[y, x] == SOUTH)))
                solver.ensure(~((kind[y, x] == FUTON) & (direction[y, x] == NORTH)))

            if (x < width - 1):
                solver.ensure(
                    ((kind[y, x] == PILLOW) & (direction[y, x] == WEST)) ==
                    ((kind[y, x + 1] == FUTON) & (direction[y, x + 1] == WEST))
                )
            else:
                solver.ensure(~((kind[y, x] == PILLOW) & (direction[y, x] == WEST)))
                solver.ensure(~((kind[y, x] == FUTON) & (direction[y, x] == EAST)))

            if (x > 0):
                solver.ensure(
                    ((kind[y, x] == PILLOW) & (direction[y, x] == EAST)) ==
                    ((kind[y, x - 1] == FUTON) & (direction[y, x - 1] == EAST))
                )
            else:
                solver.ensure(~((kind[y, x] == PILLOW) & (direction[y, x] == EAST)))
                solver.ensure(~((kind[y, x] == FUTON) & (direction[y, x] == WEST)))

    # 布団の周囲には少なくとも１つのAISLEがある
    directions = {
        NORTH: ([-1, 0, 0, 1, 1, 2], [0, -1, 1, -1, 1, 0]),
        SOUTH: ([-2, 1, -1, 0, -1, 0], [0, 0, -1, -1, 1, 1]),
        WEST: ([0, 0, -1, -1, 1, 1], [2, -1, 1, 0, 1, 0]),
        EAST: ([0, 0, -1, -1, 1, 1], [-2, 1, -1, 0, -1, 0])
    }

    for y in range(height):
        for x in range(width):
            for direction_key, (dy, dx) in directions.items():
                neighbor_aisles = []
                for i in range(6):
                    ny = y + dy[i]
                    nx = x + dx[i]
                    if 0 <= ny < height and 0 <= nx < width:
                        neighbor_aisles.append(kind[ny, nx] == AISLE)
                solver.ensure(
                    then(fold_and(kind[y, x] == PILLOW, direction[y, x] == direction_key), fold_or(neighbor_aisles)))

    solver.ensure(direction != NORTH)

    # variants
    if variant == V_西枕禁:
        solver.ensure(direction != WEST)
    elif variant == V_添い寝厳禁:
        common_rules.all_black_blocks_have_same_area_2(solver, direction == NORTH)
        common_rules.all_black_blocks_have_same_area_2(solver, direction == SOUTH)
        common_rules.all_black_blocks_have_same_area_2(solver, direction == WEST)
        common_rules.all_black_blocks_have_same_area_2(solver, direction == EAST)
    elif variant == V_添い寝厳守:
        for y in range(height):
            for x in range(width):
                for direction_key, (dy, dx) in directions.items():
                    neighbor_directions = []
                    for i in range(6):
                        ny = y + dy[i]
                        nx = x + dx[i]
                        if 0 <= ny < height and 0 <= nx < width:
                            neighbor_directions.append(direction[ny, nx] == direction_key)
                    solver.ensure(
                        then(fold_and(kind[y, x] == PILLOW, direction[y, x] == direction_key),
                             fold_or(neighbor_directions)))
    elif variant == V_布団ひとつながり:
        graph.active_vertices_connected(solver, (kind == PILLOW) | (kind == FUTON))
    elif variant == V_通路へび:
        for y in range(height):
            for x in range(width):
                solver.ensure(then(kind[y, x] == AISLE, count_true(kind.four_neighbors(y, x) == AISLE) <= 2))
    elif variant == V_縦横枕同個数:
        common_rules.equal_black_cells_in_each_row_and_column(solver, kind == PILLOW)
    elif variant == V_枕ひとつながり:
        graph.active_vertices_connected(solver, kind == PILLOW)
    elif variant == V_通路長さ4禁:
        for y in range(height):
            for x in range(width):
                if y < height - 3:
                    solver.ensure(~fold_and(kind[y: y + 4, x] == AISLE))
                if x < width - 3:
                    solver.ensure(~fold_and(kind[y, x: x + 4] == AISLE))

    has_answer = solver.solve()
    return has_answer, kind, direction


def solve_and_show(height: int, width: int, problem: list[list[int]], variant=0):
    has_answer, board, direction = solve_shugaku(height, width, problem, variant=variant)
    if has_answer:
        # print(stringify_array(board, {0: "O", 1: "#", 2: "P", 3: "F", None: "?"}))
        # print()
        # print(stringify_array(direction, {0: "#", 1: "v", 2: "<", 3: ">", None: "?"}))
        for y in range(height):
            ans = []
            for x in range(width):
                t = ""
                if board[y, x].sol == None:
                    t = "?"
                elif board[y, x].sol == PILLAR:
                    t = "O"
                elif board[y, x].sol == AISLE:
                    t = "#"
                elif board[y, x].sol == PILLOW:
                    t = "P"
                elif board[y, x].sol == FUTON:
                    t = "F"

                if direction[y, x].sol == None:
                    t += "?"
                elif direction[y, x].sol == NONE:
                    t *= 2
                elif direction[y, x].sol == NORTH:
                    t += "^"
                elif direction[y, x].sol == SOUTH:
                    t += "v"
                elif direction[y, x].sol == WEST:
                    t += "<"
                elif direction[y, x].sol == EAST:
                    t += ">"

                ans.append(t)
            print(*ans)
    else:
        print('no answer')


from cspuz.problem_serializer import (
    Grid,
    OneOf,
    Spaces,
    HexInt,
    DecInt,
    Dict,
    serialize_problem_as_url,
    deserialize_problem_as_url,
)

SHUGAKU_COMBINATOR = Grid(OneOf(Spaces(-1, "6"), DecInt()))


def serialize_shugaku(problem):
    height = len(problem)
    width = len(problem[0])
    return serialize_problem_as_url(SHUGAKU_COMBINATOR, "shugaku", height, width, problem)


def generate_shugaku(height, width, verbose=False, symmetry=False, variant=0):
    def penalty(problem):
        if variant != 0:
            return count_non_default_values(problem, -1, 40)

        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] == 5:
                    ret += 12
                # elif problem[y][x] == 4:
                #     ret += 30
                elif problem[y][x] != -1:
                    ret += 15 + problem[y][x] * 2
        return ret

    def compute_score(kind: cspuz.solver.IntArray2D, dir: cspuz.solver.IntArray2D):
        score = 0

        for y in range(height):
            for x in range(width):
                if kind[y, x].sol is not None:
                    score += 1
                # if kind[y, x].sol == 2:
                #     neighbors = []
                #     if y > 0:
                #         neighbors.append(kind[y - 1][x].sol)
                #     if y < height - 1:
                #         neighbors.append(kind[y + 1][x].sol)
                #     if x > 0:
                #         neighbors.append(kind[y][x - 1].sol)
                #     if x < width - 1:
                #         neighbors.append(kind[y][x + 1].sol)
                #     # neighbor!=0となる数を取得
                #     non_zero_neighbors = [n for n in neighbors if n != 0]
                #     non_zero_count = len(non_zero_neighbors)
                #     # neighborsがすべて0でないとき
                #     if all([n != 0 for n in neighbors]):
                #         score += 20

                if dir[y, x].sol is not None:
                    score += 1

        return score

    generated = generate_problem(lambda problem: solve_shugaku(height, width, problem, variant=variant),
                                 builder_pattern=ArrayBuilder2D(height, width, [-1, 0, 1, 2, 3, 4, 5], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=penalty,
                                 score=compute_score,
                                 verbose=verbose,
                                 # pretest=pretest,
                                 # initial_temperature=20.0,
                                 # temperature_decay=0.99,
                                 )

    return generated


import multiprocessing


def generatehxw(height, width, variant=0):
    problem = generate_shugaku(height, width, symmetry=False, verbose=True, variant=variant)
    solve_and_show(height, width, problem, variant=variant)
    print(serialize_shugaku(problem))


# 並列生成関数
def parallel_generatehxw(height, width, num, variant=0):
    # 引数をタプルで渡すように修正
    with multiprocessing.Pool(processes=num) as pool:
        results = pool.starmap(generatehxw, [(height, width, variant)] * num)  # height, width, variant を繰り返す
    return results


if __name__ == "__main__":
    _ = -1
    o = 5
    def problem1():
        height = 10
        width = 10
        problem = [
            [5, -1, -1, 0, -1, -1, -1, -1, -1, 5],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, 5],
            [-1, 1, -1, -1, -1, -1, -1, 4, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, 3, -1, -1, -1],
            [-1, -1, -1, -1, 4, -1, -1, -1, -1, -1],
            [-1, -1, 3, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, -1, -1, 2, -1, 1, -1, -1, 5, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, 0, -1],
        ]
        solve_and_show(height, width, problem)


    def problem2():
        height = 8
        width = 8
        problem = [
            [o, _, _, _, _, _, _, _],
            [1, 0, _, _, _, o, _, _],
            [_, _, _, _, _, _, _, 3],
            [_, _, _, _, _, o, _, _],
            [_, _, _, _, 0, _, _, _],
            [o, _, _, _, _, _, _, _],
            [_, _, _, _, o, _, _, 1],
            [0, _, _, _, _, _, _, _],

        ]
        solve_and_show(height, width, problem, variant=V_通路長さ4禁)


    def gen():
        results = parallel_generatehxw(8, 8, 6, variant=V_布団ひとつながり)
        for result in results:
            print(result)


    gen()