import cspuz
from cspuz import Solver, graph, BoolGridFrame
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.expr import BoolExpr
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D

# fire
_ = False
X = True


def solve_firewalk(fire: list[list[bool]], num: list[list[any]]):
    height = len(fire)
    width = len(fire[0])

    solver = Solver()
    is_line = graph.BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(is_line)

    for y in range(height):
        for x in range(width):
            if num[y][x] != _:
                solver.ensure(fold_or(is_line.vertex_neighbors(y, x)))

    is_inner = solver.bool_array((height - 1, width - 1))
    for y in range(height):
        for x in range(width - 1):
            if y == 0:
                up = False
            else:
                up = is_inner[y - 1, x]
            if y == height - 1:
                down = False
            else:
                down = is_inner[y, x]
            solver.ensure(~(up ^ down ^ is_line.horizontal[y, x]))
    for y in range(height - 1):
        for x in range(width):
            if x == 0:
                left = False
            else:
                left = is_inner[y, x - 1]
            if x == width - 1:
                right = False
            else:
                right = is_inner[y, x]
            solver.ensure(~(left ^ right ^ is_line.vertical[y, x]))

    # false:
    # + | +
    #  0
    # -   -
    #    1
    # + | +
    #
    # true:
    # + | +
    #    0
    # -   -
    #  1
    # + | +

    fire_cell_mode = solver.bool_array((height, width))
    solver.add_answer_key(fire_cell_mode)

    cell_ids = [[[] for __ in range(width)] for __ in range(height)]
    last_cell_id = 0

    for y in range(height):
        for x in range(width):
            cell_ids[y][x].append(last_cell_id)
            last_cell_id += 1
            if fire[y][x]:
                cell_ids[y][x].append(last_cell_id)
                last_cell_id += 1

                solver.ensure(
                    (~fold_or(is_line.vertex_neighbors(y, x))).then(~fire_cell_mode[y, x])
                )

                if 0 < y < height - 1 and 0 < x < width - 1:
                    solver.ensure(
                        fold_and(is_line.vertex_neighbors(y, x))
                        .then(
                            fire_cell_mode[y, x] == is_inner[y - 1, x - 1]
                        )
                    )
            else:
                solver.ensure(~fire_cell_mode[y, x])

    aux_graph = graph.Graph(last_cell_id)
    loop_edges = []
    for y in range(height):
        for x in range(width - 1):
            for i in range(len(cell_ids[y][x])):
                for j in range(len(cell_ids[y][x + 1])):
                    condition = True

                    if len(cell_ids[y][x]) == 2:
                        if i == 0:
                            condition = condition & fire_cell_mode[y, x]
                        else:
                            condition = condition & ~fire_cell_mode[y, x]
                    if len(cell_ids[y][x + 1]) == 2:
                        if j == 0:
                            condition = condition & ~fire_cell_mode[y, x + 1]
                        else:
                            condition = condition & fire_cell_mode[y, x + 1]
                    aux_graph.add_edge(cell_ids[y][x][i], cell_ids[y][x + 1][j])
                    loop_edges.append(condition & is_line.horizontal[y, x])

    for y in range(height - 1):
        for x in range(width):
            for i in range(len(cell_ids[y][x])):
                for j in range(len(cell_ids[y + 1][x])):
                    if len(cell_ids[y][x]) == 2:
                        if i != 1:
                            continue
                    if len(cell_ids[y + 1][x]) == 2:
                        if j != 0:
                            continue

                    aux_graph.add_edge(cell_ids[y][x][i], cell_ids[y + 1][x][j])
                    loop_edges.append(is_line.vertical[y, x])

    graph.active_edges_single_cycle(solver, loop_edges, aux_graph)

    direction = graph.BoolGridFrame(solver, height - 1, width - 1)
    up = is_line.vertical & direction.vertical
    down = is_line.vertical & ~direction.vertical
    left = is_line.horizontal & direction.horizontal
    right = is_line.horizontal & ~direction.horizontal

    line_size = solver.int_array((height, width), 0, height * width - 1)
    line_rank = solver.int_array((height, width), 0, height * width - 1)

    def add_constraint(src: tuple[int, int], dest: tuple[int, int], edge: BoolExpr):
        s = fire[src[0]][src[1]]
        d = fire[dest[0]][dest[1]]
        if not s and not d:
            solver.ensure(edge.then(
                (line_size[src] == line_size[dest]) & (line_rank[src] == line_rank[dest] + 1)
            ))
        elif not s and d:
            solver.ensure(edge.then(line_rank[src] == 0))
        elif s and not d:
            solver.ensure(edge.then(line_rank[dest] == line_size[dest]))

    for y in range(height):
        for x in range(width):
            if y > 0:
                add_constraint((y, x), (y - 1, x), up[y - 1, x])
            if y < height - 1:
                add_constraint((y, x), (y + 1, x), down[y, x])
            if x > 0:
                add_constraint((y, x), (y, x - 1), left[y, x - 1])
            if x < width - 1:
                add_constraint((y, x), (y, x + 1), right[y, x])

    for y in range(height):
        for x in range(width):
            if num[y][x] != _:
                solver.ensure(line_size[y, x] == num[y][x] - 1)

            inbound = []
            outbound = []
            if y > 0:
                inbound.append(is_line.vertical[y - 1, x] & ~direction.vertical[y - 1, x])
                outbound.append(up[y - 1, x])
            if y < height - 1:
                inbound.append(is_line.vertical[y, x] & direction.vertical[y, x])
                outbound.append(down[y, x])
            if x > 0:
                inbound.append(is_line.horizontal[y, x - 1] & ~direction.horizontal[y, x - 1])
                outbound.append(left[y, x - 1])
            if x < width - 1:
                inbound.append(is_line.horizontal[y, x] & direction.horizontal[y, x])
                outbound.append(right[y, x])

            solver.ensure(
                count_true(inbound) == count_true(outbound)
            )

    is_sat = solver.solve()
    return is_sat, is_line, fire_cell_mode


if __name__ == "__main__":
    fire = [
        [_, _, X, _, _, X],
        [_, X, X, _, _, _],
        [_, _, _, _, _, _],
        [_, _, _, _, _, _],
        [_, _, X, _, _, _],
    ]
    num = [
        [_, 1, _, _, _, _],
        [_, _, _, _, _, 8],
        [3, _, 6, _, _, _],
        [_, _, _, _, _, _],
        [_, _, _, _, _, _],
    ]

    is_sat, is_line, fire_mode = solve_firewalk(fire, num)
    if is_sat:
        print("Solution found:")
        print(stringify_grid_frame(is_line))
        print(stringify_array(fire_mode, {True: "\\", False: "/", None: "?"}))
    else:
        print("No solution exists.")
