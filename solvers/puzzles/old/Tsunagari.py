size = [int(1 / 2 * i * (i + 1)) for i in range(20)]

problemText = ("Tsunagari/3/5"
               "/-1. 3.-1. 3.-1"
               "/ 4.-1. 2.-1.-1"
               "/-1.-1. 4.-1.-1")
problemText = ("Tsunagari/6/6"
               "/ 7. 2. 7.-1.-1. 8"
               "/-1.-1.-1.-1.-1.-1"
               "/-1.-1.-1.-1.-1.-1"
               "/ 5.-1. 3.-1.-1. 4"
               "/-1.-1.-1.-1.-1.-1"
               "/ 1.-1. 5.-1.-1. 8")
problemText = problemText.strip().split("/")

# 問題のサイズ
height = int(problemText[1])
width = int(problemText[2])

# バリデーション
if problemText[0] != "Tsunagari":
    print("問題が正しく入力されていません。")
    exit()
if int(height * width) not in size:
    print("問題のサイズが正しくありません。")
    exit()

# sizeの何番目か
size_index = size.index(int(height * width))
print(f"numbers: 1-{size_index}")

# 問題のヒント
# .で区切って２次元int配列に変換
problem = [i.split(".") for i in problemText[3:]]
problem = [[int(j) for j in i] for i in problem]

from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_array

solver = Solver()
grid = solver.int_array((height, width), 1, size_index)
solver.add_answer_key(grid)

for y in range(height):
    for x in range(width):
        if problem[y][x] != -1:
            solver.ensure(grid[y, x] == problem[y][x])

# iという数字は盤面にi個存在する
# 連結しているマスには同じ数字が書かれている
for i in range(size_index):
    solver.ensure(count_true(grid == i + 1) == i + 1)
    graph.active_vertices_connected(solver, grid == i + 1)

is_sat = solver.solve()
print(is_sat)

if is_sat:
    for i in range(height):
        for j in range(width):
            print(grid[i, j].sol if grid[i, j].sol is not None else "?", end=" ")
        print()
