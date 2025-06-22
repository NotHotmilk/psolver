import tkinter as tk
from tkinter import messagebox

# ユーザーの環境に 'ThreeNums.py' が存在することを前提とします
from ThreeNums import solve


class PuzzleGUI:
    def __init__(self, master):
        self.master = master
        master.title("3つの数字チェッカー v1.0.0")

        # ★ 変更点: 自動ソルブ用のタイマーIDを保持する変数を追加
        self.solve_timer = None

        # フラグ: 簡単入力モード
        self.simple_var = tk.BooleanVar(value=True)

        # 上部コントロール: N指定エントリとボタン + 簡単入力チェック
        ctrl_frame = tk.Frame(master)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(ctrl_frame, text="サイズ:").pack(side=tk.LEFT)
        self.n_entry = tk.Entry(ctrl_frame, width=5)
        self.n_entry.pack(side=tk.LEFT)
        tk.Button(ctrl_frame, text="設定", command=self.setup_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="解く", command=self.solve_puzzle).pack(side=tk.LEFT)
        # 簡単入力モードチェックボックス
        tk.Checkbutton(ctrl_frame, text="簡単入力", variable=self.simple_var).pack(side=tk.RIGHT)

        # 入力用フレーム
        self.grid_frame = tk.Frame(master)
        self.grid_frame.pack()

        self.top_entries = []
        self.left_entries = []
        self.center_labels = []
        self.focus_order = []
        self.widget_to_index = {}

        self.n_entry.insert(0, '6')
        self.setup_grid()

    def setup_grid(self):
        try:
            N = int(self.n_entry.get())
            if N <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("入力エラー", "1以上の整数を入力してください。")
            return
        self.N = N

        # 既存ウィジェットを破棄
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.top_entries.clear()
        self.left_entries.clear()
        self.center_labels.clear()
        self.focus_order.clear()
        self.widget_to_index.clear()

        # 新しいグリッド作成
        self.top_frame = tk.Frame(self.grid_frame)
        self.top_frame.grid(row=0, column=1)
        self.left_frame = tk.Frame(self.grid_frame)
        self.left_frame.grid(row=1, column=0)
        self.center_frame = tk.Frame(self.grid_frame)
        self.center_frame.grid(row=1, column=1)

        cell_size = 40
        # 上部 3×N の上キー
        for y in range(3):
            row = []
            for x in range(N):
                e = tk.Entry(self.top_frame, width=2, justify='center', font=("Arial", 14))
                e.grid(row=y, column=x, padx=1, pady=1, ipadx=cell_size // 10, ipady=cell_size // 10)
                e.bind("<Key>", self.on_key)
                e.bind("<Up>", lambda ev, r=y - 1, c=x, w='T': self.move_focus(r, c, w))
                e.bind("<Down>", lambda ev, r=y + 1, c=x, w='T': self.move_focus(r, c, w))
                e.bind("<Left>", lambda ev, r=y, c=x - 1, w='T': self.move_focus(r, c, w))
                e.bind("<Right>", lambda ev, r=y, c=x + 1, w='T': self.move_focus(r, c, w))
                row.append(e)
            self.top_entries.append(row)

        # 左部 N×3 の左キー
        for y in range(N):
            row = []
            for x in range(3):
                e = tk.Entry(self.left_frame, width=2, justify='center', font=("Arial", 14))
                e.grid(row=y, column=x, padx=1, pady=1, ipadx=cell_size // 10, ipady=cell_size // 10)
                e.bind("<Key>", self.on_key)
                e.bind("<Up>", lambda ev, r=y - 1, c=x, w='L': self.move_focus(r, c, w))
                e.bind("<Down>", lambda ev, r=y + 1, c=x, w='L': self.move_focus(r, c, w))
                e.bind("<Left>", lambda ev, r=y, c=x - 1, w='L': self.move_focus(r, c, w))
                e.bind("<Right>", lambda ev, r=y, c=x + 1, w='L': self.move_focus(r, c, w))
                row.append(e)
            self.left_entries.append(row)

        # 中央 N×N の解答表示
        for y in range(N):
            row = []
            for x in range(N):
                lbl = tk.Label(self.center_frame, width=2, height=1,
                               relief='ridge', text='', font=("Arial", 14))
                lbl.grid(row=y, column=x, padx=1, pady=1,
                         ipadx=cell_size // 10, ipady=cell_size // 10)
                row.append(lbl)
            self.center_labels.append(row)

        # フォーカス移動順序リストを構築
        # 縦キー: [0][0] -> [1][0] -> [2][0] -> [0][1] -> ...
        for x in range(N):
            for k in range(3):
                widget = self.top_entries[k][x]
                self.widget_to_index[widget] = len(self.focus_order)
                self.focus_order.append(widget)
        # 横キー: [0][0] -> [0][1] -> [0][2] -> [1][0] -> ...
        for y in range(N):
            for k in range(3):
                widget = self.left_entries[y][k]
                self.widget_to_index[widget] = len(self.focus_order)
                self.focus_order.append(widget)

        # ★ 変更点: グリッド再設定後、解答欄をクリア（自動で解を計算）
        self.solve_puzzle()

    def move_focus(self, row, col, which):
        if which == 'T':
            if col == -1:
                self.left_entries[0][row].focus_set()
            if row == 3:
                self.left_entries[col][2].focus_set()
        else:
            if row == -1:
                self.top_entries[col][0].focus_set()
            if col == 3:
                self.top_entries[2][row].focus_set()
        if row < 0 or col < 0:
            return
        if which == 'T':
            if row < 3 and col < self.N:
                self.top_entries[row][col].focus_set()
        else:
            if row < self.N and col < 3:
                self.left_entries[row][col].focus_set()

    # ★ 新規追加: ソルバーの実行を遅延させて予約するメソッド
    def schedule_solve(self):
        """連続したキー入力によるソルバーの過剰な実行を防ぐため、
        300msの遅延を設けてソルバーの実行を予約します。"""
        if self.solve_timer:
            self.master.after_cancel(self.solve_timer)
        self.solve_timer = self.master.after(300, self.solve_puzzle)

    def on_key(self, event):
        w = event.widget
        char = event.char
        # 数字入力時: 上書き＆挿入
        if char.isdigit():
            w.delete(0, tk.END)
            w.insert(0, char)
            # 簡単入力モードなら次へ移動
            if self.simple_var.get():
                idx = self.widget_to_index.get(w)
                if idx is not None:
                    next_idx = idx + 1
                    if next_idx < len(self.focus_order):
                        self.focus_order[next_idx].focus_set()
            self.schedule_solve()  # ★ 変更点: 自動ソルブを予約
            return "break"
        # Backspace/Delete
        if event.keysym in ('BackSpace', 'Delete'):
            w.delete(0, tk.END)
            if self.simple_var.get() and event.keysym == 'BackSpace':
                idx = self.widget_to_index.get(w)
                if idx is not None and idx - 1 >= 0:
                    self.focus_order[idx - 1].focus_set()
            self.schedule_solve()  # ★ 変更点: 自動ソルブを予約
            return "break"
        if event.keysym == 'space' and self.simple_var.get():
            w.delete(0, tk.END)
            idx = self.widget_to_index.get(w)
            if idx is not None and idx + 1 < len(self.focus_order):
                self.focus_order[idx + 1].focus_set()
            self.schedule_solve()  # ★ 変更点: 自動ソルブを予約
            return "break"
        return "break"

    def solve_puzzle(self):
        # ★ 変更点: 実行前に予約されたタイマーがあればキャンセル
        if self.solve_timer:
            self.master.after_cancel(self.solve_timer)
            self.solve_timer = None

        N = self.N
        v_keys_p = [[-1] * 3 for _ in range(N)]
        h_keys_p = [[-1] * 3 for _ in range(N)]
        try:
            for x in range(N):
                for k in range(3):
                    txt = self.top_entries[k][x].get().strip()
                    v_keys_p[x][k] = int(txt) if txt != '' else -1
            for y in range(N):
                for k in range(3):
                    txt = self.left_entries[y][k].get().strip()
                    h_keys_p[y][k] = int(txt) if txt != '' else -1
        except ValueError:
            messagebox.showerror("入力エラー", "キーは0～9の整数か空白で入力してください。")
            return

        try:
            is_sat, num_arr, *_ = solve(v_keys_p, h_keys_p)
        except Exception as e:
            messagebox.showerror("Solver エラー", str(e))
            return
        if not is_sat:
            for y in range(N):
                for x in range(N):
                    self.center_labels[y][x].config(text='☓')
            return

        grid = num_arr
        for y in range(N):
            for x in range(N):
                v = grid[y][x].sol
                if v is None:
                    # ★ 変更点: '?' の代わりに空白 '' を表示
                    txt = ''
                elif v == -1:
                    txt = '☓'
                else:
                    txt = str(v)
                self.center_labels[y][x].config(text=txt)


if __name__ == '__main__':
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()