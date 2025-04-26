import sys, json
import Guidearrow


def main():
    payload = json.load(sys.stdin)
    ty = payload['ty']
    tx = payload['tx']
    height = payload['height']
    width = payload['width']
    problem = payload['problem']

    # ソルバー実行
    is_sat, is_black = Guidearrow.solve_guidearrow(ty, tx, problem)
    ans = []

    # import tkinter as tk
    # from tkinter import messagebox
    # # デバッグ用ポップアップ
    # root = tk.Tk()
    # root.withdraw()  # メインウィンドウを非表示にする
    # debug_message = f"ty: {ty}\ntx: {tx}\nproblem: {problem}"
    # messagebox.showinfo("Debug Info", debug_message)
    

    def sol_to_str(sol, is_sat, n):
        if not is_sat:
            return -1 if n % 2 == 0 else 1
        if sol is None:
            return -1
        if sol == True:
            return 1
        if sol == False:
            return 0

    for y in range(height):
        line = []
        for x in range(width):
            line.append(sol_to_str(is_black[y, x].sol, is_sat, y + x))
        ans.append(line)

    # JSON で出力
    print(json.dumps({
        'is_black': ans
    }))
    
    sys.exit(0)


if __name__ == '__main__':
    main()
