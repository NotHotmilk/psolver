import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.expr import BoolExpr
from cspuz.problem_serializer import serialize_problem_as_url, MultiDigit
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D


# water
_ = False
X = True



def solve_waterwalk(water: list[list[bool]], num: list[list[any]]):
    height = len(water)
    width = len(water[0])

    solver = Solver()
    is_line = graph.BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(is_line)

    is_passed = graph.active_edges_single_cycle(solver, is_line)

    for y in range(height):
        for x in range(width):
            if num[y][x] != _:
                solver.ensure(is_passed[y, x])

    direction = graph.BoolGridFrame(solver, height - 1, width - 1)
    up = is_line.vertical & direction.vertical
    down = is_line.vertical & ~direction.vertical
    left = is_line.horizontal & direction.horizontal
    right = is_line.horizontal & ~direction.horizontal

    line_size = solver.int_array((height, width), 0, height * width - 1)
    line_rank = solver.int_array((height, width), 0, height * width - 1)


    def add_constraint(src: tuple[int, int], dest: tuple[int, int], edge: BoolExpr):
        s = water[src[0]][src[1]]
        d = water[dest[0]][dest[1]]
        if not s and not d:
            solver.ensure(edge.then(
                (line_size[src] == line_size[dest]) & (line_rank[src] == line_rank[dest] + 1)
            ))
        elif not s and d:
            solver.ensure(edge.then(line_rank[src] == 0))
            solver.ensure(edge.then(line_rank[dest] == line_size[dest]))
        elif s and not d:
            solver.ensure(edge.then(line_rank[dest] == line_size[dest]))
            solver.ensure(edge.then(line_rank[src] == 0))
        else:
            solver.ensure(edge.then(
                (line_size[src] == line_size[dest]) & (line_rank[src] == line_rank[dest] + 1)
            ))

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
            if water[y][x]:
                solver.ensure(line_size[y, x] <= 1)
            
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

    return is_sat, is_line

from cspuz.problem_serializer import (
    Grid,
    OneOf,
    Spaces,
    HexInt,
    DecInt,
    Dict,
    Tupl,
    serialize_problem_as_url,
    deserialize_problem_as_url,
)


if __name__ == "__main__":
    water = [
        [_, _, _, _, _, _],
        [_, _, X, X, X, X],
        [X, X, X, X, X, X],
        [X, X, X, X, X, X],
        [_, _, _, _, _, _],
        [_, _, _, _, _, _],
    ]
    num = [
        [_, _, _, 5, _, _],
        [_, _, _, _, _, _],
        [_, _, _, _, _, _],
        [_, _, _, _, _, _],
        [_, _, _, _, 2, _],
        [_, _, _, _, _, _],
    ]
    
    is_sat, is_line = solve_waterwalk(water, num)
    if is_sat:
        print("Solution found:")
        print(stringify_grid_frame(is_line))
    else:
        print("No solution exists.")