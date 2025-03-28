import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from copy import deepcopy
import json
import os
import colorsys

# ヘルパー関数：HSL → HEX 変換
def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

# ヘルパー関数：指定された色番号(1～3)に応じた色を返す
def poly_color(num):
    hue = ((num - 1) * 209) % 360
    return hsl_to_hex(hue, 50, 50)

class PolyominoEditor(ttk.Frame):
    def __init__(self, parent, default_allow_rotate=True, default_allow_flip=True):
        super().__init__(parent)
        self.master.title("ポリオミノエディタ v1.2.0 - 三色問題対応版 v1.0.0")
        self.pack(side="left", fill="y", padx=10, pady=10)

        # ttkスタイル設定
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Poly.TFrame", background="white")
        style.configure("SelectedPoly.TFrame", background="#99bbff")

        # 内部管理
        self.polyominoes = []
        self.current_poly_index = None
        self.drag_value = None

        self.grid_size = 8
        self.cell_size = 40

        # 左パネル（スクロール可能なリストと追加ボタン）
        self.left_frame = ttk.Frame(self, width=400, height=600)
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        # キャンバス（リスト部分）
        self.left_canvas = tk.Canvas(self.left_frame, borderwidth=0)
        self.vscrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.left_canvas.yview)
        self.left_canvas.configure(yscrollcommand=self.vscrollbar.set)
        self.vscrollbar.pack(side="right", fill="y")
        self.left_canvas.pack(side="top", fill="both", expand=True)
        self.left_canvas.bind("<Enter>", lambda e: self.left_canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.left_canvas.bind("<Leave>", lambda e: self.left_canvas.unbind_all("<MouseWheel>"))
        self.left_canvas.bind("<Button-4>", lambda event: self.left_canvas.yview_scroll(-1, "units"))
        self.left_canvas.bind("<Button-5>", lambda event: self.left_canvas.yview_scroll(1, "units"))

        self.poly_list_container = ttk.Frame(self.left_canvas, padding=5)
        self.left_canvas.create_window((0, 0), window=self.poly_list_container, anchor="nw")
        self.poly_list_container.bind("<Configure>",
                                      lambda event: self.left_canvas.configure(
                                          scrollregion=self.left_canvas.bbox("all")))

        # 下部ボタン群（追加・辞書操作）
        self.bottom_frame = ttk.Frame(self.left_frame)
        self.bottom_frame.pack(side="bottom", fill="x", pady=5)
        self.add_button = ttk.Button(self.bottom_frame, text="ポリオミノを追加",
                                     command=lambda: self.add_polyomino(default_allow_rotate, default_allow_flip))
        self.add_button.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        self.register_button = ttk.Button(self.bottom_frame, text="辞書に登録", command=self.register_current_poly_to_dict)
        self.register_button.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        self.load_dict_button = ttk.Button(self.bottom_frame, text="辞書から呼び出す", command=self.open_dictionary_dialog)
        self.load_dict_button.pack(side="left", fill="x", expand=True, padx=2, pady=2)

        # 中央キャンバス：8x8グリッドの描画
        self.center_frame = ttk.Frame(self)
        self.center_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        canvas_width = self.grid_size * self.cell_size
        canvas_height = self.grid_size * self.cell_size
        self.canvas = tk.Canvas(self.center_frame, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)

        self.rect_ids = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                self.rect_ids[r][c] = rect

        self.refresh_poly_list()

        # 辞書ファイルの読み込み
        self.dictionary_file = "polyomino_dictionary_three_color.json"
        self.load_polyomino_dict()


    def _on_mousewheel(self, event):
        self.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def canvas_click(self, event):
        if self.current_poly_index is None:
            return
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return
        poly = self.polyominoes[self.current_poly_index]
        new_value = 0 if poly["grid"][row][col] == 1 else 1
        poly["grid"][row][col] = new_value
        self.drag_value = new_value
        self.update_canvas()

    def canvas_drag(self, event):
        if self.current_poly_index is None or self.drag_value is None:
            return
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return
        poly = self.polyominoes[self.current_poly_index]
        if poly["grid"][row][col] != self.drag_value:
            poly["grid"][row][col] = self.drag_value
            fill_color = "gray" if self.drag_value == 1 else "white"
            self.canvas.itemconfig(self.rect_ids[row][col], fill=fill_color)

    def update_canvas(self):
        if self.current_poly_index is None:
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    self.canvas.itemconfig(self.rect_ids[r][c], fill="white")
        else:
            poly = self.polyominoes[self.current_poly_index]
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    fill_color = "gray" if poly["grid"][r][c] == 1 else "white"
                    self.canvas.itemconfig(self.rect_ids[r][c], fill=fill_color)

    def add_polyomino(self, default_allow_rotate, default_allow_flip):
        new_poly = {
            "grid": [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)],
            "name": "",
            "allow_rotate": default_allow_rotate,
            "allow_flip": default_allow_flip,
            "disabled": False,
            "color": 0,  # 0: 未設定, 1: 赤, 2: 青, 3: 黄
        }
        self.polyominoes.append(new_poly)
        self.load_polyomino(len(self.polyominoes) - 1)

    def refresh_poly_list(self):
        for child in self.poly_list_container.winfo_children():
            child.destroy()

        for index, poly in enumerate(self.polyominoes):
            style_name = "SelectedPoly.TFrame" if index == self.current_poly_index else "Poly.TFrame"
            main_frame = ttk.Frame(self.poly_list_container, style=style_name, relief="ridge", borderwidth=2, padding=5)
            main_frame.pack(fill="x", pady=5)
            preview_cell_size = 10
            preview_canvas = tk.Canvas(main_frame, width=self.grid_size * preview_cell_size,
                                       height=self.grid_size * preview_cell_size, bg="white", highlightthickness=0)
            preview_canvas.pack(side="left", padx=(0, 5))
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    x1 = c * preview_cell_size
                    y1 = r * preview_cell_size
                    x2 = x1 + preview_cell_size
                    y2 = y1 + preview_cell_size
                    # もしセルが1なら、ポリオミノの色設定に応じてpoly_color()で色付け
                    if poly["grid"][r][c] == 1:
                        fill_color = poly_color(poly["color"]) if poly["color"] != 0 else "gray"
                    else:
                        fill_color = "white"
                    preview_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

            content_frame = ttk.Frame(main_frame)
            content_frame.pack(side="left", fill="x", expand=True)
            btn_frame = ttk.Frame(content_frame)
            btn_frame.pack(fill="x")
            edit_btn = ttk.Button(btn_frame, text="編集", command=lambda i=index: self.load_polyomino(i))
            edit_btn.pack(side="left", padx=2)
            del_btn = ttk.Button(btn_frame, text="削除", command=lambda i=index: self.delete_polyomino(i))
            del_btn.pack(side="left", padx=2)
            up_btn = ttk.Button(btn_frame, text="↑", width=3, command=lambda i=index: self.move_poly_up(i))
            up_btn.pack(side="left", padx=2)
            if index == 0:
                up_btn.state(["disabled"])
            down_btn = ttk.Button(btn_frame, text="↓", width=3, command=lambda i=index: self.move_poly_down(i))
            down_btn.pack(side="left", padx=2)
            if index == len(self.polyominoes) - 1:
                down_btn.state(["disabled"])
            entry_frame = ttk.Frame(content_frame)
            entry_frame.pack(fill="x", pady=3)
            ttk.Label(entry_frame, text="名前:").grid(row=0, column=0, sticky="w")
            name_var = tk.StringVar(value=poly["name"])
            name_entry = ttk.Entry(entry_frame, textvariable=name_var, width=15)
            name_entry.grid(row=0, column=1, sticky="w", padx=2)
            name_var.trace_add("write", lambda *args, i=index, var=name_var: self.update_poly_name(i, var.get()))

            # 色選択用コンボボックス
            color_frame = ttk.Frame(content_frame)
            color_frame.pack(fill="x", pady=3)
            ttk.Label(color_frame, text="色:").pack(side="left")
            color_options = ["未設定", "赤", "青", "黄"]
            current_color = poly.get("color", 0)
            color_var = tk.StringVar(value=color_options[current_color])
            color_combo = ttk.Combobox(color_frame, textvariable=color_var, values=color_options, state="readonly", width=10)
            color_combo.pack(side="left", padx=2)
            color_combo.bind("<<ComboboxSelected>>", lambda e, i=index, var=color_var: self.update_poly_color(i, var.get()))

            check_frame = ttk.Frame(content_frame)
            check_frame.pack(fill="x")
            rotate_var = tk.BooleanVar(value=poly["allow_rotate"])
            rotate_chk = ttk.Checkbutton(check_frame, text="回転を許す", variable=rotate_var,
                                         command=lambda i=index, var=rotate_var: self.update_rotate(i, var.get()))
            rotate_chk.pack(side="left", padx=2)
            flip_var = tk.BooleanVar(value=poly["allow_flip"])
            flip_chk = ttk.Checkbutton(check_frame, text="反転を許す", variable=flip_var,
                                       command=lambda i=index, flip_var=flip_var, rotate_var=rotate_var: self.update_flip(i, flip_var.get(), rotate_var))
            flip_chk.pack(side="left", padx=2)
            disable_var = tk.BooleanVar(value=poly.get("disabled", False))
            disable_chk = ttk.Checkbutton(check_frame, text="無効化", variable=disable_var,
                                          command=lambda i=index, var=disable_var: self.update_disable(i, var.get()))
            disable_chk.pack(side="left", padx=2)

    def update_poly_color(self, index, new_color_str):
        mapping = {"未設定": 0, "赤": 1, "青": 2, "黄": 3}
        self.polyominoes[index]["color"] = mapping.get(new_color_str, 0)

    def load_polyomino(self, index):
        self.current_poly_index = index
        self.update_canvas()
        self.refresh_poly_list()

    def delete_polyomino(self, index):
        del self.polyominoes[index]
        if self.current_poly_index == index:
            self.current_poly_index = None
            self.update_canvas()
        elif self.current_poly_index is not None and self.current_poly_index > index:
            self.current_poly_index -= 1
        self.refresh_poly_list()

    def move_poly_up(self, index):
        if index <= 0:
            return
        self.polyominoes[index - 1], self.polyominoes[index] = self.polyominoes[index], self.polyominoes[index - 1]
        if self.current_poly_index == index:
            self.current_poly_index = index - 1
        elif self.current_poly_index == index - 1:
            self.current_poly_index = index
        self.refresh_poly_list()

    def move_poly_down(self, index):
        if index >= len(self.polyominoes) - 1:
            return
        self.polyominoes[index + 1], self.polyominoes[index] = self.polyominoes[index], self.polyominoes[index + 1]
        if self.current_poly_index == index:
            self.current_poly_index = index + 1
        elif self.current_poly_index == index + 1:
            self.current_poly_index = index
        self.refresh_poly_list()

    def update_poly_name(self, index, new_name):
        self.polyominoes[index]["name"] = new_name

    def update_rotate(self, index, value):
        if self.polyominoes[index]["allow_flip"] and not value:
            value = True
        self.polyominoes[index]["allow_rotate"] = value

    def update_flip(self, index, value, rotate_var):
        self.polyominoes[index]["allow_flip"] = value
        if value:
            self.polyominoes[index]["allow_rotate"] = True
            rotate_var.set(True)

    def update_disable(self, index, value):
        self.polyominoes[index]["disabled"] = value

    def get_polyominoes(self):
        if not self.polyominoes:
            return None
        ret_poly_list = [deepcopy(poly) for poly in self.polyominoes if not poly.get("disabled", False)]
        if not ret_poly_list:
            return None
        ret_poly_list = [deepcopy(poly) for poly in ret_poly_list if any(any(row) for row in poly["grid"])]
        if not ret_poly_list:
            return None
        return ret_poly_list

    # ---------------------------
    # 辞書関連の機能
    # ---------------------------
    def load_polyomino_dict(self):
        if os.path.exists(self.dictionary_file):
            try:
                with open(self.dictionary_file, 'r', encoding='utf-8') as f:
                    self.poly_dict = json.load(f)
            except Exception as e:
                messagebox.showerror("エラー", f"辞書ファイルの読み込みに失敗しました: {e}")
                self.poly_dict = []
        else:
            self.poly_dict = []

    def save_polyomino_dict(self):
        try:
            with open(self.dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(self.poly_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("エラー", f"辞書ファイルの保存に失敗しました: {e}")

    def register_current_poly_to_dict(self):
        if self.current_poly_index is None:
            messagebox.showwarning("選択なし", "登録するポリオミノをまず編集してください。")
            return
        poly = deepcopy(self.polyominoes[self.current_poly_index])
        if not poly["name"]:
            name = simpledialog.askstring("名前入力", "ポリオミノの名前を入力してください。")
            if not name:
                messagebox.showwarning("名前が必要", "ポリオミノには名前が必要です。")
                return
            poly["name"] = name

        for i, entry in enumerate(self.poly_dict):
            if entry["name"] == poly["name"]:
                overwrite = messagebox.askyesno("上書き確認", "同じ名前のポリオミノが既に存在します。上書きしますか？")
                if overwrite:
                    self.poly_dict[i] = poly
                else:
                    return
                break
        else:
            self.poly_dict.append(poly)
        self.save_polyomino_dict()
        messagebox.showinfo("登録完了", "ポリオミノが辞書に登録されました。")

    def open_dictionary_dialog(self):
        dict_window = tk.Toplevel(self)
        dict_window.title("辞書から呼び出す")
        dict_window.geometry("400x300")

        content_frame = ttk.Frame(dict_window)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        listbox_frame = ttk.Frame(content_frame)
        listbox_frame.pack(side="left", fill="both", expand=True)
        listbox = tk.Listbox(listbox_frame, selectmode="extended")
        listbox.pack(fill="both", expand=True)
        for entry in self.poly_dict:
            listbox.insert("end", entry["name"])
        listbox.bind("<<ListboxSelect>>", lambda event: self.update_preview(listbox, preview_canvas))

        preview_frame = ttk.Frame(content_frame)
        preview_frame.pack(side="left", fill="both", expand=True, padx=(5,0))
        preview_canvas = tk.Canvas(preview_frame, width=self.grid_size*15, height=self.grid_size*15, bg="white", highlightthickness=1, relief="solid")
        preview_canvas.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(dict_window)
        btn_frame.pack(fill="x", padx=5, pady=5)
        load_btn = ttk.Button(btn_frame, text="読み込む",
                              command=lambda: self.load_polyomino_from_dict(listbox, dict_window))
        load_btn.pack(side="left", padx=5)
        delete_btn = ttk.Button(btn_frame, text="削除",
                                command=lambda: self.delete_polyomino_from_dict(listbox))
        delete_btn.pack(side="left", padx=5)
        close_btn = ttk.Button(btn_frame, text="閉じる", command=dict_window.destroy)
        close_btn.pack(side="right", padx=5)

    def update_preview(self, listbox, preview_canvas):
        preview_canvas.delete("all")
        selections = listbox.curselection()
        if not selections:
            return
        index = selections[0]
        poly = self.poly_dict[index]
        preview_cell_size = 15
        for r, row in enumerate(poly["grid"]):
            for c, cell in enumerate(row):
                x1 = c * preview_cell_size
                y1 = r * preview_cell_size
                x2 = x1 + preview_cell_size
                y2 = y1 + preview_cell_size
                # もしセルが1なら、poly_color()で色付け
                fill_color = poly_color(poly.get("color", 0)) if cell == 1 and poly.get("color", 0) != 0 else ("gray" if cell == 1 else "white")
                preview_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

    def load_polyomino_from_dict(self, listbox, window):
        selections = listbox.curselection()
        if not selections:
            messagebox.showwarning("選択なし", "読み込むポリオミノを選択してください。")
            return
        for index in selections:
            poly = deepcopy(self.poly_dict[index])
            self.polyominoes.append(poly)
        self.current_poly_index = len(self.polyominoes) - 1
        self.update_canvas()
        self.refresh_poly_list()
        window.destroy()

    def delete_polyomino_from_dict(self, listbox):
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("選択なし", "削除するポリオミノを選択してください。")
            return
        for index in reversed(selection):
            confirm = messagebox.askyesno("確認", f"{self.poly_dict[index]['name']}を本当に削除してもよろしいですか？")
            if confirm:
                del self.poly_dict[index]
                listbox.delete(index)
        self.save_polyomino_dict()

if __name__ == "__main__":
    root = tk.Tk()
    app = PolyominoEditor(root)
    root.mainloop()
