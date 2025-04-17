import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and
from cspuz.puzzle.util import stringify_array, stringify_grid_frame
import common_rules
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt



def solve(problem):
    height, width = len(problem) - 1, len(problem[0]) - 1

    solver = Solver()
    edge_type = solver.bool_array((height, width))  # False: /, True: \
    solver.add_answer_key(edge_type)

    N = 0
    S = 1
    E = 2
    W = 3

    def horizontal_node(x, y):
        if not ( 0 <= x < width and 0 <= y < height + 1):
            raise ValueError("Invalid coordinates for horizontal node")
        # (height + 1) * width
        return x + y * width

    def vertical_node(x, y):
        if not (0 <= x < width + 1 and 0 <= y < height):
            raise ValueError("Invalid coordinates for vertical node")
        return (width + 1) * height + x + y * (width + 1)

    def coord_to_node(x, y, direction):
        if direction == N:
            return horizontal_node(x, y)
        elif direction == S:
            return horizontal_node(x, y + 1)
        elif direction == E:
            return vertical_node(x + 1, y)
        elif direction == W:
            return vertical_node(x, y)

    g = graph.Graph((height + 1) * width + (width + 1) * height)
    edge_list = []
    for y in range(height):
        for x in range(width):
            g.add_edge(coord_to_node(x, y, N), coord_to_node(x, y, E))
            edge_list.append(edge_type[y, x])
            g.add_edge(coord_to_node(x, y, S), coord_to_node(x, y, W))
            edge_list.append(edge_type[y, x])
            g.add_edge(coord_to_node(x, y, N), coord_to_node(x, y, W))
            edge_list.append(~edge_type[y, x])
            g.add_edge(coord_to_node(x, y, S), coord_to_node(x, y, E))
            edge_list.append(~edge_type[y, x])
    graph.active_edges_single_cycle(solver, g, edge_list)

    for y in range(height + 1):
        for x in range(width + 1):
            if problem[y][x] >= 0:
                related = []
                if 0 < y and 0 < x:
                    related.append(edge_type[y - 1, x - 1])
                if 0 < y and x < width:
                    related.append(~edge_type[y - 1, x])
                if y < height and 0 < x:
                    related.append(~edge_type[y, x - 1])
                if y < height and x < width:
                    related.append(edge_type[y, x])
                solver.ensure(count_true(related) == problem[y][x])

    is_sat = solver.find_answer()
    return is_sat, edge_type


def plot_solution(problem, edge_type):
    """
    解答を matplotlib で描画する関数。

    - 各セルは 1×1 の正方形として描画し、セル内に斜め線を描きます。
    - edge_type が True なら左上から右下 (「\」)、
      False なら右上から左下 (「/」) を描画します。
    - 問題の頂点に数値が設定されている場合は、その数字も表示します。
    """
    # edge_type は numpy 配列で shape=(height, width)
    height, width = edge_type.shape
    fig, ax = plt.subplots(figsize=(width, height))

    # セルの境界線（グリッド）の描画
    for x in range(width + 1):
        ax.plot([x, x], [0, height], color='black', linewidth=1)
    for y in range(height + 1):
        ax.plot([0, width], [y, y], color='black', linewidth=1)

    # 各セルに斜め線を描画
    for y in range(height):
        for x in range(width):
            if edge_type[y, x].sol == True:
                ax.plot([x + 0.5, x + 1], [y, y + 0.5], color='black', linewidth=2)
                ax.plot([x, x + 0.5], [y + 0.5, y + 1], color='black', linewidth=2)
            elif edge_type[y, x].sol == False:
                ax.plot([x, x + 0.5], [y + 0.5, y], color='black', linewidth=2)
                ax.plot([x + 0.5, x + 1], [y + 1, y + 0.5], color='black', linewidth=2)

            else:
                # 未確定のセルは何も描画しない
                pass
    # 問題の頂点に数字を表示 (問題は (height+1) x (width+1) の配列)
    for y in range(height + 1):
        for x in range(width + 1):
            if problem[y][x] >= 0:
                ax.text(x, y, str(problem[y][x]), ha='center', va='center',
                        fontsize=12, color='red')

    ax.set_aspect('equal')
    ax.invert_yaxis()  # 上端を 0 にするために y 軸を反転
    ax.axis('off')
    plt.show()


if __name__ == "__main__":
    _ = -1
    problem = [
        [_, _, _, _, _, _],
        [_, _, _, 0, _, _],
        [2, _, _, _, _, _],
        [_, _, 4, _, _, _],
        [_, _, _, 4, _, _],
        [_, _, _, _, _, _],
    ]
    is_sat, edge_type = solve(problem)
    if is_sat:
        print("SAT")
        print(stringify_array(edge_type, common_rules.BW_MAP))
        plot_solution(problem, edge_type)
    else:
        print("UNSAT")
