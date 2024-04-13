problemText = ("AroundMaze/4/4/^1/v3" # 入口と出口の位置
               "/-1.-1.-1.-1. 0"
               "/-1. 2.-1.-1.-1"
               "/-1.-1.-1.-1.-1"
               "/-1. 1.-1. 2.-1"
               "/-1.-1.-1.-1.-1")

problemText = problemText.strip().split("/")

# バリデーション
if problemText[0] != "AroundMaze":
    print("問題が正しく入力されていません。")
    exit()

# 問題のサイズ
height = int(problemText[1])
width = int(problemText[2])

# 入口と出口の位置
DIR_MAP = {"<": 1, ">": 2, "^": 3, "v": 4}
entranceDir = DIR_MAP[problemText[3][0]]
entrancePos = int(problemText[3][1:])
exitDir = DIR_MAP[problemText[4][0]]
exitPos = int(problemText[4][1:])

print(entranceDir, entrancePos, exitDir, exitPos)

# 問題のヒント
# .で区切って２次元int配列に変換
problem = [i.split(".") for i in problemText[5:]]
problem = [[int(j) for j in i] for i in problem]

from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_grid_frame


solver = Solver()
# grid_frame = graph.BoolGridFrame(solver, height, width)
# solver.add_answer_key(grid_frame)
#
# is_passed = graph.active_edges_acyclic(solver, grid_frame, entrancePos)



has_answer = solver.solve()
print(has_answer)

if has_answer:
    ans = stringify_grid_frame(grid_frame)
    output_lines = [' '.join(line) for line in ans.split('\n')]
    output_text = '\n'.join(output_lines)
    print(output_text)

