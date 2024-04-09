problemText = "Nurikabe/4/4/-1.-1.1.-1/-1.3.-1.-1/-1.-1.-1.-1/-1.-1.-1.-1"
problemText = "Nurikabe/6/6/-1.-1.-1.-1.-1.-1/-1.4.-1.3.-1.-1/-1.-1.5.-1.-1.-1/3.-1.-1.-1.-1.-1/-1.-1.-1.-1.-1.-1/-1.-1.-1.-1.-1.-1"
problemText = problemText.strip().split("/")

# バリデーション
if problemText[0] != "Nurikabe":
    print("問題が正しく入力されていません。")
    exit()

# 問題のサイズ
height = int(problemText[1])
width = int(problemText[2])

# 問題のヒント
# .で区切って２次元int配列に変換
clues = [i.split(".") for i in problemText[3:]]
clues = [[int(j) for j in i] for i in clues]

from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_array


solver = Solver()

is_black = solver.bool_array((height, width))
solver.add_answer_key(is_black)

# 黒マスがひとつながり
graph.active_vertices_connected(solver, is_black)
# 黒マスが2x2になっていない
solver.ensure(~fold_and(
    is_black[:-1, :-1] &
    is_black[:-1, 1:] &
    is_black[1:, :-1] &
    is_black[1:, 1:]))

# 補助変数 block_id を用意
regions = []
for y in range(height):
    for x in range(width):
        if clues[y][x] != -1:
            regions.append((y, x, clues[y][x]))

block_id = solver.int_array((height, width), 0, len(regions))

# block_id == len(regions) なマスと黒マスは一致する
solver.ensure((block_id == len(regions)) == is_black)


for i, (y, x, n) in enumerate(regions):
    solver.ensure(block_id[y, x] == i)
    solver.ensure(count_true(block_id == i) == n)
    graph.active_vertices_connected(solver, block_id == i)

# 隣り合う白マスはblock_idが同じ
solver.ensure((~is_black[:-1, :] & ~is_black[1:, :]).then(block_id[:-1, :] == block_id[1:, :]))
solver.ensure((~is_black[:, :-1] & ~is_black[:, 1:]).then(block_id[:, :-1] == block_id[:, 1:]))

# 解く
has_answer = solver.solve()

print(has_answer)
if has_answer:
    print(stringify_array(is_black, {True: "#", False: ".", None: "?"}))