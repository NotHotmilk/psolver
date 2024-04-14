problem = [
    [-1,  0, -1, -1],
    [-1,  1, -1,  1],
    [-1, -1,  1, -1],
    [-1, -1, -1, -1],
]
problem = [
    [-1, -1, -1, -1, -1, -1],
    [-1, -1, -1,  1,  1, -1],
    [-1,  0,  1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1],
    [ 0, -1, -1, -1, -1, -1],
]
problem = [
    [ 1,  0,  1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1,  1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1],
]
problem = [
    [ 1,  0,  1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1],
    [-1,  1, -1, -1,  1, -1],
    [-1, -1,  1, -1, -1, -1],
    [-1,  1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1],
]

height = len(problem)
width = len(problem[0])

from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array

solver = Solver()
is_black = solver.bool_array((height, width))
solver.add_answer_key(is_black)

black_group_id, black_group_size = graph.connected_groups(solver, is_black)
white_group_id, white_group_size = graph.connected_groups(solver, ~is_black)
# solver.add_answer_key(black_group_id, black_group_size)
# solver.add_answer_key(white_group_id, white_group_size)


for y in range(height):
    for x in range(width):
        if problem[y][x] != -1:
            solver.ensure(is_black[y, x] == (problem[y][x] == 1))

# 黒マスは4マスになる
for y in range(height):
    for x in range(width):
        solver.ensure(then(is_black[y, x], black_group_size[y, x] == 4))


# # 00
# # 01 のパターンを許さない -> 白マスが長方形を形成する
# for y in range(height - 1):
#     for x in range(width - 1):
#         solver.ensure(count_true(is_black[y:y+2, x:x+2]) != 1)

# 白マスがひとつながり
graph.active_vertices_connected(solver, ~is_black)

# # 白マスが2x2にならない
# solver.ensure(
#     is_black[:-1, :-1] |
#     is_black[:-1, 1:] |
#     is_black[1:, :-1] |
#     is_black[1:, 1:]
# )


# # すべての行・列において、黒マスの数が同じ
# same_count = solver.int_var(0, max(height, width))
# # solver.ensure(same_count == 4)
# solver.add_answer_key(same_count)
# for y in range(height):
#     solver.ensure(count_true(is_black[y]) == same_count)
# for x in range(width):
#     solver.ensure(count_true(is_black[:, x]) == same_count)

# # 黒マスが連続しない
# graph.active_vertices_not_adjacent(solver, is_black)

has_answer = solver.solve()
print(has_answer)

if has_answer:
    print(stringify_array(is_black, {True: '#', False: '.', None: '?'}))
    print()
    print("group_id")
    for y in range(height):
        for x in range(width):
            print(black_group_id[y, x].sol or '.', end=' ')
        print()
    print()
    print(f"group_size")
    for y in range(height):
        for x in range(width):
            print(black_group_size[y, x].sol or '.', end=' ')
        print()