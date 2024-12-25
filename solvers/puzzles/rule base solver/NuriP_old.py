from cspuz import Solver
from cspuz.puzzle.util import stringify_array
from colorist import Effect, Color, BgColor


def solve_nuri_p(problem_tuple: tuple[list[list[int]], list[int], list[int]]):
    problem, key_y, key_x = problem_tuple

    height = len(problem)
    width = len(problem[0])

    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    for y in range(height):
        solver.ensure(sum(is_black[y, x].cond(0, problem[y][x]) for x in range(width)) == key_y[y])
    for x in range(width):
        solver.ensure(sum(is_black[y, x].cond(0, problem[y][x]) for y in range(height)) == key_x[x])

    solver.solve()
    return is_black


def read_problems(filename):
    with open(filename, 'r') as file:
        # ファイル全体を読み込み、複数の空行があっても問題を区切れるようにする
        content = file.read().strip()
        # 複数の空行も含めて問題を区切るため、split('\n\n+')で空行以上を分割
        problem_blocks = [block for block in content.split('\n\n') if block.strip()]

    problems = []

    # 各問題ブロックを処理
    for block in problem_blocks:
        # 各ブロック内の行を取得してリスト化
        lines = block.strip().split('\n')
        matrix = [list(map(int, line.strip().split())) for line in lines]

        # key_x, key_y, problem に分割
        key_x = matrix[0]  # 最初の行が key_x
        key_y = [row[0] for row in matrix[1:]]  # 2行目以降の最初の列が key_y
        problem = [row[1:] for row in matrix[1:]]  # 2行目以降の残りの列が problem

        # (problem, key_y, key_x)のタプルをproblemsリストに追加
        problems.append((problem, key_y, key_x))

    return problems


def print_nuri_p(problem_tuple, ans):
    problem, key_y, key_x = problem_tuple

    print('  ', end=' ')
    for x in range(len(problem[0])):
        print(f"{Effect.UNDERLINE}{key_x[x]:2d}{Effect.OFF}", end=' ')

    print()

    for y in range(len(problem)):
        print(f"{Effect.UNDERLINE}{key_y[y]:2d}{Effect.OFF}", end=' ')

        for x in range(len(problem[0])):
            if ans[y, x].sol is None:
                print(f"{BgColor.RED}{problem[y][x]:2d}{BgColor.OFF}", end=' ')
            elif ans[y, x].sol:
                print(f"{Effect.REVERSE}{problem[y][x]:2d}{Effect.OFF}", end=' ')
            else:
                print(f"{problem[y][x]:2d}", end=' ')
        print()

# 通常ソルバー部分終了
# ここからはレベル計算部分

def create_temp_solver_with_no_memory(problem):
    height = len(problem)
    width = len(problem[0])

    temp_solver = Solver()
    temp_is_black = temp_solver.bool_array((height, width))
    temp_solver.add_answer_key(temp_is_black)

    return temp_solver, temp_is_black

def create_temp_solver(is_black, problem):

    height = len(problem)
    width = len(problem[0])

    temp_solver = Solver()
    temp_is_black = temp_solver.bool_array((height, width))
    temp_solver.add_answer_key(temp_is_black)

    # 既に確定しているマスについてはその値をコピー
    for y in range(height):
        for x in range(width):
            if is_black[y, x].sol is not None:
                temp_solver.ensure(temp_is_black[y, x] == is_black[y, x].sol)

    return temp_solver, temp_is_black


def temp_solve(base_solver, base_is_black, temp_solver: Solver, temp_is_black, problem, new_constraints):
    level = 0

    height = len(problem)
    width = len(problem[0])

    # 一時的に増えた制約を追加して解きなおす
    temp_solver.ensure(new_constraints)
    temp_solver.solve()

    # 解きなおした結果を反映
    for y in range(height):
        for x in range(width):
            if temp_is_black[y, x].sol is not None:
                base_solver.ensure(base_is_black[y, x] == temp_is_black[y, x].sol)
                base_solver.solve()

    return


def one_line_with_no_memory(solver: Solver, is_black, problem, key_y, key_x) -> bool:
    height = len(problem)
    width = len(problem[0])

    # 行ごとに解く
    for y in range(height):
        temp_solver, temp_is_black = create_temp_solver_with_no_memory(problem)
        row_constraints = []
        row_constraints.append(sum(temp_is_black[y, x].cond(0, problem[y][x]) for x in range(width)) == key_y[y])
        temp_solve(solver, is_black, temp_solver, temp_is_black, problem, row_constraints)

    # 列ごとに解く
    for x in range(width):
        temp_solver, temp_is_black = create_temp_solver_with_no_memory(problem)
        col_constraints = []
        col_constraints.append(sum(temp_is_black[y, x].cond(0, problem[y][x]) for y in range(height)) == key_x[x])
        temp_solve(solver, is_black, temp_solver, temp_is_black, problem, col_constraints)

    solver.solve()


    for y in range(height):
        for x in range(width):
            if is_black[y, x].sol is None:
                return False

    return True



def one_line(solver: Solver, is_black, problem, key_y, key_x):
    height = len(problem)
    width = len(problem[0])

    count_ans_sol_num = 0
    for y in range(height):
        for x in range(width):
            if is_black[y, x].sol is not None:
                count_ans_sol_num += 1

    # 行ごとに解く
    for y in range(height):
        temp_solver, temp_is_black = create_temp_solver(is_black, problem)
        row_constraints = []
        row_constraints.append(sum(temp_is_black[y, x].cond(0, problem[y][x]) for x in range(width)) == key_y[y])
        temp_solve(solver, is_black, temp_solver, temp_is_black, problem, row_constraints)

    # 列ごとに解く
    for x in range(width):
        temp_solver, temp_is_black = create_temp_solver(is_black, problem)
        col_constraints = []
        col_constraints.append(sum(temp_is_black[y, x].cond(0, problem[y][x]) for y in range(height)) == key_x[x])
        temp_solve(solver, is_black, temp_solver, temp_is_black, problem, col_constraints)

    solver.solve()
    # print("途中経過")
    # print_nuri_p((problem, key_y, key_x), is_black)
    # print()

    count_ans_sol_num_after = 0
    for y in range(height):
        for x in range(width):
            if is_black[y, x].sol is not None:
                count_ans_sol_num_after += 1

    has_changed = (count_ans_sol_num_after > count_ans_sol_num)
    return has_changed


def calculate_level(problem_tuple: tuple[list[list[int]], list[int], list[int]]):

    level = 0

    problem, key_y, key_x = problem_tuple

    height = len(problem)
    width = len(problem[0])

    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    if one_line_with_no_memory(solver, is_black, *problem_tuple):
        # 解けるなら
        return 1

    level += 1
    while one_line(solver, is_black, *problem_tuple):
        level += 1

    return level


if __name__ == '__main__':
    filename = '/home/notmilk/PycharmProjects/psolver/solvers/puzzles/rule base solver/NuriPProblems.txt'
    problems = read_problems(filename)

    for i in range(len(problems)):
        print(f'Problem {i}:')
        ans = solve_nuri_p(problems[i])
        print_nuri_p(problems[i], ans)
        print(f'Level: {calculate_level(problems[i])}')
        print()


