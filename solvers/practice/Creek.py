problemText = "Creek/3/3/-1.-1.-1.-1/2.-1.3.-1/1.-1.-1.-1/-1.-1.-1.-1"
problemText = "Creek/4/4/-1.-1.-1.-1.-1/1.-1.3.-1.-1/-1.-1.-1.-1.-1/-1.3.2.3.-1/-1.-1.-1.-1.-1"
problemText = ("Creek+/5/5"
           "/-1.-1.-1.-1.-1.-1"
           "/-1.3.-1.-1.-1.-1"
           "/-1.-1.-1.-1.3.-1"
           "/-1.3.-1.-1.-1.-1"
           "/-1.-1.2.-1.-1.-1"
           "/0.-1.-1.-1.-1.-1")

problemText = problemText.strip().split("/")

# バリデーション
if problemText[0] != "Creek" and problemText[0] != "Creek+":
    print("問題が正しく入力されていません。")
    exit()
else:
    print(problemText[0])

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

for y in range(height + 1):
    for x in range(width + 1):
        if clues[y][x] == -1:
            continue
        solver.ensure(count_true(is_black[max(0, y - 1):min(y + 1, height), max(0, x - 1):min(x + 1, width)]) == clues[y][x])

graph.active_vertices_connected(solver, ~is_black)


# 黒マスが2x2になっていない
if problemText[0] == "Creek+":
    for y in range(height - 1):
        for x in range(width - 1):
            solver.ensure(~fold_and(is_black[y:(y + 2), x:(x + 2)]))

# 解く
has_answer = solver.solve()

print(has_answer)
if has_answer:
    print(stringify_array(is_black, {True: "#", False: ".", None: "?"}))

