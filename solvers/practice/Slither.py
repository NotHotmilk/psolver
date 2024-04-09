problemText = "Slither/3/3/-1.3.-1/-1.3.-1/-1.-1.2"
problemText = problemText.strip().split("/")

# バリデーション
if problemText[0] != "Slither":
    print("問題が正しく入力されていません。")
    exit()

# 問題のサイズ
height = int(problemText[1])
width = int(problemText[2])

# 問題のヒント
# .で区切って２次元int配列に変換
problem = [i.split(".") for i in problemText[3:]]
problem = [[int(j) for j in i] for i in problem]


from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or
from cspuz.puzzle.util import stringify_grid_frame


solver = Solver()
grid_frame = graph.BoolGridFrame(solver, height, width)
solver.add_answer_key(grid_frame)

graph.active_edges_single_cycle(solver, grid_frame)
solver.ensure(fold_or(grid_frame))

for y in range(height):
    for x in range(width):
        if problem[y][x] != -1:
            solver.ensure(count_true(grid_frame.cell_neighbors(y, x)) == problem[y][x])

has_answer = solver.solve()

if has_answer:
    print(stringify_grid_frame(grid_frame))
