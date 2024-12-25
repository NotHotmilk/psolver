from cspuz import Solver
from cspuz.constraints import alldifferent, cond

R, B, Y, G, ALL = 0, 1, 2, 3, 4
X1, X2, Y1, Y2 = "X1", "X2", "Y1", "Y2"


def solve_asp():
    solver = Solver()

    num = solver.int_array(16, 1, 4)
    col = solver.int_array(16, 0, 3)

    solver.add_answer_key(num, col)

    solver.ensure(alldifferent((num + col + col + col + col)))

    UL, UR, DL, DR = 0, 1, 2, 3

    def line_col(player_num, line):
        idx = (player_num - 1) * 4
        return {
            X1: (col[idx + UL], col[idx + DL]),
            X2: (col[idx + UR], col[idx + DR]),
            Y1: (col[idx + UL], col[idx + UR]),
            Y2: (col[idx + DL], col[idx + DR])
        }.get(line)

    def line_num(player_num, line):
        idx = (player_num - 1) * 4
        return {
            X1: (num[idx + UL], num[idx + DL]),
            X2: (num[idx + UR], num[idx + DR]),
            Y1: (num[idx + UL], num[idx + UR]),
            Y2: (num[idx + DL], num[idx + DR])
        }.get(line)

    def get_num_of_color_in_line(player_num, line, color):
        col1, col2 = line_col(player_num, line)
        num1, num2 = line_num(player_num, line)

        if color == ALL:
            return num1 + num2
        else:
            return cond(col1 == color, num1, 0) + cond(col2 == color, num2, 0)

    def ensure_sum(player_num, line, color, ans):
        solver.ensure(get_num_of_color_in_line(player_num, line, color) == ans)

    def ensure_two_sum(player_num, line, color1, color2, ans):
        solver.ensure(get_num_of_color_in_line(player_num, line, color1)
                      + get_num_of_color_in_line(player_num, line, color2) == ans)

    def ensure_diff(player_num, line, bigger_color, smaller_color, ans):
        solver.ensure(get_num_of_color_in_line(player_num, line, bigger_color)
                      - get_num_of_color_in_line(player_num, line, smaller_color) == ans)

    # ここに問題ごとの制約を追加する

    ensure_sum(1, Y2, ALL, 8)
    ensure_diff(1, X2, B, Y, 0)

    # ここまで

    if solver.solve():
        print_answer(num, col)
    else:
        print("no answer")


def print_answer(num, col):
    from colorist import Color

    def num2str(n):
        return "." if n is None else str(n)

    def colorize(c):
        if c is None:
            return Color.WHITE
        return [Color.RED, Color.BLUE, Color.YELLOW, Color.GREEN][c]

    for i in range(4):
        print(f"p{i + 1}")
        for j in range(4):
            idx = i * 4 + j
            print(f"{colorize(col[idx].sol)}{num2str(num[idx].sol)}{Color.OFF}", end=" " if j % 2 == 0 else "\n")


if __name__ == '__main__':
    solve_asp()
