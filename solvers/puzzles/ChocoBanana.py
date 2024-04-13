problem = [
    [1, 0, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [0, 1, 0, 0],
]
problem = [
    [ 1,  0, -1, -1],
    [-1, -1,  1, -1],
    [ 0, -1, -1,  1],
    [-1,  1,  1, -1],
]

height = 4
width = 4

from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_array, stringify_grid_frame

solver = Solver()
is_black = solver.bool_array((height, width))
solver.add_answer_key(is_black)

# 問題の条件を追加
for y in range(height):
    for x in range(width):
        if problem[y][x] != -1:
            solver.ensure(is_black[y, x] == (problem[y][x] == 1))

# # 白マスが連結している
# graph.active_vertices_connected(solver, ~is_black)

# # 黒マスが連結している
# graph.active_vertices_connected(solver, is_black)

# # 黒マスが 2x2 になっていない
# solver.ensure(~(is_black[:-1, :-1] & is_black[:-1, 1:] & is_black[1:, :-1] & is_black[1:, 1:]))
#
# # 白マスが 2x2 になっていない
# solver.ensure((is_black[:-1, :-1] | is_black[:-1, 1:] | is_black[1:, :-1] | is_black[1:, 1:]))
#
# # すべての行・列において、黒マスの数が同じ
# same_count = solver.int_var(0,max(height, width))
#
# for y in range(height):
#     solver.ensure(count_true(is_black[y, :]) == same_count)
# for x in range(width):
#     solver.ensure(count_true(is_black[:, x]) == same_count)

# 11
# 10 のパターンを許さない -> 黒マスが長方形を形成する
for y in range(height - 1):
    for x in range(width - 1):
        solver.ensure(count_true(is_black[y:y+2, x:x+2]) != 3)

# 00
# 01 のパターンを許さない -> 黒マスが長方形を形成する
for y in range(height - 1):
    for x in range(width - 1):
        solver.ensure(count_true(is_black[y:y+2, x:x+2]) != 1)

has_answer = solver.solve()
print(has_answer)

if has_answer:
    print(stringify_array(is_black, {True: "#", False: ".", None: "?"}))