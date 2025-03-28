import tkinter as tk
from tkinter import ttk, messagebox
from copy import deepcopy
import colorsys
from polyomino_editor_three_colors_edition import PolyominoEditor


# HSL (h,s,l) → HEX 変換ヘルパー
def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


# 指定された色番号に応じた色を返す（赤:1, 青:2, 黄:3）
def poly_color(num):
    hue = ((num - 1) * 209) % 360
    return hsl_to_hex(hue, 50, 50)


# --- 三色問題用ソルバー ---
def enumerate_solutions(height, width, problem, blocks, rotation: list[bool], reflection: list[bool],
                        block_color: list[int], max_solutions=16):
    from cspuz import Solver
    from cspuz.constraints import fold_and
    from cspuz.graph import active_vertices_connected
    solver = Solver()
    # -1: 黒いセル, 0: 空白, 1以上: ポリオミノ番号
    kind = solver.int_array((height, width), -1, len(blocks))
    color = solver.int_array((height, width), 0, 3)  # 0: 未定, 1: 赤, 2: 青, 3: 黄
    solver.add_answer_key(kind)
    import common_rules
    common_rules.place_polyomino_with_each_status(solver, kind, height, width, blocks, rotation, reflection, False)

    # 黒いセルはポリオミノに含まれない
    for y in range(height):
        for x in range(width):
            solver.ensure((problem[y][x] == -1) == (kind[y, x] == -1))
            if problem[y][x] == -1:
                solver.ensure(color[y, x] == 0)

    # 各ポリオミノの色を設定
    for y in range(height):
        for x in range(width):
            for p in range(len(blocks)):
                if block_color[p] == 0:
                    solver.ensure((kind[y, x] == (p + 1)).then(color[y, x] != 0))  # 赤, 青, 黄のいずれか
                else:
                    solver.ensure((kind[y, x] == (p + 1)).then(color[y, x] == block_color[p]))

    # 同じ色のポリオミノは接触しない
    for y in range(height):
        for x in range(width):
            if x + 1 < width:
                solver.ensure(
                    ((color[y, x] != 0) & (color[y, x] == color[y, x + 1]))
                    .then(kind[y, x] == kind[y, x + 1]))
            if y + 1 < height:
                solver.ensure(
                    ((color[y, x] != 0) & (color[y, x] == color[y + 1, x]))
                    .then(kind[y, x] == kind[y + 1, x]))
            if x - 1 >= 0:
                solver.ensure(
                    ((color[y, x] != 0) & (color[y, x] == color[y, x - 1]))
                    .then(kind[y, x] == kind[y, x - 1]))
            if y - 1 >= 0:
                solver.ensure(
                    ((color[y, x] != 0) & (color[y, x] == color[y - 1, x]))
                    .then(kind[y, x] == kind[y - 1, x]))

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
        self.window.title("三色問題チェッカー v1.0.0")

        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill="both", expand=True)

        board_frame = ttk.Frame(main_frame, padding=10)
        board_frame.pack(fill="both", expand=True)
        ttk.Label(board_frame, text="盤面").pack()

        self.cell_size = 40
        self.problem = []  # 各セルは None または -1
        self.mode = "input"

        self.board_canvas = tk.Canvas(board_frame, bg="white")
        self.board_canvas.pack()

        self.board_drag_value = None
        self.last_board_cell = (-1, -1)

        # 左クリックで黒セル(-1)の配置／解除
        self.board_canvas.bind("<Button-1>", self.board_click)
        self.board_canvas.bind("<B1-Motion>", self.board_drag)
        # 右クリックの★機能は削除

        self.nav_frame = ttk.Frame(board_frame, padding=5)
        self.prev_btn = ttk.Button(self.nav_frame, text="←", command=self.show_prev_solution, width=3)
        self.prev_btn.pack(side="left", padx=5)
        self.next_btn = ttk.Button(self.nav_frame, text="→", command=self.show_next_solution, width=3)
        self.next_btn.pack(side="left", padx=5)
        self.sol_info_label = ttk.Label(self.nav_frame, text="")
        self.sol_info_label.pack(side="left", padx=20)
        self.nav_frame.pack()

        size_frame = ttk.Frame(self.window, padding=10)
        size_frame.pack(fill="x")
        ttk.Label(size_frame, text="盤面サイズ: ").pack(side="left")
        self.height_var = tk.IntVar(value=10)
        self.width_var = tk.IntVar(value=10)
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=5)
        height_entry.pack(side="left", padx=5)
        ttk.Label(size_frame, text="×").pack(side="left")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=5)
        width_entry.pack(side="left", padx=5)
        size_update_btn = ttk.Button(size_frame, text="サイズを反映", command=self.update_board_size)
        size_update_btn.pack(side="left", padx=10)

        solve_frame = ttk.Frame(self.window, padding=10)
        solve_frame.pack()
        self.solve_btn = ttk.Button(solve_frame, text="解く", command=self.solve_puzzle)
        self.solve_btn.pack()

        self.solutions = []
        self.current_solution_index = 0

        self.create_board()

        self.window.bind("<Left>", lambda e: self.show_prev_solution())
        self.window.bind("<Right>", lambda e: self.show_next_solution())

    def create_board(self):
        h = self.height_var.get()
        w = self.width_var.get()
        self.problem = [[-1 for _ in range(w)] for _ in range(h)]
        canvas_width = w * self.cell_size
        canvas_height = h * self.cell_size
        self.board_canvas.config(width=canvas_width, height=canvas_height)
        self.mode = "input"
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
                cell_value = self.problem[r][c]
                fill_color = "#212121" if cell_value == -1 else "white"
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

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
        self.mode = "input"
        self.solutions = []
        self.nav_frame.pack()
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

        # # すべてのポリオミノに色が設定されているか確認（0: 未設定）
        # for p in polyominoes:
        #     if p.get("color", 0) == 0:
        #         messagebox.showerror("エラー", "すべてのポリオミノに色（赤, 青, 黄）を設定してください。")
        #         return

        blocks = [deepcopy(p["grid"]) for p in polyominoes]
        rotation = [p["allow_rotate"] for p in polyominoes]
        reflection = [p["allow_flip"] for p in polyominoes]
        block_color = [p["color"] for p in polyominoes]

        solutions = enumerate_solutions(h, w, self.problem, blocks, rotation, reflection, block_color)
        self.solutions = solutions
        self.current_solution_index = 0
        self.show_solution(self.current_solution_index)

    def show_solution(self, index):
        self.mode = "solution"
        self.board_canvas.delete("all")
        polyominoes = self.polyomino_app.get_polyominoes()
        if self.solutions:
            sol = self.solutions[index]
            h = len(sol)
            w = len(sol[0]) if h > 0 else 0
            cell = self.cell_size
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
                        fill_color = "#000000"
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    elif sol[r][c] == 0:
                        fill_color = "white"
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                    else:
                        poly_index = sol[r][c] - 1
                        pcolor = polyominoes[poly_index]["color"]
                        fill_color = poly_color(pcolor)
                        self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                        self.board_canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                                      text=str(sol[r][c]), font=("Arial", int(cell / 2)))
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


if __name__ == "__main__":
    root = tk.Tk()
    poly_app = PolyominoEditor(root, True, False)
    puzzle_ui = PuzzleSolverUI(root, poly_app)
    root.mainloop()
