problemText = [
    [7, 9, 2, 0, 5, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 6, 0, 0, 0, 0],
    [9, 5, 0, 3, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 9, 0],
    [0, 0, 0, 0, 0, 2, 0, 1, 6],
    [0, 0, 0, 0, 4, 0, 0, 0, 2],
    [0, 0, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 2, 0, 5, 6, 0],
]

from cspuz import Solver

solver = Solver()
cells = [[solver.int_var(1, 9) for _ in range(9)] for _ in range(9)]

solver.add_answer_key(cells)

for y in range(9):
    for x in range(9):
        if problemText[y][x] != 0:
            solver.ensure(cells[y][x] == problemText[y][x])

for y in range(9):
    for x1 in range(9):
        for x2 in range(x1 + 1, 9):
            solver.ensure(cells[y][x1] != cells[y][x2])

for x in range(9):
    for y1 in range(9):
        for y2 in range(y1 + 1, 9):
            solver.ensure(cells[y1][x] != cells[y2][x])

for b in range(9):
    block_cells = []
    for i in range(9):
        block_cells.append(cells[b // 3 * 3 + i // 3][b % 3 * 3 + i % 3])

    for i in range(9):
        for j in range(i + 1, 9):
            solver.ensure(block_cells[i] != block_cells[j])

has_answer = solver.solve()

if has_answer:
    for y in range(9):
        for x in range(9):
            print(cells[y][x].sol or ".", end=" ")
        print()