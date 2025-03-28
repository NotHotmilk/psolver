import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


_ = 0
U = 1
R = 2
D = 3
L = 4
X = 5


def solve_guidearrow(ty: int, tx: int, problem: list[list[int]]):
    height, width = len(problem), len(problem[0])

    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)
    graph.active_vertices_connected(solver, ~is_black)

    for y in range(height):
        for x in range(width):
            solver.ensure(
                is_black[y, x].then(
                    count_true(is_black.four_neighbors(y, x)) == 1
                )
            )

    rank = solver.int_array((height, width), 0, height * width)
    solver.ensure(rank[ty, tx] == 0)
    solver.ensure(~is_black[ty, tx])

    for y in range(height):
        for x in range(width):
            if (y, x) != (ty, tx):
                solver.ensure(
                    (~is_black[y, x]).then(
                        fold_and(
                            (~is_black.four_neighbors(y, x)).then(
                                rank.four_neighbors(y, x) != rank[y, x]
                            )
                        )
                        & (count_true(
                            (~is_black.four_neighbors(y, x)) & (rank.four_neighbors(y, x) < rank[y, x])
                        ) == 1)
                    )
                )

            if problem[y][x] != 0:
                solver.ensure(~is_black[y, x])
                if problem[y][x] == U:
                    if y == 0:
                        return False, None
                    solver.ensure(~is_black[y - 1, x])
                    solver.ensure(rank[y - 1, x] < rank[y, x])
                if problem[y][x] == R:
                    if x == width - 1:
                        return False, None
                    solver.ensure(~is_black[y, x + 1])
                    solver.ensure(rank[y, x + 1] < rank[y, x])
                if problem[y][x] == D:
                    if y == height - 1:
                        return False, None
                    solver.ensure(~is_black[y + 1, x])
                    solver.ensure(rank[y + 1, x] < rank[y, x])
                if problem[y][x] == L:
                    if x == 0:
                        return False, None
                    solver.ensure(~is_black[y, x - 1])
                    solver.ensure(rank[y, x - 1] < rank[y, x])

    # 補助. 長方形条件
    for y in range(height - 1):
        for x in range(width - 1):
            solver.ensure(count_true(is_black[y:y + 2, x:x + 2]) != 3)

    is_sat = solver.solve()
    return is_sat, is_black,


def generate_guidearrow(height: int, width: int, ty: int, tx: int, verbose=False):
    def compute_score(is_black):
        score = 0

        for y in range(height):
            for x in range(width):
                if is_black[y, x].sol is not None:
                    score += 1

        return score

    generated = generate_problem(lambda problem: solve_guidearrow(ty, tx, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [0, U, L, R, D], default=0),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=0, weight=6),
                                 verbose=verbose,
                                 # score=compute_score,
                                 )
    return generated


if __name__ == "__main__":
    ty, tx = 7, 7
    problem = [
        [0, 0, 0, 0, 0, 0, 0, R, 0, 0, 0, 0, 0, 0, 0],
        [U, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, D],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [U, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, D],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [U, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, D],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [U, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, D],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [U, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, D],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [U, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [U, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, L, 0, 0, 0, 0, 0],
    ]
    is_sat, is_black = solve_guidearrow(ty, tx, problem)

    if is_sat:
        print(stringify_array(is_black, common_rules.BW_MAP))
    else:
        print('no solution')

    # problem = generate_guidearrow(9, 9, 4, 4, verbose=True)
    #
    # is_sat, is_black, _ = solve_guidearrow(4, 4, problem)
    # if is_sat:
    #     print(stringify_array(is_black, common_rules.BW_MAP))
    # else:
    #     print('no solution')
