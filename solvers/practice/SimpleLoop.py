problemText = "SimpleLoop/4/4/0.0.0.0/0.1.1.0/0.0.0.0/0.0.0.0"
problemText = "SimpleLoop/5/5/0.0.0.0.0/0.0.0.0.0/0.1.1.0.0/0.0.0.0.0/1.0.0.0.0"
problemText = problemText.strip().split("/")

# バリデーション
if problemText[0] != "SimpleLoop":
    print("問題が正しく入力されていません。")
    exit()

# 問題のサイズ
height = int(problemText[1])
width = int(problemText[2])

# 問題のヒント
# .で区切って２次元int配列に変換
clues = [i.split(".") for i in problemText[3:]]
clues = [[int(j) for j in i] for i in clues]

# 解く
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_grid_frame

solver = Solver()
grid_frame = graph.BoolGridFrame(solver, height-1, width-1)
solver.add_answer_key(grid_frame)
is_passed = graph.active_edges_single_cycle(solver, grid_frame)

for y in range(height):
    for x in range(width):
        solver.ensure(is_passed[y, x] == (clues[y][x] == 0))

has_answer = solver.solve()
print(has_answer)

if has_answer:
    ans = stringify_grid_frame(grid_frame)
    output_lines = [' '.join(line) for line in ans.split('\n')]
    output_text = '\n'.join(output_lines)
    print(output_text)
