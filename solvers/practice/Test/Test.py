problem = [
    [-1, -1, -1, -1],
    [-1, -1, -1, -1],
    [-1, -1, -1, -1],
    [-1, -1, -1, -1],
]
height = 4
width = 4

from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_grid_frame

solver = Solver()
grid_frame = graph.BoolGridFrame(solver, height, width)
solver.add_answer_key(grid_frame)

is_passed = graph.active_vertices_connected(solver, grid_frame)

for y in range(height):
    for x in range(width):
        if problem[y][x] != -1:
            solver.ensure(count_true(grid_frame.cell_neighbors(y, x)) == problem[y][x])



has_answer = solver.solve()
print(has_answer)

if has_answer:
    ans = stringify_grid_frame(grid_frame)
    output_lines = [' '.join(line) for line in ans.split('\n')]
    output_text = '\n'.join(output_lines)
    print(output_text)