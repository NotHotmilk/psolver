import tkinter as tk
from tkinter import ttk, messagebox
from copy import deepcopy
import time
import colorsys
from polyomino_editor import PolyominoEditor


# HSL (h, s, l) → HEX 変換ヘルパー
def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


# ポリオミノ番号に応じた背景色を返す
def poly_color(num):
    hue = ((num - 1) * 209) % 360
    return hsl_to_hex(hue, 50, 50)


def enumerate_solutions(height, width, problem, blocks, rotation: list[bool], reflection: list[bool], max_solutions=16):
    from cspuz import Solver
    from cspuz.constraints import fold_and
    solver = Solver()
    # ドメインは 0 (空セル) から len(blocks)（ポリオミノ番号）
    kind = solver.int_array((height, width), 0, len(blocks))
    has_block = solver.bool_array((height, width))
    solver.add_answer_key(kind)
    import common_rules
    common_rules.place_polyomino_with_each_status(solver, kind, height, width, blocks, rotation, reflection)

    solver.ensure((kind == 0) == (~has_block))

    to_up = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_up[0, :] == 0)
    solver.ensure(to_up[1:, :] == has_block[:-1, :].cond(0, to_up[:-1, :] + 1))

    to_down = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_down[-1, :] == 0)
    solver.ensure(to_down[:-1, :] == has_block[1:, :].cond(0, to_down[1:, :] + 1))

    to_left = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_left[:, 0] == 0)
    solver.ensure(to_left[:, 1:] == has_block[:, :-1].cond(0, to_left[:, :-1] + 1))

    to_right = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_right[:, -1] == 0)
    solver.ensure(to_right[:, :-1] == has_block[:, 1:].cond(0, to_right[:, 1:] + 1))

    for y in range(height):
        for x in range(width):
            solver.ensure((kind[y, x] == 0).then(to_up[y, x] + to_down[y, x] == to_left[y, x] + to_right[y, x]))

    solutions = []
    is_sat = solver.find_answer()
    while is_sat and len(solutions) < max_solutions:
        sol = [[kind[y, x].sol for x in range(width)] for y in range(height)]
        solutions.append(sol)
        exclusion = []
        for y in range(height):
            for x in range(width):
                exclusion.append(kind[y, x] == kind[y, x].sol)
        solver.ensure(~fold_and(exclusion))
        is_sat = solver.find_answer()
    return solutions


class PuzzleSolverUI:
    def __init__(self, master, polyomino_app):
        self.polyomino_app = polyomino_app
        self.window = tk.Toplevel(master)
        self.window.title("正方形を残せチェッカー v1.2.0")

        # 盤面サイズ入力エリア（上部）
        size_frame = ttk.Frame(self.window, padding=10)
        size_frame.pack(fill="x")
        ttk.Label(size_frame, text="盤面サイズ: ").pack(side="left")
        self.height_var = tk.IntVar(value=6)
        self.width_var = tk.IntVar(value=6)
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=5)
        height_entry.pack(side="left", padx=5)
        ttk.Label(size_frame, text="×").pack(side="left")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=5)
        width_entry.pack(side="left", padx=5)
        size_update_btn = ttk.Button(size_frame, text="サイズを反映", command=self.update_board_size)
        size_update_btn.pack(side="left", padx=10)

        # 盤面エリア（問題入力・解答表示を共通）
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill="both", expand=True)
        board_frame = ttk.Frame(main_frame, padding=10)
        board_frame.pack(fill="both", expand=True)
        ttk.Label(board_frame, text="盤面").pack()
        self.cell_size = 40  # セルサイズ
        self.problem = []    # 盤面内部状態（boolの2次元リスト）
        self.board_canvas = tk.Canvas(board_frame, bg="white")
        self.board_canvas.pack(fill="both", expand=True)
        self.board_drag_value = None
        self.last_board_cell = (-1, -1)
        self.board_canvas.bind("<Button-1>", self.board_click)
        self.board_canvas.bind("<B1-Motion>", self.board_drag)

        # 解答切替用ナビゲーションフレーム
        nav_frame = ttk.Frame(main_frame, padding=10)
        nav_frame.pack(fill="x")
        self.prev_btn = ttk.Button(nav_frame, text="←", command=self.show_prev_solution)
        self.prev_btn.pack(side="left", padx=5)
        self.next_btn = ttk.Button(nav_frame, text="→", command=self.show_next_solution)
        self.next_btn.pack(side="left", padx=5)
        self.prev_btn.config(width=3)
        self.next_btn.config(width=3)
        self.sol_info_label = ttk.Label(nav_frame, text="")
        self.sol_info_label.pack(side="left", padx=20)

        # 「解く」ボタン
        solve_frame = ttk.Frame(self.window, padding=10)
        solve_frame.pack()
        self.solve_btn = ttk.Button(solve_frame, text="解く", command=self.solve_puzzle)
        self.solve_btn.pack()

        self.solutions = []
        self.current_solution_index = 0

        self.create_board()

        # キー操作で左右移動
        self.window.bind("<Left>", lambda e: self.show_prev_solution())
        self.window.bind("<Right>", lambda e: self.show_next_solution())

    def create_board(self):
        h = self.height_var.get() if hasattr(self, "height_var") else 12
        w = self.width_var.get() if hasattr(self, "width_var") else 12
        self.problem = [[False for _ in range(w)] for _ in range(h)]
        canvas_width = w * self.cell_size
        canvas_height = h * self.cell_size
        self.board_canvas.config(width=canvas_width, height=canvas_height)
        self.draw_board()

    def update_board_size(self):
        self.create_board()

    def draw_board(self):
        self.board_canvas.delete("all")
        h = len(self.problem)
        w = len(self.problem[0]) if h > 0 else 0
        for r in range(h):
            for c in range(w):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

    def board_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        h = len(self.problem)
        w = len(self.problem[0]) if h > 0 else 0
        if 0 <= row < h and 0 <= col < w:
            new_value = not self.problem[row][col]
            self.board_drag_value = new_value
            self.problem[row][col] = new_value
            self.last_board_cell = (row, col)
            self.draw_board()

    def board_drag(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if (row, col) == self.last_board_cell:
            return
        h = len(self.problem)
        w = len(self.problem[0]) if h > 0 else 0
        if 0 <= row < h and 0 <= col < w:
            if self.problem[row][col] != self.board_drag_value:
                self.problem[row][col] = self.board_drag_value
                self.last_board_cell = (row, col)
                self.draw_board()

    def solve_puzzle(self):
        h = self.height_var.get()
        w = self.width_var.get()
        if len(self.problem) != h or (self.problem and len(self.problem[0]) != w):
            self.create_board()

        polyominoes = self.polyomino_app.get_polyominoes()
        if not polyominoes:
            messagebox.showerror("エラー", "ポリオミノがありません。")
            return

        blocks = [deepcopy(p["grid"]) for p in polyominoes]
        rotation = [p["allow_rotate"] for p in polyominoes]
        reflection = [p["allow_flip"] for p in polyominoes]

        solutions = enumerate_solutions(h, w, self.problem, blocks, rotation, reflection)
        self.solutions = solutions
        self.current_solution_index = 0
        self.show_solution(self.current_solution_index)

    def show_solution(self, index):
        self.board_canvas.delete("all")
        if self.solutions:
            sol = self.solutions[index]
            h = len(sol)
            w = len(sol[0]) if h > 0 else 0
            cell = int(self.cell_size)
            canvas_width = w * cell
            canvas_height = h * cell
            self.board_canvas.config(width=canvas_width, height=canvas_height)
            for r in range(h):
                for c in range(w):
                    x1 = c * cell
                    y1 = r * cell
                    x2 = x1 + cell
                    y2 = y1 + cell
                    # セルの値が 0 の場合は白、非 0 の場合はポリオミノ番号に応じた色で描画
                    if sol[r][c] == 0:
                        fill_color = "white"
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    else:
                        num = sol[r][c]
                        fill_color = poly_color(num)
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                        self.board_canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                                      text=str(num), font=("Arial", int(cell / 2)))
        if not self.solutions:
            self.sol_info_label.config(text="解なし")
        elif len(self.solutions) == 1:
            self.sol_info_label.config(text="唯一解")
        elif len(self.solutions) >= 16:
            self.sol_info_label.config(text=f"16個以上の複数解 {self.current_solution_index + 1}/{len(self.solutions)}")
        else:
            self.sol_info_label.config(text=f"複数解 {self.current_solution_index + 1}/{len(self.solutions)}")

    def show_prev_solution(self):
        if self.solutions:
            self.current_solution_index = (self.current_solution_index - 1) % len(self.solutions)
            self.show_solution(self.current_solution_index)

    def show_next_solution(self):
        if self.solutions:
            self.current_solution_index = (self.current_solution_index + 1) % len(self.solutions)
            self.show_solution(self.current_solution_index)


if __name__ == "__main__":
    root = tk.Tk()
    poly_edit = PolyominoEditor(root, False, False)
    puzzle_ui = PuzzleSolverUI(root, poly_edit)
    root.mainloop()
