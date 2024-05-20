import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_shugaku(height: int, width: int, problem: list[list[int]]):
    solver = Solver()
    kind = solver.int_array((height, width), 0, 3)
    # 0: pillar, 1: aisle, 2: pillow, 3: futon
    direction = solver.int_array((height, width), 0, 3)
    # 枕の向き
    # 0: none, 1: down, 2: left, 3: right
    solver.add_answer_key(kind)
    solver.add_answer_key(direction)

    graph.active_vertices_connected(solver, kind == 1)
    common_rules.not_forming_2by2_square(solver, kind == 1)

    # 問題の条件を追加　
    for y in range(height):
        for x in range(width):
            if problem[y][x] == 5:
                solver.ensure(kind[y, x] == 0)
            elif problem[y][x] != -1:
                solver.ensure(kind[y, x] == 0)
                solver.ensure(count_true(kind.four_neighbors(y, x) == 2) == problem[y][x])
            else:
                solver.ensure(kind[y, x] != 0)
            solver.ensure(then(fold_or(kind[y, x] == 2, kind[y, x] == 3), direction[y, x] != 0))
            solver.ensure(then(fold_or(kind[y, x] == 0, kind[y, x] == 1), direction[y, x] == 0))

    # 布団を形成する
    for y in range(height):
        for x in range(width):
            solver.ensure(
                then(kind[y, x] == 2, count_true(
                    fold_and(direction[y, x] == 1, kind[max(0, y - 1), x] == 3, direction[max(0, y - 1), x] == 1),
                    fold_and(direction[y, x] == 2, kind[y, min(width - 1, x + 1)] == 3,
                             direction[y, min(width - 1, x + 1)] == 2),
                    fold_and(direction[y, x] == 3, kind[y, max(0, x - 1)] == 3, direction[y, max(0, x - 1)] == 3)
                ) == 1)
            )

    # 布団の周囲に少なくとも一つの通路がある
    for y in range(height):
        for x in range(width):
            # down
            down = []
            if y > 1:
                down.append(kind[y - 2, x] == 1)
            if y < height - 1:
                down.append(kind[y + 1, x] == 1)
            if x > 0 and y > 0:
                down.append(kind[y - 1, x - 1] == 1)
            if x > 0:
                down.append(kind[y, x - 1] == 1)
            if x < width - 1 and y > 0:
                down.append(kind[y - 1, x + 1] == 1)
            if x < width - 1:
                down.append(kind[y, x + 1] == 1)
            solver.ensure(then(fold_and(kind[y, x] == 2, direction[y, x] == 1), fold_or(down)))

            # left
            left = []
            if y > 0:
                left.append(kind[y - 1, x] == 1)
            if y < height - 1:
                left.append(kind[y + 1, x] == 1)
            if x > 0:
                left.append(kind[y, x - 1] == 1)
            if x < width - 1 and y > 0:
                left.append(kind[y - 1, x + 1] == 1)
            if x < width - 1 and y < height - 1:
                left.append(kind[y + 1, x + 1] == 1)
            if x < width - 2:
                left.append(kind[y, x + 2] == 1)
            solver.ensure(then(fold_and(kind[y, x] == 2, direction[y, x] == 2), fold_or(left)))

            # right
            right = []
            if y > 0:
                right.append(kind[y - 1, x] == 1)
            if y < height - 1:
                right.append(kind[y + 1, x] == 1)
            if x < width - 1:
                right.append(kind[y, x + 1] == 1)
            if x > 0 and y > 0:
                right.append(kind[y - 1, x - 1] == 1)
            if x > 0 and y < height - 1:
                right.append(kind[y + 1, x - 1] == 1)
            if x > 1:
                right.append(kind[y, x - 2] == 1)
            solver.ensure(then(fold_and(kind[y, x] == 2, direction[y, x] == 3), fold_or(right)))

    has_answer = solver.solve()

    return has_answer, kind, direction


def generate_shugaku(height, width, verbose=False, symmetry=False):
    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] == 5:
                    ret += 10
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
                        score += 1000

                if dir[y, x].sol is not None:
                    score += 1

        return score

    # def pretest(problem):
    #     import max_rectangle
    #     max_area, (h, w) = max_rectangle.max_rectangle_area_with_dimensions(
    #         [[1 if problem[y][x] == -1 else 0 for x in range(width)] for y in range(height)])
    #     return max_area >= 20

    generated = generate_problem(lambda problem: solve_shugaku(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [-1, 0, 1, 2, 3, 4, 5], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=penalty,
                                 score=compute_score,
                                 verbose=verbose,
                                 # pretest=pretest,
                                 )

    return generated


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


def generatehxw(height, width):
    print("Generating")
    problem = generate_shugaku(height, width, symmetry=False, verbose=True)

    has_answer, board, direction = solve_shugaku(height, width, problem)

    print(stringify_array(problem, {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "x", -1: "."}))
    print()
    print(stringify_array(board, {0: "O", 1: "#", 2: "P", 3: "F", None: "?"}))
    print()
    print(stringify_array(direction, {0: ".", 1: "v", 2: "<", 3: ">", None: "?"}))
    # print(stringify_array(board + 4 * direction,
    #                       {0: "( )", 1: "###", 6: "[v]", 10: "[<]", 14: "[>]", 7: "vvv", 11: "<<<", 15: ">>>", None: "?"}))
    print()
    print(serialize_shugaku(problem))

    return serialize_shugaku(problem)


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(generatehxw_wrapper, range(4))
    return results


def generatehxw_wrapper(i):
    return generatehxw(8, 8)


if __name__ == '__main__':

    results = parallel_generatehxw()
    for result in results:
        print(result)

    # height = 5
    # width = 5
    # problem = [
    #     [-1, -1, -1, -1, -1],
    #     [-1, 4, -1, -1, -1],
    #     [-1, -1, -1, -1, -1],
    #     [-1, -1, -1, -1, -1],
    #     [ 5, -1, -1,  1, -1]
    # ]
    #
    # has_answer, board, direction = solve_shugaku(height, width, problem)
    # if has_answer:
    #     print(stringify_array(board, {0: "O", 1: "#", 2: "P", 3: "F", None: "?"}))
    #     print()
    #     print(stringify_array(direction, {0: "#", 1: "v", 2: "<", 3: ">", None: "?"}))
    # else:
    #     print('no answer')
