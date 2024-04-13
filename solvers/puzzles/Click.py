problem = [
    [-1, -1, -1, -1,  1, -1, -1],
    [-1,  2, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1,  1, -1, -1,  1],
    [-1, -1, -1, -1, -1, -1, -1],
    [-1,  2, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1,  0],
]
height = 6
width = 6

problem = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1,  1, -1, -1, -1, -1, -1,  1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1,  2, -1, -1, -1, -1],
    [-1,  2, -1, -1, -1, -1,  3, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1,  1, -1, -1, -1, -1, -1,  1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
]
height = 8
width = 8


from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_array, stringify_grid_frame

solver = Solver()
is_black = solver.bool_array((height, width))
solver.add_answer_key(is_black)

# 問題の条件を追加
for y in range(height+1):
    for x in range(width+1):
        if problem[y][x] != -1:
            solver.ensure(
                count_true(
                    is_black[max(0, y - 1):min(y + 1, height), max(0, x - 1):min(x + 1, width)]
                )
                == problem[y][x])

# # 白マスが連結している
# graph.active_vertices_connected(solver, ~is_black)

# 黒マスが連結している
graph.active_vertices_connected(solver, is_black)

# # 黒マスが 2x2 になっていない
# solver.ensure(~(is_black[:-1, :-1] & is_black[:-1, 1:] & is_black[1:, :-1] & is_black[1:, 1:]))
#
# # 白マスが 2x2 になっていない
# solver.ensure((is_black[:-1, :-1] | is_black[:-1, 1:] | is_black[1:, :-1] | is_black[1:, 1:]))

# すべての行・列において、黒マスの数が同じ
same_count = solver.int_var(0, max(height, width))
solver.add_answer_key(same_count)

for y in range(height):
    solver.ensure(count_true(is_black[y, :]) == same_count)
for x in range(width):
    solver.ensure(count_true(is_black[:, x]) == same_count)

has_answer = solver.solve()
print(has_answer)

if has_answer:
    print(stringify_array(is_black, {True: "#", False: ".", None: "?"}))
    print(same_count.sol)