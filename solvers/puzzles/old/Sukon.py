import sys
from cspuz import Solver
from cspuz.constraints import alldifferent
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D


def solve_sukon(height, width, problem):
    """
    問題 problem は、サイズ (height, width*2) の2次元配列です。
    各行の前半 width 個が上部の数字、後半 width 個が下部の数字に対応します。
    問題指定値は -1 が未指定を表し、0～9 の値が手がかりとなります。
    """
    solver = Solver()
    # 上部・下部それぞれのセルの変数を作成（範囲は 0～9）
    upper_cells = solver.int_array((height, width), 0, 9)
    lower_cells = solver.int_array((height, width), 0, 9)
    solver.add_answer_key(upper_cells, lower_cells)

    # 問題で指定されている値を反映する。
    # problem[i][2*j] が上部、problem[i][2*j+1] が下部の数字を表す。
    for i in range(height):
        for j in range(width):
            clue_upper = problem[i][2 * j]
            clue_lower = problem[i][2 * j + 1]
            if clue_upper != -1:
                solver.ensure(upper_cells[i, j] == clue_upper)
            if clue_lower != -1:
                solver.ensure(lower_cells[i, j] == clue_lower)

    # 各マスで、下部の数字は上部より大きい
    for i in range(height):
        for j in range(width):
            solver.ensure(upper_cells[i, j] < lower_cells[i, j])

    # 各行について、上部・下部合わせた 2*width 個の数字がすべて異なる
    for i in range(height):
        # 各行の上部と下部の数字をリストにまとめる
        row_numbers = [upper_cells[i, j] for j in range(width)] + [lower_cells[i, j] for j in range(width)]
        solver.ensure(alldifferent(row_numbers))

    # 各列について、上部・下部合わせた 2*height 個の数字がすべて異なる
    for j in range(width):
        col_numbers = [upper_cells[i, j] for i in range(height)] + [lower_cells[i, j] for i in range(height)]
        solver.ensure(alldifferent(col_numbers))

    is_sat = solver.solve()
    return is_sat, upper_cells, lower_cells


def generate_sukon(height, width, symmetry=False, verbose=False, disallow_adjacent=False):
    """
    ArrayBuilder2D の盤面サイズは (height, width*2) です。
    各マスは 2 つの値を持ち、左側が上部、右側が下部に対応します。
    手がかりとして -1（未指定）または 0～9 の数字を与えます。
    """
    # 手がかりのペナルティ（与えすぎると解が唯一でなくなるためペナルティを与える）
    clue_penalty = lambda problem: count_non_default_values(problem, default=-1, weight=13)
    generated = generate_problem(
        lambda problem: solve_sukon(height, width, problem),
        builder_pattern=ArrayBuilder2D(
            height,
            width * 2,  # 各行に上部と下部の合計 2*width 個の値を配置する
            list(range(-1, 10)),  # -1 は未指定、0～9 が手がかりとして使える
            default=-1,
            symmetry=symmetry,
            disallow_adjacent=disallow_adjacent
        ),
        clue_penalty=clue_penalty,
        verbose=verbose,
    )
    return generated


if __name__ == "__main__":
    # 例として 5x5 盤面の数婚パズルを生成
    height, width = 5, 5
    # problem = generate_sukon(height, width, symmetry=False, verbose=True, disallow_adjacent=False)

    # 8/. 4/. 3/5 1/. ./.
    # ./. ./7 ./. 8/. ./.
    # ./. ./. 6/. ./5 8/.
    # ./. ./2 ./. ./. ./.
    # ./1 ./. ./. ./. 3/.

    problem = [
        [8, -1, 4, -1, 3, 5, 1, -1, -1, -1],
        [-1, -1, -1, 7, -1, -1, 4, -1, -1, -1],
        [-1, -1, -1, -1, 6, -1, -1, 5, 8, -1],
        [-1, -1, -1, 2, -1, -1, -1, -1, -1, -1],
        [-1, 1, -1, -1, -1, -1, -1, -1, 3, -1],
    ]

    if problem is None:
        print("生成に失敗しました。")
        sys.exit(1)
    # 問題を文字列で出力（-1 をドットとして表示）
    symbol_map = {-1: ".", **{i: str(i) for i in range(10)}}
    print("【手がかり盤面】")
    for i in range(height):
        row = []
        # 各行は [上部, 下部, 上部, 下部, ...] の順となっている
        for j in range(width):
            upper = problem[i][2 * j]
            lower = problem[i][2 * j + 1]
            row.append(f"{symbol_map[upper]}/{symbol_map[lower]}")
        print(" ".join(row))
    print("\n【解答】")
    sat, upper_cells, lower_cells = solve_sukon(height, width, problem)
    if sat:
        # 解の出力
        for i in range(height):
            row = []
            for j in range(width):
                u = upper_cells[i, j].sol if upper_cells[i, j].sol is not None else "_"
                l = lower_cells[i, j].sol if lower_cells[i, j].sol is not None else "_"
                row.append(f"{u}/{l}")
            print(" ".join(row))
    else:
        print("解が存在しません。")
