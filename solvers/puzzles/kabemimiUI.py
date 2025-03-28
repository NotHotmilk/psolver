import tkinter as tk
from tkinter import ttk, messagebox
from copy import deepcopy
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


# --- 壁に耳ありチェッカー（統合版・色付け＆＊保持対応・解なし情報表示変更） ---
# 問題盤面は bool の2次元リスト（True: もともと＊があったセル）
def enumerate_solutions(height, width, problem, blocks, rotation: list[bool], reflection: list[bool], max_solutions=16):
    from cspuz import Solver
    from cspuz.constraints import fold_and
    solver = Solver()
    # セルの値は 0（空セル）～len(blocks)（ポリオミノ番号）
    kind = solver.int_array((height, width), 0, len(blocks))
    solver.add_answer_key(kind)
    import common_rules
    common_rules.place_polyomino_with_each_status(solver, kind, height, width, blocks, rotation, reflection)
    # 問題盤面で True のセルは必ずポリオミノが置かれる（0 ではない）
    for y in range(height):
        for x in range(width):
            if problem[y][x]:
                solver.ensure(kind[y, x] != 0)
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
        self.window.title("壁に耳ありチェッカー v1.2.2")

        # 盤面サイズ入力エリア
        size_frame = ttk.Frame(self.window, padding=10)
        size_frame.pack(fill="x")
        ttk.Label(size_frame, text="盤面サイズ: ").pack(side="left")
        self.height_var = tk.IntVar(value=12)
        self.width_var = tk.IntVar(value=12)
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=5)
        height_entry.pack(side="left", padx=5)
        ttk.Label(size_frame, text="×").pack(side="left")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=5)
        width_entry.pack(side="left", padx=5)
        size_update_btn = ttk.Button(size_frame, text="サイズを反映", command=self.update_board_size)
        size_update_btn.pack(side="left", padx=10)

        # 統合キャンバスとナビゲーション（解答切替用）
        board_frame = ttk.Frame(self.window, padding=10)
        board_frame.pack(fill="both", expand=True)
        ttk.Label(board_frame, text="盤面").pack()
        self.cell_size = 40  # セルサイズ
        self.problem = []    # 入力盤面：各セルは False（空）または True（もともと＊があった）
        self.mode = "input"  # "input"（盤面入力）または "solution"（解答表示）
        self.board_canvas = tk.Canvas(board_frame, bg="white")
        self.board_canvas.pack(fill="both", expand=True)
        self.board_canvas.bind("<Button-1>", self.board_click)
        self.board_canvas.bind("<B1-Motion>", self.board_drag)

        # 解答切替用ナビゲーションフレーム（解答表示時にのみ表示）
        self.nav_frame = ttk.Frame(board_frame, padding=10)
        self.prev_btn = ttk.Button(self.nav_frame, text="←", command=self.show_prev_solution, width=3)
        self.prev_btn.pack(side="left", padx=5)
        self.next_btn = ttk.Button(self.nav_frame, text="→", command=self.show_next_solution, width=3)
        self.next_btn.pack(side="left", padx=5)
        self.sol_info_label = ttk.Label(self.nav_frame, text="")
        self.sol_info_label.pack(side="left", padx=20)
        self.nav_frame.pack_forget()

        # 「解く」ボタン
        solve_frame = ttk.Frame(self.window, padding=10)
        solve_frame.pack()
        self.solve_btn = ttk.Button(solve_frame, text="解く", command=self.solve_puzzle)
        self.solve_btn.pack()

        self.solutions = []
        self.current_solution_index = 0

        self.last_board_cell = (-1, -1)
        self.board_drag_value = None

        self.create_board()

        # 矢印キーで解答切替
        self.window.bind("<Left>", lambda e: self.show_prev_solution())
        self.window.bind("<Right>", lambda e: self.show_next_solution())

    def create_board(self):
        h = self.height_var.get()
        w = self.width_var.get()
        self.problem = [[False for _ in range(w)] for _ in range(h)]
        canvas_width = w * self.cell_size
        canvas_height = h * self.cell_size
        self.board_canvas.config(width=canvas_width, height=canvas_height)
        self.mode = "input"
        self.nav_frame.pack_forget()
        self.draw_board()

    def update_board_size(self):
        self.create_board()

    def draw_board(self):
        self.board_canvas.delete("all")
        h = len(self.problem)
        w = len(self.problem[0]) if h > 0 else 0
        if self.mode == "input":
            # 盤面入力モード：白背景＋＊があるセルには "＊" を表示
            for r in range(h):
                for c in range(w):
                    x1 = c * self.cell_size
                    y1 = r * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.board_canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                    if self.problem[r][c]:
                        self.board_canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                                      text="＊", font=("Arial", int(self.cell_size/2)))
        elif self.mode == "solution":
            # 解答表示モード：各セルが 0 なら白、非 0 ならポリオミノの色を描画（＊は保持）
            sol = self.solutions[self.current_solution_index]
            canvas_width = w * self.cell_size
            canvas_height = h * self.cell_size
            self.board_canvas.config(width=canvas_width, height=canvas_height)
            for r in range(h):
                for c in range(w):
                    x1 = c * self.cell_size
                    y1 = r * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    if sol[r][c] == 0:
                        fill_color = "white"
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    else:
                        num = sol[r][c]
                        fill_color = poly_color(num)
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                        # もともと＊があったセルなら "＊" を表示、なければテキストは表示しない
                        if self.problem[r][c]:
                            self.board_canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                                          text="＊", font=("Arial", int(self.cell_size/2)))

    def board_click(self, event):
        if self.mode == "solution":
            # 解答表示中はクリックで入力モードに戻る
            self.switch_to_input_mode()
            return
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
        if self.mode == "solution":
            self.switch_to_input_mode()
            return
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

    def switch_to_input_mode(self):
        """解答表示モードから入力モードに戻す"""
        self.mode = "input"
        self.solutions = []
        self.nav_frame.pack_forget()
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
        if not self.solutions:
            # 解なしの場合はキャンバスはそのままにして、情報ラベルに「解なし」を表示
            self.sol_info_label.config(text="解なし")
            self.nav_frame.pack()
            return
        self.mode = "solution"
        self.current_solution_index = index
        self.draw_board()
        self.update_solution_nav()

    def update_solution_nav(self):
        if not self.solutions:
            info = "解なし"
        elif len(self.solutions) == 1:
            info = "唯一解"
        elif len(self.solutions) >= 16:
            info = f"16個以上の複数解 {self.current_solution_index + 1}/{len(self.solutions)}"
        else:
            info = f"複数解 {self.current_solution_index + 1}/{len(self.solutions)}"
        self.sol_info_label.config(text=info)
        if self.solutions and len(self.solutions) > 1:
            self.prev_btn.config(state="normal")
            self.next_btn.config(state="normal")
        else:
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
        self.nav_frame.pack()

    def show_prev_solution(self):
        if self.solutions:
            self.current_solution_index = (self.current_solution_index - 1) % len(self.solutions)
            self.show_solution(self.current_solution_index)

    def show_next_solution(self):
        if self.solutions:
            self.current_solution_index = (self.current_solution_index + 1) % len(self.solutions)
            self.show_solution(self.current_solution_index)


# --- メイン ---
if __name__ == "__main__":
    root = tk.Tk()
    poly_app = PolyominoEditor(root, True, False)
    puzzle_ui = PuzzleSolverUI(root, poly_app)
    root.mainloop()
