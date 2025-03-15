import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, stringify_grid_frame_with_array2D
from cspuz.generator import generate_problem, ArrayBuilder2D
import common_rules

POS_CELL_CENTER = 0
POS_INTERSECTION = 1
POS_VERTICAL_EDGE = 2
POS_HORIZONTAL_EDGE = 3

SYM_VERTICAL = 1
SYM_SLASH = 2
SYM_HORIZONTAL = 3
SYM_BACKSLASH = 4

SYM_ANY = 5


def reflect_cell(pos_type, sym_type, base, cell):
    """
    pos_type: 位置の種類（CENTER, INTERSECTION, VERTICAL, HORIZONTAL）
    sym_type: 対称軸の種類
              1: 水平反転, 2: 垂直反転, 3: 斜め "/" の反転, 4: 斜め "\" の反転
    base: 対称軸の基準となる座標
    cell: 反転対象のセルの座標 (y, x)

    ※内部で全体を2倍して整数演算とし、最後に2で割って返します。
    ※エラーチェックは、反転後の座標が整数にならない場合にのみ ValueError を発生させます。
    """
    # まず cell 座標を2倍
    y, x = cell
    y *= 2
    x *= 2
    # pos_type に応じたオフセット（内部で2倍しているので、0.5 → 1）
    offset = {
        POS_CELL_CENTER: (0, 0),
        POS_INTERSECTION: (1, 1),
        POS_VERTICAL_EDGE: (0, 1),
        POS_HORIZONTAL_EDGE: (1, 0),
    }[pos_type]
    b_y, b_x = base
    # base も2倍してオフセットを加える
    b_y = b_y * 2 + offset[0]
    b_x = b_x * 2 + offset[1]

    # 対称軸ごとの反転
    if sym_type == SYM_HORIZONTAL:
        new_y = 2 * b_y - y
        new_x = x
    elif sym_type == SYM_VERTICAL:
        new_y = y
        new_x = 2 * b_x - x
    elif sym_type == SYM_SLASH:  # 斜め "/" の反転
        new_y = b_y - (x - b_x)
        new_x = b_x - (y - b_y)
    elif sym_type == SYM_BACKSLASH:  # 斜め "\" の反転
        new_y = b_y + (x - b_x)
        new_x = b_x + (y - b_y)
    else:
        raise ValueError("Invalid symmetry type.")

    # 反転後の座標が2で割り切れるかチェック（整数でない場合はエラー）
    if new_y % 2 != 0 or new_x % 2 != 0:
        raise ValueError("Symmetry reflection is not an integer.")

    return (new_y // 2, new_x // 2)


def check_inside(height, width, y, x):
    return 0 <= y < height and 0 <= x < width


def solve_sentai_show(height, width, problem):
    cellCenters, intersections, verticalEdges, horizontalEdges = problem

    # ナナメの線が辺の中点にある場合は解なし

    for i in range(len(verticalEdges)):
        for j in range(len(verticalEdges[i])):
            if (verticalEdges[i][j] == SYM_SLASH) | (verticalEdges[i][j] == SYM_BACKSLASH):
                return False, None, None

    for i in range(len(horizontalEdges)):
        for j in range(len(horizontalEdges[i])):
            if (horizontalEdges[i][j] == SYM_SLASH) | (horizontalEdges[i][j] == SYM_BACKSLASH):
                return False, None, None

    segments = []

    def add_problem(segments, array, pos_type):
        for i in range(len(array)):
            for j in range(len(array[i])):
                if array[i][j] != 0:
                    segments.append((pos_type, array[i][j], i, j))

    add_problem(segments, cellCenters, POS_CELL_CENTER)
    add_problem(segments, intersections, POS_INTERSECTION)
    add_problem(segments, verticalEdges, POS_VERTICAL_EDGE)
    add_problem(segments, horizontalEdges, POS_HORIZONTAL_EDGE)

    #  1: 水平 -
    #  2: 垂直 |
    #  3: 斜め /
    #  4: 斜め \

    region_count = len(segments)
    if region_count == 0:
        return False, None, None

    solver = Solver()
    region_id = solver.int_array((height, width), 0, region_count - 1)
    division = graph.BoolGridFrame(solver, height, width)

    solver.add_answer_key(region_id)
    solver.add_answer_key(division)

    for y in range(height - 1):
        for x in range(width):
            solver.ensure(division.horizontal[y + 1, x] == (region_id[y, x] != region_id[y + 1, x]))

    for y in range(height):
        for x in range(width - 1):
            solver.ensure(division.vertical[y, x + 1] == (region_id[y, x] != region_id[y, x + 1]))

    solver.ensure(division.vertical[:, 0] == True)
    solver.ensure(division.vertical[:, -1] == True)
    solver.ensure(division.horizontal[0, :] == True)
    solver.ensure(division.horizontal[-1, :] == True)

    for i in range(region_count):
        graph.active_vertices_connected(solver, region_id == i)

    # 各ヒントに対して、その領域が対称性を持つように制約を追加
    for i, (pos_type, sym_type, y, x) in enumerate(segments):
        solver.ensure(region_id[y, x] == i)

        def get_constraint(p_type, s_type, y, x):
            my_region = []
            if p_type == POS_CELL_CENTER:
                my_region = [(y, x)]
            elif p_type == POS_INTERSECTION:
                my_region = [(y, x), (y + 1, x), (y, x + 1), (y + 1, x + 1)]
            elif p_type == POS_VERTICAL_EDGE:
                my_region = [(y, x), (y, x + 1)]
            elif p_type == POS_HORIZONTAL_EDGE:
                my_region = [(y, x), (y + 1, x)]

            constraints = []
            for yy in range(height):
                for xx in range(width):
                    if (yy, xx) in my_region:
                        constraints.append(region_id[yy, xx] == i)
                    else:
                        new_y, new_x = reflect_cell(p_type, s_type, (y, x), (yy, xx))
                        if check_inside(height, width, new_y, new_x):
                            constraints.append((region_id[yy, xx] == i) == (region_id[new_y, new_x] == i))
                        else:
                            constraints.append(region_id[yy, xx] != i)
            return fold_and(constraints)

        if (sym_type != SYM_ANY):
            solver.ensure(get_constraint(pos_type, sym_type, y, x))
        else:
            c = []
            if (pos_type == POS_CELL_CENTER):
                c.append(get_constraint(pos_type, SYM_HORIZONTAL, y, x))
                c.append(get_constraint(pos_type, SYM_VERTICAL, y, x))
                c.append(get_constraint(pos_type, SYM_SLASH, y, x))
                c.append(get_constraint(pos_type, SYM_BACKSLASH, y, x))
            elif (pos_type == POS_INTERSECTION):
                c.append(get_constraint(pos_type, SYM_HORIZONTAL, y, x))
                c.append(get_constraint(pos_type, SYM_VERTICAL, y, x))
                c.append(get_constraint(pos_type, SYM_SLASH, y, x))
                c.append(get_constraint(pos_type, SYM_BACKSLASH, y, x))
            elif (pos_type == POS_VERTICAL_EDGE):
                c.append(get_constraint(pos_type, SYM_HORIZONTAL, y, x))
                c.append(get_constraint(pos_type, SYM_VERTICAL, y, x))
            elif (pos_type == POS_HORIZONTAL_EDGE):
                c.append(get_constraint(pos_type, SYM_HORIZONTAL, y, x))
                c.append(get_constraint(pos_type, SYM_VERTICAL, y, x))

            solver.ensure(fold_or(c))


    is_sat = solver.solve()
    return is_sat, region_id, division


def solve_and_show(height, width, problem):
    is_sat, region_id, division = solve_sentai_show(height, width, problem)

    if is_sat:
        print(stringify_grid_frame(division))

    else:
        print('no answer')


if __name__ == '__main__':
    height, width = (4, 4)

    center = [[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    intersection = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    vertical_mid = [[0, 0, 0], [0, 0, 0], [0, 3, 0], [0, 0, 0]]
    horizontal_mid = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    problem = (center, intersection, vertical_mid, horizontal_mid)

    is_sat, region_id = solve_sentai_show(height, width, problem)

    if is_sat:
        print(stringify_array(region_id, common_rules.NUM_MAP_ZERO))
