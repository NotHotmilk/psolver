import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

# 0: pillar, 1: aisle, 2: pillow, 3: futon
PILLAR = 0
AISLE = 1
PILLOW = 2
FUTON = 3

# 布団の方角 AISLEとPILLARはNONE
# 0: none, 1: south, 2: west, 3: east; not allowed: north
NONE = 0
SOUTH = 1
WEST = 2
EAST = 3


def solve_shugaku(height: int, width: int, problem: list[list[int]], variant = False):
    solver = Solver()
    kind = solver.int_array((height, width), 0, 3)
    direction = solver.int_array((height, width), 0, 3)
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
            solver.ensure(
                then((kind[y, x] == PILLOW) & (direction[y, x] == SOUTH),
                     (kind[max(y - 1, 0), x] == FUTON) & (direction[max(y - 1, 0), x] == SOUTH))
            )
            solver.ensure(
                then((kind[y, x] == PILLOW) & (direction[y, x] == WEST),
                     (kind[y, min(x + 1, width - 1)] == FUTON) & (direction[y, min(x + 1, width - 1)] == WEST))
            )
            solver.ensure(
                then((kind[y, x] == PILLOW) & (direction[y, x] == EAST),
                     (kind[y, max(x - 1, 0)] == FUTON) & (direction[y, max(x - 1, 0)] == EAST))
            )
            solver.ensure(
                then((kind[y, x] == FUTON) & (direction[y, x] == SOUTH),
                     (kind[min(y + 1, height - 1), x] == PILLOW) & (direction[min(y + 1, height - 1), x] == SOUTH))
            )
            solver.ensure(
                then((kind[y, x] == FUTON) & (direction[y, x] == WEST),
                     (kind[y, max(x - 1, 0)] == PILLOW) & (direction[y, max(x - 1, 0)] == WEST))
            )
            solver.ensure(
                then((kind[y, x] == FUTON) & (direction[y, x] == EAST),
                     (kind[y, min(x + 1, width - 1)] == PILLOW) & (direction[y, min(x + 1, width - 1)] == EAST))
            )

    # variantの条件を追加
    if variant:
        solver.ensure(direction != WEST)

    # 布団の周囲には少なくとも１つのAISLEがある
    # South
    # ? X ?
    # X F X
    # X P X
    # ? X ?
    sdy = [-2, 1, -1, 0, -1, 0]
    sdx = [0, 0, -1, -1, 1, 1]
    wdy = [0, 0, -1, -1, 1, 1]
    wdx = [2, -1, 1, 0, 1, 0]
    edy = [0, 0, -1, -1, 1, 1]
    edx = [-2, 1, -1, 0, -1, 0]

    for y in range(height):
        for x in range(width):
            south = []
            for i in range(6):
                ny = y + sdy[i]
                nx = x + sdx[i]
                if 0 <= ny < height and 0 <= nx < width:
                    south.append(kind[ny, nx] == AISLE)
            solver.ensure(then(fold_and(kind[y, x] == PILLOW, direction[y, x] == SOUTH), fold_or(south)))

            west = []
            for i in range(6):
                ny = y + wdy[i]
                nx = x + wdx[i]
                if 0 <= ny < height and 0 <= nx < width:
                    west.append(kind[ny, nx] == AISLE)
            solver.ensure(then(fold_and(kind[y, x] == PILLOW, direction[y, x] == WEST), fold_or(west)))

            east = []
            for i in range(6):
                ny = y + edy[i]
                nx = x + edx[i]
                if 0 <= ny < height and 0 <= nx < width:
                    east.append(kind[ny, nx] == AISLE)
            solver.ensure(then(fold_and(kind[y, x] == PILLOW, direction[y, x] == EAST), fold_or(east)))

    has_answer = solver.solve()
    return has_answer, kind, direction


def solve_and_show(height: int, width: int, problem: list[list[int]]):
    has_answer, board, direction = solve_shugaku(height, width, problem)
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
                elif direction[y, x].sol == 0:
                    t *= 2
                elif direction[y, x].sol == 1:
                    t += "v"
                elif direction[y, x].sol == 2:
                    t += "<"
                elif direction[y, x].sol == 3:
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


def generate_shugaku(height, width, verbose=False, symmetry=False, variant = False):
    def penalty(problem):
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
                if kind[y, x].sol == 2:
                    neighbors = []
                    if y > 0:
                        neighbors.append(kind[y - 1][x].sol)
                    if y < height - 1:
                        neighbors.append(kind[y + 1][x].sol)
                    if x > 0:
                        neighbors.append(kind[y][x - 1].sol)
                    if x < width - 1:
                        neighbors.append(kind[y][x + 1].sol)
                    # neighbor!=0となる数を取得
                    non_zero_neighbors = [n for n in neighbors if n != 0]
                    non_zero_count = len(non_zero_neighbors)
                    # neighborsがすべて0でないとき
                    if all([n != 0 for n in neighbors]):
                        score += 20

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


def generatehxw(height, width):
    print("Generating")
    problem = generate_shugaku(height, width, symmetry=False, verbose=True, variant=True)

    solve_and_show(height, width, problem)
    print(serialize_shugaku(problem))


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(generatehxw_wrapper, range(8))
    return results


def generatehxw_wrapper(i):
    return generatehxw(8, 8)


if __name__ == "__main__":
    # height = 10
    # width = 10
    # problem = [
    #     [5, -1, -1, 0, -1, -1, -1, -1, -1,  5],
    #     [-1, -1, -1, -1, -1, -1, -1, -1, -1,  5],
    #     [-1, 1, -1, -1, -1, -1, -1,  4, -1, -1],
    #     [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    #     [-1, -1, -1, -1, -1, -1,  3, -1, -1, -1],
    #     [-1, -1, -1, -1,  4, -1, -1, -1, -1, -1],
    #     [-1, -1,  3, -1, -1, -1, -1, -1, -1, -1],
    #     [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    #     [-1, -1, -1,  2, -1,  1, -1, -1,  5, -1],
    #     [-1, -1, -1, -1, -1, -1, -1, -1,  0, -1],
    # ]
    #
    # solve_and_show(height, width, problem)

    results = parallel_generatehxw()
    for result in results:
        print(result)
