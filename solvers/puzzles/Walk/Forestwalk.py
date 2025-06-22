import cspuz
from cspuz import Solver, graph, BoolGridFrame
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.expr import BoolExpr
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D

# forest
_ = False
X = True


def solve_forestwalk(forest: list[list[bool]], num: list[list[any]]):
    height = len(forest)
    width = len(forest[0])

    solver = Solver()
    is_line = graph.BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(is_line)

    # The network is connected
    vertices, g = graph._from_grid_frame(is_line)
    line_graph = g.line_graph()
    graph.active_vertices_connected(solver, vertices, line_graph)

    is_passed = solver.bool_array((height, width))

    rank = solver.int_array((height, width), 0, height * width - 1)
    size = solver.int_array((height, width), 0, height * width - 1)
    solver.ensure(rank <= size)

    for y in range(height):
        for x in range(width):
            solver.ensure(
                (~is_passed[y, x]).then(
                    ~fold_or((is_line.vertex_neighbors(y, x)))
                ))

            if forest[y][x]:
                solver.ensure(
                    is_passed[y, x].then(
                        count_true(is_line.vertex_neighbors(y, x)) == 3
                    )
                )
                solver.ensure(rank[y, x] == 0)
                solver.ensure(size[y, x] == 0)
            else:
                solver.ensure(
                    is_passed[y, x].then(
                        count_true(is_line.vertex_neighbors(y, x)) == 2
                    )
                )

                if num[y][x] != _:
                    solver.ensure(is_passed[y, x])
                    solver.ensure(size[y, x] == num[y][x] - 1)

                lower = []
                upper = []

                def check_neighbor(edge: BoolExpr, y2, x2):
                    if forest[y2][x2]:
                        solver.ensure(edge.then((rank[y, x] == 0) | (rank[y, x] == size[y, x])))
                        lower.append(edge & (rank[y, x] == 0))
                        upper.append(edge & (rank[y, x] == size[y, x]))
                    else:
                        solver.ensure(edge.then(
                            (rank[y2, x2] == rank[y, x] + 1) | (rank[y2, x2] == rank[y, x] - 1)
                        ))
                        solver.ensure(edge.then(size[y2, x2] == size[y, x]))
                        lower.append(edge & (rank[y2, x2] == rank[y, x] - 1))
                        upper.append(edge & (rank[y2, x2] == rank[y, x] + 1))

                if y > 0:
                    check_neighbor(is_line.vertical[y - 1, x], y - 1, x)
                if y < height - 1:
                    check_neighbor(is_line.vertical[y, x], y + 1, x)
                if x > 0:
                    check_neighbor(is_line.horizontal[y, x - 1], y, x - 1)
                if x < width - 1:
                    check_neighbor(is_line.horizontal[y, x], y, x + 1)

                solver.ensure(is_passed[y, x].then(count_true(lower) >= 1))
                solver.ensure(is_passed[y, x].then(count_true(upper) >= 1))

    is_sat = solver.solve()
    return is_sat, is_line


if __name__ == "__main__":
    forest = [
        [_, _, X, _, X, _],
        [X, _, _, _, X, _],
        [_, _, _, X, _, _],
        [_, _, _, _, _, _],
        [X, X, _, _, X, _],
    ]
    num = [
        [2, _, _, 3, _, _],
        [_, _, _, _, _, _],
        [_, _, _, _, 4, _],
        [_, _, _, _, _, _],
        [_, _, _, _, _, _],
    ]

    is_sat, is_line = solve_forestwalk(forest, num)
    if is_sat:
        print("Solution found:")
        print(stringify_grid_frame(is_line))
    else:
        print("No solution exists.")