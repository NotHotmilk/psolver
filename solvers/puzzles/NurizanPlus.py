# # NOTE: 問題読み込み
# 
# problemText = "NuriP/4/4/5.3.4.7/5.3.6.5/1.2.3.4/2.2.1.3/3.1.3.1/4.1.2.1"
# problemText = "NuriP/4/4/2.2.-.10/5.1.7.1/1.1.1.1/1.1.2.1/2.1.1.4/3.-.6.7"


def solve_nuri_p(problemText):

    problemText = problemText.strip().split("/")
    
    # バリデーション
    if problemText[0] != "NuriP":
        print("問題が正しく入力されていません。")
        # exit()
        return ["問題が正しく入力されていません。"]

    # 問題のサイズ
    height = int(problemText[1])
    width = int(problemText[2])

    # 問題のキー（枠外に表示されるヤツ）
    # .で区切ってint配列に変換
    p_y_keys = problemText[3].split(".")
    p_x_keys = problemText[4].split(".")

    # 問題の手がかり（枠内に表示されるヤツ）
    # .で区切って２次元int配列に変換
    p_problem = [i.split(".") for i in problemText[5:]]

    # # デバッグ
    # print(f"問題が入力されました。")
    # print(f"問題のサイズ: 縦{height}x横{width}")
    # print(f"キー: 縦{p_y_keys}x横{p_x_keys}")
    # print("手がかり:")
    # for i in p_problem:
    #     print(i)
    # print()

    # NOTE: 制約

    from cspuz import Solver

    solver = Solver()

    key_y = solver.int_array(height, 0, 1000)
    key_x = solver.int_array(width, 0, 1000)

    for y in range(height):
        if p_y_keys[y] != '-':
            solver.ensure(key_y[y] == int(p_y_keys[y]))

    for x in range(width):
        if p_x_keys[x] != '-':
            solver.ensure(key_x[x] == int(p_x_keys[x]))

    s_problem = solver.int_array((height, width), 0, 100)

    for y in range(height):
        for x in range(width):
            if p_problem[y][x] != '-':
                solver.ensure(s_problem[y, x] == int(p_problem[y][x]))

    is_white = solver.bool_array((height, width))

    solver.add_answer_key(is_white)

    # is_whiteなclueの和がkeyと一致する
    for y in range(height):
        solver.ensure(sum(is_white[y, x].cond(s_problem[y, x], 0) for x in range(width)) == key_y[y])

    for x in range(width):
        solver.ensure(sum(is_white[y, x].cond(s_problem[y, x], 0) for y in range(height)) == key_x[x])

    # NOTE: 結果


    # 解く 未確定なら?を表示 確定かつ白ならもともとの数字を表示 確定かつ黒なら#を表示
    if solver.solve():
        # 問題が解けた場合の処理
        is_unique_solution = not any(is_white[y, x].sol is None for y in range(height) for x in range(width))
        print("唯一解です。" if is_unique_solution else "唯一解ではありません。")
        # is_white_str = [['? ' if is_white[y, x].sol is None else '. ' if is_white[y, x].sol else '# ' for x in range(width)]
        #                 for y in range(height)]
        is_white_str = [
            ['? ' if is_white[y, x].sol is None else str(s_problem[y, x].sol) + ' ' if is_white[y, x].sol else '# ' for
             x in range(width)]
            for y in range(height)]

    else:
        # 問題が解けなかった場合の処理
        print("解が存在しません。")
        # exit()
        # answer に、! をheight*width個追加
        answer = []
        for y in range(height):
            answer.append('! ' * width)        
        return answer

    # 問題の解、または解けなかった場合の状態を表示
    answer = []
    
    for y in range(height):
        print(''.join(is_white_str[y]))
        answer.append(''.join(is_white_str[y]))

    return answer
