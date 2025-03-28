import tkinter as tk
from tkinter import ttk, messagebox
from copy import deepcopy
import colorsys
from polyomino_editor import PolyominoEditor


# HSL (h,s,l) → HEX 変換ヘルパー
def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


# ポリオミノ番号に応じた背景色を返す
def poly_color(num):
    hue = ((num - 1) * 209) % 360
    return hsl_to_hex(hue, 50, 50)


# --- おじゃまブロック迷路用ソルバー ---
def enumerate_solutions(height, width, problem, blocks, rotation: list[bool], reflection: list[bool], max_solutions=16):
    from cspuz import Solver
    from cspuz.constraints import fold_and
    from cspuz.graph import active_vertices_connected
    solver = Solver()
    # ドメインは -2（それ以外）、-1（濃い灰色セル）、0（★セル）、1～len(blocks)（ポリオミノ）    
    kind = solver.int_array((height, width), -2, len(blocks))
    solver.add_answer_key(kind)
    import common_rules
    common_rules.place_polyomino_with_each_status(solver, kind, height, width, blocks, rotation, reflection)

    # 問題盤面の各セルに対して、-1,0 のセルは配置を固定する
    for y in range(height):
        for x in range(width):
            solver.ensure((problem[y][x] == -1) == (kind[y, x] == -1))
            if problem[y][x] == 0:
                solver.ensure(kind[y, x] == 0)
            # -2と0は接触しない
            solver.ensure((kind[y, x] == -2).then(kind.four_neighbors(y, x) != 0))

    # ★セル同士の連結性を保証（★セル：kind == 0）
    active_vertices_connected(solver, kind == 0)

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
        self.window.title("おじゃまブロック迷路チェッカー v1.1.0")

        # メインフレーム
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill="both", expand=True)

        # 盤面（入力／解答表示統合用）を配置するフレーム
        board_frame = ttk.Frame(main_frame, padding=10)
        board_frame.pack(fill="both", expand=True)
        ttk.Label(board_frame, text="盤面").pack()

        self.cell_size = 40  # 入力時のセルサイズ
        self.problem = []    # 盤面内部状態（各セルは None, -1, 0 のいずれか）
        self.mode = "input"  # "input" または "solution"

        # 統合キャンバス：入力時は盤面入力、解答時は解答表示として利用
        self.board_canvas = tk.Canvas(board_frame, bg="white")
        self.board_canvas.pack()

        self.board_drag_value = None
        self.last_board_cell = (-1, -1)

        self.board_canvas.bind("<Button-1>", self.board_click)
        self.board_canvas.bind("<B1-Motion>", self.board_drag)
        self.board_canvas.bind("<Button-3>", self.board_right_click)  # 右クリック

        # 解答が複数ある場合の解答切替用ナビゲーションフレーム
        self.nav_frame = ttk.Frame(board_frame, padding=5)
        self.prev_btn = ttk.Button(self.nav_frame, text="←", command=self.show_prev_solution, width=3)
        self.prev_btn.pack(side="left", padx=5)
        self.next_btn = ttk.Button(self.nav_frame, text="→", command=self.show_next_solution, width=3)
        self.next_btn.pack(side="left", padx=5)
        self.sol_info_label = ttk.Label(self.nav_frame, text="")
        self.sol_info_label.pack(side="left", padx=20)
        # 常に表示（解答表示時に更新）
        self.nav_frame.pack()

        # 盤面サイズ入力エリア
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

        # 「解く」ボタン
        solve_frame = ttk.Frame(self.window, padding=10)
        solve_frame.pack()
        self.solve_btn = ttk.Button(solve_frame, text="解く", command=self.solve_puzzle)
        self.solve_btn.pack()

        self.solutions = []
        self.current_solution_index = 0

        self.create_board()

        # 矢印キーによる解答切替（解答表示時のみ有効）
        self.window.bind("<Left>", lambda e: self.show_prev_solution())
        self.window.bind("<Right>", lambda e: self.show_next_solution())

    def create_board(self):
        h = self.height_var.get()
        w = self.width_var.get()
        # 初期状態はすべて空（None）
        self.problem = [[None for _ in range(w)] for _ in range(h)]
        canvas_width = w * self.cell_size
        canvas_height = h * self.cell_size
        self.board_canvas.config(width=canvas_width, height=canvas_height)
        self.mode = "input"
        self.draw_board()

    def update_board_size(self):
        self.create_board()

    # 入力盤面描画（セル：-1→濃い灰色、0→★表示、None→白）
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
                cell_value = self.problem[r][c]
                fill_color = "dim gray" if cell_value == -1 else "white"
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                if cell_value == 0:
                    self.board_canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                                  text="★", font=("Arial", int(self.cell_size / 2)))

    # 左クリック：セルを -1（濃い灰色）に切替、既に -1 なら空に戻す
    def board_click(self, event):
        if self.mode == "solution":
            self.switch_to_input_mode()
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        h = len(self.problem)
        w = len(self.problem[0]) if h > 0 else 0
        if 0 <= row < h and 0 <= col < w:
            new_value = -1 if self.problem[row][col] != -1 else None
            self.board_drag_value = new_value
            self.problem[row][col] = new_value
            self.last_board_cell = (row, col)
            self.draw_board()

    # 左クリックドラッグ：ドラッグ開始時の値を反映
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

    # 右クリック：セルを 0（★マス）に切替、既に 0 なら空に戻す
    def board_right_click(self, event):
        if self.mode == "solution":
            self.switch_to_input_mode()
            return
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        h = len(self.problem)
        w = len(self.problem[0]) if h > 0 else 0
        if 0 <= row < h and 0 <= col < w:
            self.problem[row][col] = 0 if self.problem[row][col] != 0 else None
            self.draw_board()

    def switch_to_input_mode(self):
        """入力モードに切り替え、解答表示をクリアする"""
        self.mode = "input"
        self.solutions = []
        self.nav_frame.pack()  # ナビゲーションは常に表示
        self.draw_board()

    # 「解く」ボタン押下時：解答を求め、統合キャンバスに描画
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

    # 解答表示（各セルの描画ルール：
    #   - -1 → 濃い灰色
    #   - 0  → 薄い赤（★セル：もともと入力されていた★なら★、そうでなければ「・」）
    #   - -2 → 白
    #   - 1以上 → poly_color() による色付け＋数字表示
    def show_solution(self, index):
        self.mode = "solution"
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
                    if sol[r][c] == -1:
                        fill_color = "dim gray"
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    elif sol[r][c] == 0:
                        fill_color = "white"
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                        # 元々入力されていたセルが★なら★、そうでなければ「・」を表示
                        text_symbol = "★" if self.problem[r][c] == 0 else "・"
                        self.board_canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                                      text=text_symbol, font=("Arial", int(cell / 2)))
                    elif sol[r][c] == -2:
                        fill_color = "white"
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    else:
                        num = sol[r][c]
                        fill_color = poly_color(num)
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                        self.board_canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                                      text=str(num), font=("Arial", int(cell / 2)))
        # ナビゲーション情報の更新
        self.update_solution_nav()

    def update_solution_nav(self):
        """解答情報の表示とナビゲーションボタンの有効／無効を更新する"""
        if not self.solutions:
            info = "解なし"
        elif len(self.solutions) == 1:
            info = "唯一解"
        elif len(self.solutions) >= 16:
            info = f"16個以上の複数解 {self.current_solution_index + 1}/{len(self.solutions)}"
        else:
            info = f"複数解 {self.current_solution_index + 1}/{len(self.solutions)}"
        self.sol_info_label.config(text=info)

        # 解が複数ある場合のみナビゲーションボタンを有効にする
        if self.solutions and len(self.solutions) > 1:
            self.prev_btn.config(state="normal")
            self.next_btn.config(state="normal")
        else:
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
        # 常にナビゲーションフレームは表示
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
    poly_app = PolyominoEditor(root, False, False)
    puzzle_ui = PuzzleSolverUI(root, poly_app)
    root.mainloop()
