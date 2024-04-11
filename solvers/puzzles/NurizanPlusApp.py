from tkinter import Tk, Label, Entry, Button, Frame, messagebox, Text, DISABLED
import pyperclip
import NurizanPlus


class PuzzleUI:
    def __init__(self, master):
        self.master = master
        self.master.title("ぬり算＋ ソルバー")

        # サイズ入力UIの設定
        self.label_width = Label(master, text="幅:")
        self.label_height = Label(master, text="高さ:")
        self.entry_width = Entry(master)
        self.entry_height = Entry(master)
        self.button_generate = Button(master, text="盤面を作成", command=self.validate_and_generate)

        # UI配置
        self.label_width.grid(row=0, column=1)
        self.entry_width.grid(row=0, column=2)
        self.label_height.grid(row=1, column=1)
        self.entry_height.grid(row=1, column=2)
        self.button_generate.grid(row=2, column=1, columnspan=2)

        # パズル盤面とキー入力スペースを表示するフレーム
        self.frame_board = Frame(master)
        self.frame_key_top = Frame(master)  # 上部のキー入力スペース
        self.frame_key_left = Frame(master)  # 左側のキー入力スペース

        # 「パズルを出力」ボタン
        self.button_output = Button(master, text="パズルを出力", command=self.output_puzzle)
        self.button_output.grid(row=5, column=1, columnspan=2)

        # 解表示グリッドのフレーム（初期化時には非表示）
        self.frame_solution = Frame(master)
        self.frame_solution.grid(row=0, column=3, rowspan=10, padx=10, sticky="nsew")
        self.solution_entries = []
        
        # 初期盤面の生成 (5x5)
        self.entry_width.insert(0, "5")
        self.entry_height.insert(0, "5")
        self.generate_board()

        # 初期盤面と解表示グリッドの生成
        self.height = 5
        self.width = 5
        self.generate_board()
        self.create_solution_grid(self.height, self.width)
        
        # 「パズルを解く」ボタンの追加
        self.button_solve = Button(master, text="パズルを解く", command=self.solve_puzzle)
        self.button_solve.grid(row=6, column=1, columnspan=2)

    def create_solution_grid(self, height, width):
        # 既存の解表示スペースをクリア
        for row in self.solution_entries:
            for entry in row:
                entry.destroy()
        self.solution_entries = []

        # 新しい解表示グリッドの作成
        for y in range(height):
            row_entries = []
            for x in range(width):
                entry = Entry(self.frame_solution, width=2, font=("Helvetica", 14), justify="center", state=DISABLED)
                entry.grid(row=y, column=x, padx=1, pady=1)
                row_entries.append(entry)
            self.solution_entries.append(row_entries)

    def validate_and_generate(self):
        width = self.entry_width.get()
        height = self.entry_height.get()
        if width.isdigit() and height.isdigit():
            width = int(width)
            height = int(height)
            if 2 <= width <= 12 and 2 <= height <= 12:
                self.generate_board()
            else:
                print("幅と高さは2以上12以下である必要があります。")
        else:
            print("幅と高さには正の整数を入力してください。")

    def generate_board(self):
        # 既存のウィジェットをクリア
        for frame in [self.frame_board, self.frame_key_top, self.frame_key_left]:
            for widget in frame.winfo_children():
                widget.destroy()

        self.width = int(self.entry_width.get())
        self.height = int(self.entry_height.get())
        
        # 上部キー入力スペースの生成
        self.top_keys = []
        self.frame_key_top.grid(row=3, column=2, columnspan=self.width, sticky="nsew")
        for x in range(self.width):
            frame = Frame(self.frame_key_top, width=40, height=40, borderwidth=1, relief="solid")
            frame.pack(side="left", padx=1)
            frame.pack_propagate(False)
            entry = Entry(frame, justify="center", font=("Helvetica", 14), bg="#bbbbbb")
            entry.pack(expand=True, fill="both")
            self.top_keys.append(entry)

        # 左側キー入力スペースの生成
        self.left_keys = []
        self.frame_key_left.grid(row=4, column=1, rowspan=self.height, sticky="nsew")
        for y in range(self.height):
            frame = Frame(self.frame_key_left, width=40, height=40, borderwidth=1, relief="solid")
            frame.pack(side="top", pady=1)
            frame.pack_propagate(False)
            entry = Entry(frame, justify="center", font=("Helvetica", 14), bg="#bbbbbb")
            entry.pack(expand=True, fill="both")
            self.left_keys.append(entry)

        # パズル盤面の生成
        self.puzzle_entries = []
        self.frame_board.grid(row=4, column=2, sticky="nsew")
        for y in range(self.height):
            row_entries = []
            for x in range(self.width):
                frame = Frame(self.frame_board, width=40, height=40, borderwidth=1, relief="solid")
                frame.grid(row=y, column=x, padx=1, pady=1)
                frame.pack_propagate(False)
                entry = Entry(frame, justify="center", font=("Helvetica", 14))
                entry.pack(expand=True, fill="both")
                row_entries.append(entry)
            self.puzzle_entries.append(row_entries)

        self.create_solution_grid(self.height, self.width)

    def output_puzzle(self):
        top_key_values = '.'.join(entry.get() if entry.get().isdigit() else '-' for entry in self.top_keys)
        left_key_values = '.'.join(entry.get() if entry.get().isdigit() else '-' for entry in self.left_keys)

        # パズル盤面の値を取得（未入力はハイフンで置き換え）
        puzzle_rows = []
        for row in self.puzzle_entries:
            row_values = '.'.join(entry.get() if entry.get().isdigit() else '-' for entry in row)
            puzzle_rows.append(row_values)
        puzzle_rows_values = '/'.join(puzzle_rows)

        # 最終的な出力文字列の構築
        output_str = f"NuriP/{self.height}/{self.width}/{left_key_values}/{top_key_values}/{puzzle_rows_values}"
        print(output_str)
        pyperclip.copy(output_str) # クリップボードにコピー
        return output_str

    def solve_puzzle(self):
        # パズルの状態を文字列として取得
        puzzle_str = self.output_puzzle()  # output_puzzleメソッドを修正して結果を返すようにする必要があります
        # NurizanPlusのsolve_NuriP関数を呼び出して解を取得
        solution = NurizanPlus.solve_nuri_p(puzzle_str)
        # # 結果をメッセージボックスで表示
        # messagebox.showinfo("解", "\n".join(solution))
        # 解表示グリッドの作成
        # 解の表示
        for y, row in enumerate(solution):
            for x, cell in enumerate(row.split()):
                entry = self.solution_entries[y][x]
                entry.config(state="normal")  # 編集可能に設定
                entry.delete(0, "end")  # 既存のテキストをクリア
                entry.insert(0, cell)  # 新しい値を挿入
                entry.config(state="readonly")  # 読み取り専用に設定


# メインウィンドウの作成とアプリの実行
root = Tk()
app = PuzzleUI(root)
root.mainloop()
