problemText = ("Sukon/5/5"
               "/-1_-1.-1_ 1.-1_-1.-1_-1.-1_-1"
               "/-1_ 1.-1_ 3.-1_-1.-1_-1.-1_-1"
               "/-1_-1.-1_-1.-1_-1.-1_-1.-1_-1"
               "/-1_-1.-1_-1.-1_-1. 6_-1. 8_-1"
               "/-1_-1.-1_-1.-1_-1. 8_-1.-1_-1")
problemText = ("Sukon/4/4"
               "/-1_-1.-1_ 1.-1_-1.-1_-1"
               "/-1_ 1.-1_ 3.-1_-1.-1_-1"
               "/-1_ 6.-1_-1.-1_-1.-1_-1"
               "/-1_-1.-1_-1. 4_-1.-1_-1")

problemText = problemText.strip().split("/")

# バリデーション
if problemText[0] != "Sukon":
    print("問題が正しく入力されていません。")
    exit()

# 問題のサイズ
height = int(problemText[1])
width = int(problemText[2])

# 上部問題と下部問題の初期化
upperProblem = [[0 for _ in range(width)] for _ in range(height)]
lowerProblem = [[0 for _ in range(width)] for _ in range(height)]

# 各マスのデータを解析して配列を構築
for i in range(height):
    row_data = problemText[3 + i].split(".")
    for j, cell_data in enumerate(row_data):
        upper_value, lower_value = map(int, cell_data.split("_"))
        upperProblem[i][j] = upper_value
        lowerProblem[i][j] = lower_value

from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, alldifferent
from cspuz.puzzle.util import stringify_grid_frame, stringify_array

solver = Solver()
upperCells = solver.int_array((height, width), 0, 2 * height - 1)
lowerCells = solver.int_array((height, width), 0, 2 * height - 1)
solver.add_answer_key(upperCells, lowerCells)

# 問題で指定されている数字を確定させる
for i in range(height):
    for j in range(width):
        if upperProblem[i][j] != -1:
            solver.ensure(upperCells[i, j] == upperProblem[i][j])
        if lowerProblem[i][j] != -1:
            solver.ensure(lowerCells[i, j] == lowerProblem[i][j])

# 各タテヨコ列に入る数字がすべて異なる
for i in range(height):
    solver.ensure(alldifferent(upperCells[i, :], lowerCells[i, :]))
for j in range(width):
    solver.ensure(alldifferent(upperCells[:, j], lowerCells[:, j]))

# 下の数字が上の数字より大きい
for i in range(height):
    for j in range(width):
        solver.ensure(upperCells[i, j] < lowerCells[i, j])

# 解く
has_answer = solver.solve()
print(has_answer)

# if has_answer:
#     symbol_map = {None: '?'}
#     symbol_map.update({i: str(i) for i in range(2 * height)})
#     # 上部のセルと下部のセルの文字列表現を取得
#     upper_cells_str = stringify_array(upperCells, symbol_map)
#     lower_cells_str = stringify_array(lowerCells, symbol_map)
#     print(upper_cells_str)
#     print()
#     print(lower_cells_str)

if has_answer:
    for i in range(height):
        for j in range(width):
            u = upperCells[i, j].sol if upperCells[i, j].sol is not None else "?"
            l = lowerCells[i, j].sol if lowerCells[i, j].sol is not None else "?"
            print(f"{u}/{l}", end=" ")
        print()