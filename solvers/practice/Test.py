# －１以外の数字ｎ: 周囲ｎマスで線がまっすぐに伸びる

problem = [
    [-1, -1, -1, -1, 1],
    [-1, 4, -1, -1, -1],
    [-1, -1, -1, -1, -1],
    [-1, -1, -1, 1, -1],
    [0, -1, -1, -1, -1],
]
height = 5
width = 5

problem = [
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [ 1, -1, -1,  6, -1, -1,  4, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1,  2, -1, -1, -1,  0, -1, -1],
    [-1, -1,  2, -1, -1, -1, -1, -1],
    [-1, -1, -1,  2, -1, -1,  0, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
]
height = 8
width = 8

problemText = ""


from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_grid_frame

solver = Solver()
grid_frame = graph.BoolGridFrame(solver, height - 1, width - 1)
solver.add_answer_key(grid_frame)

is_passed = graph.active_edges_single_cycle(solver, grid_frame)


# 点y,xで線がまっすぐに伸びるbool
def is_straight(y, x):
    v = grid_frame.vertical[y - 1:y + 1, x]
    h = grid_frame.horizontal[y, x - 1:x + 1]
    return (count_true(v) == 2) ^ (count_true(h) == 2)


for y in range(height):
    for x in range(width):
        if problem[y][x] != -1:
            solver.ensure(is_passed[y, x] == False)
            cells = [(y + dy, x + dx)
                     for dy in range(-1, 2)
                     for dx in range(-1, 2)
                     if 0 <= y + dy < height and 0 <= x + dx < width]
            solver.ensure(count_true([is_straight(y, x) for y, x in cells]) == problem[y][x])

has_answer = solver.solve()
print(has_answer)

if has_answer:
    ans = stringify_grid_frame(grid_frame)
    output_lines = [' '.join(line) for line in ans.split('\n')]
    output_text = '\n'.join(output_lines)
    print(output_text)
