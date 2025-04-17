import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

U = 1
D = 2
L = 3
R = 4


def solve_guidearrow(ty: int, tx: int, problem: list[list[int]]):
    height, width = len(problem), len(problem[0])

    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)
    graph.active_vertices_connected(solver, ~is_black)

    solver.ensure(~(is_black[:-1, :] & is_black[1:, :]))
    solver.ensure(~(is_black[:, :-1] & is_black[:, 1:]))

    rank = solver.int_array((height, width), 0, height * width)
    solver.ensure(rank[ty, tx] == 0)

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
                        return None
                    solver.ensure(~is_black[y - 1, x])
                    solver.ensure(rank[y - 1, x] < rank[y, x])
                if problem[y][x] == R:
                    if x == width - 1:
                        return None
                    solver.ensure(~is_black[y, x + 1])
                    solver.ensure(rank[y, x + 1] < rank[y, x])
                if problem[y][x] == D:
                    if y == height - 1:
                        return None
                    solver.ensure(~is_black[y + 1, x])
                    solver.ensure(rank[y + 1, x] < rank[y, x])
                if problem[y][x] == L:
                    solver.ensure(~is_black[y, x - 1])
                    solver.ensure(rank[y, x - 1] < rank[y, x])

    # グラフで、アースする制約をつける

    aux_graph = graph.Graph(height * width + 1)
    aux_vertices = []

    def to_vertex(y, x):
        return y * width + x

    for y in range(height):
        for x in range(width):
            aux_vertices.append(is_black[y, x])
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                aux_graph.add_edge(to_vertex(y, x), height * width)

    aux_vertices.append(True)

    for y in range(height - 1):
        for x in range(width - 1):
            aux_graph.add_edge(to_vertex(y, x), to_vertex(y + 1, x + 1))
            aux_graph.add_edge(to_vertex(y, x + 1), to_vertex(y + 1, x))

    graph.active_vertices_connected(solver, aux_vertices, aux_graph)

    is_sat = solver.solve()
    return is_sat, is_black


from cspuz.problem_serializer import Tupl, DecInt, MultiDigit, HexInt, Grid, OneOf, IntSpaces, Spaces, Dict
from cspuz.problem_serializer import serialize_problem_as_url, deserialize_problem_as_url

SLITHERLINK_COMBINATOR = Grid(OneOf(
    IntSpaces(0, max_int=4, max_num_spaces=2),
    Dict(5, "."),
    Spaces(0, "g"),
))


def deserialize_slitherlink(url):
    return deserialize_problem_as_url(SLITHERLINK_COMBINATOR, url, allowed_puzzles="guidearrow")


if __name__ == "__main__":
    import time

    # 溶けるまでの時間を計測
    start = time.time()

    p = deserialize_slitherlink(
        "https://puzz.link/p?guidearrow/26/26/zjegbzzndzczhehdzhbzezzrdzczhehdzhbzezzrdzczhehdzhbzezzrdzzztbzzo")

    print (stringify_array(p, common_rules.NUM_MAP))

    ty = 25
    tx = 23

    is_sat, is_black = solve_guidearrow(ty, tx, p)

    if is_sat:
        print(stringify_array(is_black, common_rules.BW_MAP))
    else:
        print('no solution')

    end = time.time()
    print("time:", end - start)