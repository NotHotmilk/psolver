import flet as ft

GRID_ROWS = 4
GRID_COLS = 5
CELL_SIZE = 60      


def main(page: ft.Page) -> None:
    page.title = "Puzzle GUI – Grid only"
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20

    # --- グリッドセルを 2 次元リストで保持しておく（後工程で状態管理に使う） ---
    cells: list[list[ft.Container]] = [[]]

    # 外枠として縁の太い Container を用意し、その中に Row/Column でマスを並べる
    outer = ft.Container(
        padding=1,                          # 外枠の線分
        border=ft.border.all(4, ft.colors.BLACK),
    )

    # ↓ Column の中に Row を並べて格子を作る
    col_children: list[ft.Control] = []
    for r in range(GRID_ROWS):
        row_children: list[ft.Control] = []
        for c in range(GRID_COLS):
            cell = ft.Container(
                width=CELL_SIZE,
                height=CELL_SIZE,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(0, ft.colors.BLACK),
            )
            row_children.append(cell)
        cells.append(row_children)           # 後でアクセスできるよう保存
        col_children.append(ft.Row(row_children, tight=True))

    outer.content = ft.Column(col_children, tight=True)
    page.add(outer)

    # ------------------------------------------------------------------
    # 以降のステップで：セルに on_click を付ける／状態を保持する／
    # 問題入力モード⇔解答モードを切り替える――などを実装します
    # ------------------------------------------------------------------


if __name__ == "__main__":
    # デスクトップ環境（flet-desktop）用
    ft.app(target=main)
    # Web で確認したい場合は:
    # ft.app(target=main, view=ft.WEB_BROWSER)
