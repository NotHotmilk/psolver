import cspuz.array
from cspuz import Solver
from cspuz.constraints import cond, then, count_true, fold_and, fold_or
from cspuz.puzzle.util import stringify_array
from colorist import Effect, Color, BgColor
import inspect


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
    # problem, key_y, key_x = problem_tuple
    #
    # print('  ', end=' ')
    # for x in range(len(problem[0])):
    #     print(f"{Effect.UNDERLINE}{key_x[x]:2d}{Effect.OFF}", end=' ')
    #
    # print()
    #
    # for y in range(len(problem)):
    #     print(f"{Effect.UNDERLINE}{key_y[y]:2d}{Effect.OFF}", end=' ')
    #
    #     for x in range(len(problem[0])):
    #         if ans[y, x].sol is None:
    #             print(f"{BgColor.RED}{problem[y][x]:2d}{BgColor.OFF}", end=' ')
    #         elif ans[y, x].sol:
    #             print(f"{Effect.REVERSE}{problem[y][x]:2d}{Effect.OFF}", end=' ')
    #         else:
    #             print(f"{problem[y][x]:2d}", end=' ')
    #     print()
    problem, key_y, key_x = problem_tuple

    print('  ', end=' ')
    for x in range(len(problem[0])):
        print(f"{Effect.UNDERLINE}{key_x[x]:2d}{Effect.OFF}", end=' ')

    print()

    for y in range(len(problem)):
        print(f"{Effect.UNDERLINE}{key_y[y]:2d}{Effect.OFF}", end=' ')

        for x in range(len(problem[0])):
            p = f"{problem[y][x]:2d}"
            if ans[y, x].sol is None:
                p = "?" + p[1:]
                print(f"{BgColor.RED}{p}{BgColor.OFF}", end=' ')
            elif ans[y, x].sol:
                p = "#" + p[1:]
                print(f"{Effect.REVERSE}{p}{Effect.OFF}", end=' ')
            else:
                p = "." + p[1:]
                print(f"{p}", end=' ')
        print()


# 通常ソルバー部分終了
# ここからはレベル計算部分

def print_func(str: str):
    frame = inspect.currentframe()
    caller_name = frame.f_back.f_code.co_name
    #print(str + f" - {caller_name}")


def create_temp_solver(is_black):
    height, width = is_black.shape

    temp_solver = Solver()
    temp_is_black = temp_solver.bool_array((height, width))
    temp_solver.add_answer_key(temp_is_black)

    # 既に確定しているマスについてはその値をコピー
    for y in range(height):
        for x in range(width):
            if is_black[y, x].sol is not None:
                temp_solver.ensure(temp_is_black[y, x] == is_black[y, x].sol)

    return temp_solver, temp_is_black


def temp_solve(base_solver, base_is_black, temp_solver: Solver, temp_is_black, before_sol_num):
    height, width = base_is_black.shape

    # 一時的に増えた制約を追加して解きなおす
    temp_solver.solve()

    # 解きなおした結果を反映
    for y in range(height):
        for x in range(width):
            if base_is_black[y, x].sol is None and temp_is_black[y, x].sol is not None:
                base_solver.ensure(base_is_black[y, x] == temp_is_black[y, x].sol)
                base_solver.solve()

    after_sol_num = get_sol_num(base_is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def get_sol_num(is_black: cspuz.array.BoolArray2D):
    height, width = is_black.shape

    count = 0
    for y in range(height):
        for x in range(width):
            if is_black[y, x].sol is not None:
                count += 1

    return count


def partition_cells_in_line(is_black, problem, is_row, index):
    height, width = is_black.shape

    black_cells = []
    white_cells = []
    unknown_cells = []
    unknown_is_black = []

    for i in range(width):
        if is_row:
            y, x = index, i
        else:
            y, x = i, index

        if is_black[y, x].sol is None:
            unknown_cells.append(problem[y][x])
            unknown_is_black.append(is_black[y, x])
        elif is_black[y, x].sol:
            black_cells.append(problem[y][x])
        else:
            white_cells.append(problem[y][x])

    return black_cells, white_cells, unknown_cells, unknown_is_black


def カギが０なので全部黒(solver: Solver, is_black, problem, key_y, key_x):
    height, width = is_black.shape

    before_sol_num = get_sol_num(is_black)

    for y in range(height):
        if key_y[y] == 0:
            print_func(f"上から{y + 1}行目")
            solver.ensure(fold_and(is_black[y, :]))
    for x in range(width):
        if key_x[x] == 0:
            print_func(f"左から{x + 1}列目")
            solver.ensure(fold_and(is_black[:, x]))

    solver.solve()

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def カギが最大なので全部白(solver: Solver, is_black, problem, key_y, key_x):
    height, width = is_black.shape

    before_sol_num = get_sol_num(is_black)

    for y in range(height):
        if key_y[y] == sum(problem[y]):
            print_func(f"上から{y + 1}行目")
            solver.ensure(~fold_or(is_black[y, :]))
    for x in range(width):
        if key_x[x] == sum(problem[y][x] for y in range(height)):
            print_func(f"左から{x + 1}列目")
            solver.ensure(~fold_or(is_black[:, x]))

    solver.solve()

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def カギの数値を超えているので黒(solver: Solver, is_black, problem, key_y, key_x):
    height, width = is_black.shape

    before_sol_num = get_sol_num(is_black)

    for y in range(height):
        for x in range(width):
            if is_black[y, x].sol is not None:
                continue
            if problem[y][x] > key_y[y] or problem[y][x] > key_x[x]:
                print_func(f"上から{y + 1}, 左から{x + 1}")
                solver.ensure(is_black[y, x])

    solver.solve()

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def 残り全部黒または白(solver: Solver, is_black, problem, key_y, key_x):
    before_sol_num = get_sol_num(is_black)

    height, width = is_black.shape

    for y in range(height):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, True, y)

        if not unknown_cells:
            continue

        temp_solver, temp_is_black = create_temp_solver(is_black)

        if key_y[y] - sum(w_cells) == sum(unknown_cells):
            temp_solver.ensure(~fold_or(unknown_is_black))
        if key_y[y] - sum(w_cells) == 0:
            temp_solver.ensure(fold_and(unknown_is_black))

        if temp_solve(solver, is_black, temp_solver, temp_is_black, before_sol_num):
            print_func(f"上から{y + 1}行目")
            return True

    for x in range(width):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, False, x)

        if not unknown_cells:
            continue

        temp_solver, temp_is_black = create_temp_solver(is_black)

        if key_x[x] - sum(w_cells) == sum(unknown_cells):
            temp_solver.ensure(~fold_or(unknown_is_black))
        if key_x[x] - sum(w_cells) == 0:
            temp_solver.ensure(fold_and(unknown_is_black))

        if temp_solve(solver, is_black, temp_solver, temp_is_black, before_sol_num):
            print_func(f"左から{x + 1}列目")
            return True

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def 白にするとオーバーするので黒(solver: Solver, is_black, problem, key_y, key_x):
    height, width = is_black.shape

    before_sol_num = get_sol_num(is_black)

    for y in range(height):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, True, y)

        if not unknown_cells:
            continue

        remain = key_y[y] - sum(w_cells)
        for i in range(len(unknown_cells)):
            if remain < unknown_cells[i]:
                solver.ensure(unknown_is_black[i])
                solver.solve()
                print_func(f"上から{y + 1}行目")
                return True

    for x in range(width):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, False, x)

        if not unknown_cells:
            continue

        remain = key_x[x] - sum(w_cells)
        for i in range(len(unknown_cells)):
            if remain < unknown_cells[i]:
                solver.ensure(unknown_is_black[i])
                solver.solve()
                print_func(f"左から{x + 1}列目")
                return True

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def 黒にすると不足するので白(solver: Solver, is_black, problem, key_y, key_x):
    height, width = is_black.shape

    before_sol_num = get_sol_num(is_black)

    for y in range(height):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, True, y)

        if not unknown_cells:
            continue

        remain = key_y[y] - sum(w_cells)
        for i in range(len(unknown_cells)):
            if remain > sum(unknown_cells) - unknown_cells[i]:
                solver.ensure(~unknown_is_black[i])
                solver.solve()
                print_func(f"上から{y + 1}行目")
                return True

    for x in range(width):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, False, x)

        if not unknown_cells:
            continue

        remain = key_x[x] - sum(w_cells)
        for i in range(len(unknown_cells)):
            if remain > sum(unknown_cells) - unknown_cells[i]:
                solver.ensure(~unknown_is_black[i])
                solver.solve()
                print_func(f"左から{x + 1}列目")
                return True

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def 残りn個のマス(solver: Solver, is_black, problem, key_y, key_x, n):
    height, width = is_black.shape

    before_sol_num = get_sol_num(is_black)

    for y in range(height):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, True, y)

        if not unknown_cells:
            continue

        if len(unknown_cells) == n:
            temp_solver, temp_is_black = create_temp_solver(is_black)
            temp_solver.ensure(sum(temp_is_black[y, x].cond(0, problem[y][x]) for x in range(width)) == key_y[y])
            if temp_solve(solver, is_black, temp_solver, temp_is_black, before_sol_num):
                print_func(f"上から{y + 1}行目の{n}マス")
                return True

    for x in range(width):
        b_cells, w_cells, unknown_cells, unknown_is_black = partition_cells_in_line(is_black, problem, False, x)

        if not unknown_cells:
            continue

        if len(unknown_cells) == n:
            temp_solver, temp_is_black = create_temp_solver(is_black)
            temp_solver.ensure(sum(temp_is_black[y, x].cond(0, problem[y][x]) for y in range(height)) == key_x[x])
            if temp_solve(solver, is_black, temp_solver, temp_is_black, before_sol_num):
                print_func(f"左から{x + 1}列目の{n}マス")
                return True

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)
    return has_changed


def 各列を完全に走査(solver: Solver, is_black, problem, key_y, key_x):
    height = len(problem)
    width = len(problem[0])

    before_sol_num = get_sol_num(is_black)

    # 行ごとに解く
    for y in range(height):
        temp_solver, temp_is_black = create_temp_solver(is_black)
        temp_solver.ensure(sum(temp_is_black[y, x].cond(0, problem[y][x]) for x in range(width)) == key_y[y])
        temp_solve(solver, is_black, temp_solver, temp_is_black, -1)

    # 列ごとに解く
    for x in range(width):
        temp_solver, temp_is_black = create_temp_solver(is_black)
        temp_solver.ensure(sum(temp_is_black[y, x].cond(0, problem[y][x]) for y in range(height)) == key_x[x])
        temp_solve(solver, is_black, temp_solver, temp_is_black, -1)

    # print("途中経過")
    # print_nuri_p((problem, key_y, key_x), is_black)
    # print()

    after_sol_num = get_sol_num(is_black)
    has_changed = (before_sol_num < after_sol_num)

    return has_changed


def calculate_level(problem_tuple: tuple[list[list[int]], list[int], list[int]], verbose=False):
    level = 0

    problem, key_y, key_x = problem_tuple

    height = len(problem)
    width = len(problem[0])

    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    print()
    # 最初に消せるマスを消す　その後は消せるマスがなくなるまで繰り返す
    カギが０なので全部黒(solver, is_black, *problem_tuple)
    カギが最大なので全部白(solver, is_black, *problem_tuple)
    カギの数値を超えているので黒(solver, is_black, *problem_tuple)

    while True:
        if verbose:
            print_nuri_p(problem_tuple, is_black)
            print()


        if get_sol_num(is_black) == height * width:
            break

        if 残りn個のマス(solver, is_black, *problem_tuple, 1):
            level = max(level, 0)
            continue
        if 残り全部黒または白(solver, is_black, *problem_tuple):
            level = max(level, 1)
            continue
        if 残りn個のマス(solver, is_black, *problem_tuple, 2):
            level = max(level, 1)
            continue
        if 白にするとオーバーするので黒(solver, is_black, *problem_tuple):
            level = max(level, 2)
            continue
        if 残りn個のマス(solver, is_black, *problem_tuple, 3):
            level = max(level, 3)
            continue
        if 黒にすると不足するので白(solver, is_black, *problem_tuple):
            level = max(level, 3)
            continue
        if 残りn個のマス(solver, is_black, *problem_tuple, 4):
            level = max(level, 4)
            continue
        if 残りn個のマス(solver, is_black, *problem_tuple, 5):
            level += max(level + 1, 5)
            continue
        if 残りn個のマス(solver, is_black, *problem_tuple, 6):
            level += max(level + 2, 6)
            continue

        各列を完全に走査(solver, is_black, *problem_tuple)
        level = f"{level}+"
        break

    return level


if __name__ == '__main__':
    filename = '/home/notmilk/PycharmProjects/psolver/solvers/puzzles/rule base solver/NuriPProblems.txt'
    problems = read_problems(filename)

    for i in range(len(problems)):
        print(f'Problem {i}:')
        ans = solve_nuri_p(problems[i])
        print_nuri_p(problems[i], ans)
        print(f'Level: {calculate_level(problems[i], verbose=False)}')
        print()
