import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

solver = Solver()
height, width = 21, 21
kind = solver.int_array((height, width), 0, 3)
solver.add_answer_key(kind)
grid_frame = graph.BoolGridFrame(solver, height - 1, width - 1)
is_passed = graph.active_edges_single_cycle(solver, grid_frame)
solver.add_answer_key(grid_frame)

solver.ensure(is_passed == (kind == 0))

graph.active_vertices_not_adjacent(solver, kind == 1)

misaki = [
    [0] * width for _ in range(height)
]

m = [(2, 6), (4, 12), (4, 16), (5, 2), (6, 9), (8, 12), (8, 16),
     (12, 4), (12, 8), (14, 11), (15, 18), (16, 4), (16, 8)]
y = [(1, 1), (1, 11), (1, 14), (2, 4),
     (4, 6), (6, 19), (7, 1), (10, 19),
     (11, 11), (12, 16), (14, 1), (16, 14),
     (18, 2), (18, 17), (19, 6), (20, 9)]

for my, mx in m:
    misaki[my][mx] = 2

for yy, yx in y:
    misaki[yy][yx] = 3

for y in range(height):
    for x in range(width):
        solver.ensure((misaki[y][x] == 2) == (kind[y, x] == 2))
        solver.ensure((misaki[y][x] == 3) == (kind[y, x] == 3))
        if misaki[y][x] == 2:
            solver.ensure(count_true(kind.four_neighbors(y, x) == 1) == 3)

solver.ensure(count_true(kind[0:7, 0:8] == 1) == 14)
solver.ensure(count_true(kind[7:14, 8:13] == 1) == 8)
solver.ensure(count_true(kind[7:14, 13:21] == 1) == 12)
solver.ensure(count_true(kind[14:21, 8:13] == 1) == 10)


solver.ensure(count_true(kind[1, 1:] == 1) == 6)
solver.ensure(count_true(kind[1:, 11] == 1) == 5)
solver.ensure(count_true(kind[1:, 14] == 1) == 5)
solver.ensure(count_true(kind[2:, 4] == 1) == 6)

solver.ensure(count_true(kind[4, 6:] == 1) == 5)
solver.ensure(count_true(kind[6, :19] == 1) == 3)
solver.ensure(count_true(kind[:7, 1] == 1) == 1)
solver.ensure(count_true(kind[10, :19] == 1) == 5)

solver.ensure(count_true(kind[11, 11:] == 1) == 2)
solver.ensure(count_true(kind[12:, 16] == 1) == 1)
solver.ensure(count_true(kind[14, 1:] == 1) == 5)
solver.ensure(count_true(kind[16, :14] == 1) == 4)

solver.ensure(count_true(kind[:18, 2] == 1) == 4)
solver.ensure(count_true(kind[:18, 17] == 1) == 4)
solver.ensure(count_true(kind[:19, 6] == 1) == 5)
solver.ensure(count_true(kind[20, 9:] == 1) == 3)




for y in range(height):
    solver.ensure(fold_or(kind[y, 8-1:13+1] == 1))
for x in range(width):
    solver.ensure(fold_or(kind[7-1:14+1, x] == 1))

solver.solve()
print(stringify_array(kind, common_rules.NUM_MAP))
print()
print()
print(stringify_grid_frame(grid_frame))
