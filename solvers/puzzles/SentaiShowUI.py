import tkinter as tk
import math
import json
import SentaiShow  # solver機能

# --- 定数 ---
# 位置の種類（整数で管理）
POS_CELL_CENTER = 0
POS_INTERSECTION = 1
POS_VERTICAL_EDGE = 2
POS_HORIZONTAL_EDGE = 3

# 対称軸の種類
SYM_HORIZONTAL = 1
SYM_VERTICAL = 2
SYM_SLASH = 3  # 斜め "/"
SYM_BACKSLASH = 4  # 斜め "\"

SYM_ANY = 5  # 任意の状態（＊）

CELL = "cell"
INTERSECTION = "intersection"
VERTICAL = "vertical"
HORIZONTAL = "horizontal"

# --- グローバル変数 ---
gridHeight = 10
gridWidth = 10
cellSize = 0
threshold = 0

# 各候補位置用の内部配列
cellCenters = []  # サイズ: gridHeight × gridWidth
intersections = []  # サイズ: (gridHeight-1) × (gridWidth-1)
verticalEdges = []  # サイズ: gridHeight × (gridWidth-1)
horizontalEdges = []  # サイズ: (gridHeight-1) × gridWidth

# 現在のカーソル位置（候補オブジェクト：辞書 { "type", "i", "j" }）
currentCursor = None


# --- 配列初期化 ---
def initArrays():
    global cellCenters, intersections, verticalEdges, horizontalEdges
    cellCenters = [[0 for _ in range(gridWidth)] for _ in range(gridHeight)]
    intersections = [[0 for _ in range(gridWidth - 1)] for _ in range(gridHeight - 1)]
    verticalEdges = [[0 for _ in range(gridWidth - 1)] for _ in range(gridHeight)]
    horizontalEdges = [[0 for _ in range(gridWidth)] for _ in range(gridHeight - 1)]


# --- 候補位置の座標計算 ---
def getCandidatePosition(candidate):
    """候補 candidate は { 'type', 'i', 'j' } の形式。
    各候補のキャンバス上の座標 (x, y) を返します。"""
    t = candidate["type"]
    i = candidate["i"]
    j = candidate["j"]
    if t == "cell":
        x = j * cellSize + cellSize / 2
        y = i * cellSize + cellSize / 2
    elif t == "intersection":
        x = j * cellSize
        y = i * cellSize
    elif t == "vertical":
        x = (j + 1) * cellSize
        y = i * cellSize + cellSize / 2
    elif t == "horizontal":
        x = j * cellSize + cellSize / 2
        y = (i + 1) * cellSize
    return x, y


def getAllCandidates():
    candidates = []
    # セル中央
    for i in range(gridHeight):
        for j in range(gridWidth):
            cand = {"type": "cell", "i": i, "j": j}
            x, y = getCandidatePosition(cand)
            cand["x"] = x
            cand["y"] = y
            candidates.append(cand)
    # 内側の格子点（交点）：i,j = 1～gridHeight-1, 1～gridWidth-1
    for i in range(1, gridHeight):
        for j in range(1, gridWidth):
            cand = {"type": "intersection", "i": i, "j": j}
            x, y = getCandidatePosition(cand)
            cand["x"] = x
            cand["y"] = y
            candidates.append(cand)
    # vertical 辺中点
    for i in range(gridHeight):
        for j in range(gridWidth - 1):
            cand = {"type": "vertical", "i": i, "j": j}
            x, y = getCandidatePosition(cand)
            cand["x"] = x
            cand["y"] = y
            candidates.append(cand)
    # horizontal 辺中点
    for i in range(gridHeight - 1):
        for j in range(gridWidth):
            cand = {"type": "horizontal", "i": i, "j": j}
            x, y = getCandidatePosition(cand)
            cand["x"] = x
            cand["y"] = y
            candidates.append(cand)
    return candidates


def findClosestCandidate(x, y):
    candidates = getAllCandidates()
    bestCandidate = None
    bestDist = float("inf")
    for cand in candidates:
        dx = cand["x"] - x
        dy = cand["y"] - y
        dist = math.hypot(dx, dy)
        if dist < bestDist:
            bestDist = dist
            bestCandidate = cand
    if bestDist <= threshold:
        return bestCandidate
    return None


# --- シンボル描画 ---
def getAllowedSymbols(candidate_type):
    if candidate_type in (CELL, INTERSECTION):
        return [1, 2, 3, 4, 5]  # 5がAny状態（＊）を表す
    elif candidate_type in (VERTICAL, HORIZONTAL):
        return [1, 3, 5]
    else:
        return []


def drawSymbol(cx, cy, value):
    """
    内部の value によって線分を描画します。

    セル・交点の場合（cycle: 0,1,2,3,4,5）の意味：
      0 : 空白
      1 : ｜（垂直線）
      2 : ／（斜め /）
      3 : ―（水平線）
      4 : ＼（斜め \）
      5 : ＊ (Any)

    辺の場合は、値は 0,1,3 のみ。
    線分の全長は cellSize*0.5、線幅は 3 です。
    """
    lineLength = cellSize * 0.5
    half = lineLength / 2
    if value == 0:
        return
    elif value == 1:
        canvas.create_line(cx, cy - half, cx, cy + half, width=3)
    elif value == 2:
        delta = half / math.sqrt(2)
        canvas.create_line(cx - delta, cy + delta, cx + delta, cy - delta, width=3)
    elif value == 3:
        canvas.create_line(cx - half, cy, cx + half, cy, width=3)
    elif value == 4:
        delta = half / math.sqrt(2)
        canvas.create_line(cx - delta, cy - delta, cx + delta, cy + delta, width=3)
    elif value == 5:
        canvas.create_line(cx, cy - half, cx, cy + half, width=3)
        canvas.create_line(cx - half, cy, cx + half, cy, width=3)
        delta = half / math.sqrt(2)
        canvas.create_line(cx - delta, cy - delta, cx + delta, cy + delta, width=3)
        canvas.create_line(cx - delta, cy + delta, cx + delta, cy - delta, width=3)


def drawExplorationSymbol(cx, cy, value):
    # 探索用には ANY 状態（value==5）の場合のみ描画する
    if value != 5:
        return
    # ANY 状態の場合、drawSymbol と同様に "*" を表示（薄い赤色）
    # canvas.create_text(cx, cy, text="*", font=("Helvetica", int(cellSize*0.5)), fill="lightcoral", tags="explore")
    lineLength = cellSize * 0.5
    half = lineLength / 2
    canvas.create_line(cx, cy - half, cx, cy + half, width=3, fill="lightcoral", tags="explore")
    canvas.create_line(cx - half, cy, cx + half, cy, width=3, fill="lightcoral", tags="explore")
    delta = half / math.sqrt(2)
    canvas.create_line(cx - delta, cy - delta, cx + delta, cy + delta, width=3, fill="lightcoral", tags="explore")
    canvas.create_line(cx - delta, cy + delta, cx + delta, cy - delta, width=3, fill="lightcoral", tags="explore")


# --- division 解答描画 ---
def drawDivisionSolution(division):
    """
    solve_sentai_show から返された division 解答をキャンバス上に描画します。
    盤面の外枠は何もしません。

    内部の垂直エッジ（division.vertical, shape=(gridHeight, gridWidth-1)）について：
      - True なら、該当エッジ全体に沿って緑色の縦線を描画
      - False なら、該当エッジの中央において、エッジに直交する短い灰色の横線を描画

    内部の水平エッジ（division.horizontal, shape=(gridHeight-1, gridWidth)）について：
      - True なら、該当エッジ全体に沿って緑色の横線を描画
      - False なら、該当エッジの中央において、エッジに直交する短い灰色の縦線を描画
    """
    # 描画前に既存の division 描画を削除
    canvas.delete("division")

    # 垂直エッジ（内側のみ：j=1,...,gridWidth-1）
    for i in range(gridHeight):
        for j in range(1, gridWidth):
            # division.vertical は配列で、各要素は属性 sol を持つと仮定
            sol = division.vertical[i, j].sol if hasattr(division.vertical[i, j], "sol") else division.vertical[i, j]
            # キャンバス上の位置：x = j * cellSize, y 座標の範囲は [i*cellSize, (i+1)*cellSize]
            mid_x = j * cellSize
            mid_y = i * cellSize + cellSize / 2
            if sol is None:
                continue
            elif sol is True:
                # 緑色の縦線：エッジ全体（セル境界全体）
                x0 = mid_x
                y0 = i * cellSize
                x1 = mid_x
                y1 = (i + 1) * cellSize
                canvas.create_line(x0, y0, x1, y1, fill="green", width=3, tags="division")
            elif sol is False:
                # 灰色の横線：エッジ中央、横方向の短い線
                short = cellSize * 0.3
                x0 = mid_x - short / 2
                y0 = mid_y
                x1 = mid_x + short / 2
                y1 = mid_y
                canvas.create_line(x0, y0, x1, y1, fill="gray", width=3, tags="division")
    # 水平エッジ（内側のみ：i=1,...,gridHeight-1）
    for i in range(1, gridHeight):
        for j in range(gridWidth):
            sol = division.horizontal[i, j].sol if hasattr(division.horizontal[i, j], "sol") else division.horizontal[
                i, j]
            mid_x = j * cellSize + cellSize / 2
            mid_y = i * cellSize
            if sol is None:
                continue
            elif sol is True:
                # 緑色の横線：エッジ全体
                x0 = j * cellSize
                y0 = mid_y
                x1 = (j + 1) * cellSize
                y1 = mid_y
                canvas.create_line(x0, y0, x1, y1, fill="green", width=3, tags="division")
            elif sol is False:
                # 灰色の縦線：エッジ中央、短い縦線
                short = cellSize * 0.3
                x0 = mid_x
                y0 = mid_y - short / 2
                x1 = mid_x
                y1 = mid_y + short / 2
                canvas.create_line(x0, y0, x1, y1, fill="gray", width=3, tags="division")


def exploreZeroCandidates():
    """
    すべての候補位置で、現在値が 0 のものに対して、
    ANY状態（値 5）を仮入力した場合の解の存在を探索します。
    解が存在する場合、その記号（5）を薄い赤（探索用）で描画します。
    この探索結果は一時的な描画（タグ "explore"）とします。
    """
    canvas.delete("explore")
    results = []
    for cand in getAllCandidates():
        cand_type = cand["type"]
        i = cand["i"]
        j = cand["j"]
        # 現在の値を取得
        if cand_type == CELL:
            current_val = cellCenters[i][j]
        elif cand_type == INTERSECTION:
            current_val = intersections[i - 1][j - 1]
        elif cand_type == VERTICAL:
            current_val = verticalEdges[i][j]
        elif cand_type == HORIZONTAL:
            current_val = horizontalEdges[i][j]
        else:
            continue
        if current_val != 0:
            continue
        # 探索は ANY 状態のみ、すなわち 5
        if cand_type in (CELL, INTERSECTION, VERTICAL, HORIZONTAL):
            if cand_type == CELL:
                cellCenters[i][j] = 5
            elif cand_type == INTERSECTION:
                intersections[i - 1][j - 1] = 5
            elif cand_type == VERTICAL:
                verticalEdges[i][j] = 5
            elif cand_type == HORIZONTAL:
                horizontalEdges[i][j] = 5
            prob = (cellCenters, intersections, verticalEdges, horizontalEdges)
            is_sat, _, _ = SentaiShow.solve_sentai_show(gridHeight, gridWidth, prob)
            if is_sat:
                results.append((cand, 5))
            # 元に戻す
            if cand_type == CELL:
                cellCenters[i][j] = 0
            elif cand_type == INTERSECTION:
                intersections[i - 1][j - 1] = 0
            elif cand_type == VERTICAL:
                verticalEdges[i][j] = 0
            elif cand_type == HORIZONTAL:
                horizontalEdges[i][j] = 0
    for cand, sym in results:
        cx, cy = getCandidatePosition(cand)
        drawExplorationSymbol(cx, cy, sym)



# --- キャンバス描画 ---
def drawGrid():
    canvas.delete("all")
    # 盤面の外枠
    canvas.create_rectangle(0, 0, cellSize * gridWidth, cellSize * gridHeight, width=3)
    # 内部グリッド（破線）
    for j in range(1, gridWidth):
        x = j * cellSize
        canvas.create_line(x, 0, x, cellSize * gridHeight, dash=(5, 5))
    for i in range(1, gridHeight):
        y = i * cellSize
        canvas.create_line(0, y, cellSize * gridWidth, y, dash=(5, 5))
    # セル中央のシンボル
    for i in range(gridHeight):
        for j in range(gridWidth):
            val = cellCenters[i][j]
            if val != 0:
                cx = j * cellSize + cellSize / 2
                cy = i * cellSize + cellSize / 2
                drawSymbol(cx, cy, val)
    # 内側の格子点（交点）のシンボル
    for i in range(1, gridHeight):
        for j in range(1, gridWidth):
            val = intersections[i - 1][j - 1]
            if val != 0:
                cx = j * cellSize
                cy = i * cellSize
                drawSymbol(cx, cy, val)
    # vertical 辺中点のシンボル
    for i in range(gridHeight):
        for j in range(gridWidth - 1):
            val = verticalEdges[i][j]
            if val != 0:
                cx = (j + 1) * cellSize
                cy = i * cellSize + cellSize / 2
                drawSymbol(cx, cy, val)
    # horizontal 辺中点のシンボル
    for i in range(gridHeight - 1):
        for j in range(gridWidth):
            val = horizontalEdges[i][j]
            if val != 0:
                cx = j * cellSize + cellSize / 2
                cy = (i + 1) * cellSize
                drawSymbol(cx, cy, val)
    # カーソル描画（赤の点線円）
    if currentCursor is not None:
        x, y = getCandidatePosition(currentCursor)
        r = cellSize * 0.1
        canvas.create_oval(x - r, y - r, x + r, y + r, outline="red", dash=(2, 2), width=1)


# --- マウスクリックイベント ---
def onCanvasClick(event):
    global currentCursor
    x, y = event.x, event.y
    cand = findClosestCandidate(x, y)
    if cand:
        currentCursor = {"type": cand["type"], "i": cand["i"], "j": cand["j"]}
        if cand["type"] in (CELL, INTERSECTION):
            # セル・交点はサイクル: 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 0
            if cand["type"] == CELL:
                cellCenters[cand["i"]][cand["j"]] = (cellCenters[cand["i"]][cand["j"]] + 1) % 6
            else:
                intersections[cand["i"] - 1][cand["j"] - 1] = (intersections[cand["i"] - 1][cand["j"] - 1] + 1) % 6
        elif cand["type"] in (VERTICAL, HORIZONTAL):
            # 辺の場合はサイクル: 0 -> 1 -> 3 -> 5 -> 0
            if cand["type"] == VERTICAL:
                current_val = verticalEdges[cand["i"]][cand["j"]]
                if current_val == 0:
                    verticalEdges[cand["i"]][cand["j"]] = 1
                elif current_val == 1:
                    verticalEdges[cand["i"]][cand["j"]] = 3
                elif current_val == 3:
                    verticalEdges[cand["i"]][cand["j"]] = 5
                elif current_val == 5:
                    verticalEdges[cand["i"]][cand["j"]] = 0
            else:
                current_val = horizontalEdges[cand["i"]][cand["j"]]
                if current_val == 0:
                    horizontalEdges[cand["i"]][cand["j"]] = 1
                elif current_val == 1:
                    horizontalEdges[cand["i"]][cand["j"]] = 3
                elif current_val == 3:
                    horizontalEdges[cand["i"]][cand["j"]] = 5
                elif current_val == 5:
                    horizontalEdges[cand["i"]][cand["j"]] = 0
        drawGrid()



# --- キーボード操作 ---
def moveCursor(dx, dy):
    global currentCursor
    candidates = getAllCandidates()
    if currentCursor is None:
        currentCursor = {"type": CELL, "i": 0, "j": 0}
    curX, curY = getCandidatePosition(currentCursor)
    bestCandidate = currentCursor
    bestDist = float("inf")
    for cand in candidates:
        if (cand["type"] == currentCursor["type"] and
                cand["i"] == currentCursor["i"] and
                cand["j"] == currentCursor["j"]):
            continue
        vecX = cand["x"] - curX
        vecY = cand["y"] - curY
        dot = vecX * dx + vecY * dy
        if dot <= 0:
            continue
        dist = math.hypot(vecX, vecY)
        if dist < bestDist:
            bestDist = dist
            bestCandidate = {"type": cand["type"], "i": cand["i"], "j": cand["j"]}
    currentCursor = bestCandidate
    drawGrid()


def setCurrentCursorValue(val):
    if currentCursor is None:
        return
    t = currentCursor["type"]
    i = currentCursor["i"]
    j = currentCursor["j"]
    if t == CELL:
        cellCenters[i][j] = val  # 0～5
    elif t == INTERSECTION:
        intersections[i - 1][j - 1] = val  # 0～5
    elif t == VERTICAL:
        if val in (0, 1, 3, 5):
            verticalEdges[i][j] = val
    elif t == HORIZONTAL:
        if val in (0, 1, 3, 5):
            horizontalEdges[i][j] = val
    drawGrid()

def onKeyPress(event):
    if event.keysym in ["Up", "Down", "Left", "Right"]:
        if event.keysym == "Up":
            moveCursor(0, -1)
        elif event.keysym == "Down":
            moveCursor(0, 1)
        elif event.keysym == "Left":
            moveCursor(-1, 0)
        elif event.keysym == "Right":
            moveCursor(1, 0)
    elif event.keysym == "BackSpace":
        setCurrentCursorValue(0)
    elif event.char:
        # セル・交点の場合、"1"-"5"または "*" で入力可能
        if currentCursor is not None and currentCursor["type"] in (CELL, INTERSECTION):
            if event.char in "12345":
                setCurrentCursorValue(int(event.char))
        elif currentCursor is not None and currentCursor["type"] in (VERTICAL, HORIZONTAL):
            # 辺の場合は "1", "3", "5" を受け付ける
            if event.char in "135":
                setCurrentCursorValue(int(event.char))




# --- グリッド生成 ---
def generateGrid():
    global gridHeight, gridWidth, cellSize, threshold, currentCursor
    try:
        gridHeight = int(height_entry.get())
        gridWidth = int(width_entry.get())
    except Exception as e:
        print("入力エラー:", e)
        return
    if gridHeight < 2:
        gridHeight = 2
    if gridHeight > 20:
        gridHeight = 20
    if gridWidth < 2:
        gridWidth = 2
    if gridWidth > 20:
        gridWidth = 20
    height_entry.delete(0, tk.END)
    height_entry.insert(0, str(gridHeight))
    width_entry.delete(0, tk.END)
    width_entry.insert(0, str(gridWidth))
    initArrays()
    cellSize = min(500 / gridWidth, 500 / gridHeight)
    threshold = cellSize * 0.3
    currentCursor = {"type": CELL, "i": 0, "j": 0}
    drawGrid()
    canvas.focus_set()


# --- 入出力機能 ---
def exportProblem():
    global gridHeight, gridWidth, cellCenters, intersections, verticalEdges, horizontalEdges
    data = {
        "gridHeight": gridHeight,
        "gridWidth": gridWidth,
        "cellCenters": cellCenters,
        "intersections": intersections,
        "verticalEdges": verticalEdges,
        "horizontalEdges": horizontalEdges
    }
    s = json.dumps(data)
    io_entry.delete(0, tk.END)
    io_entry.insert(0, s)
    # 自動コピー
    root.clipboard_clear()
    root.clipboard_append(s)
    print("Exported to clipboard.")


def importProblem():
    global gridHeight, gridWidth, cellCenters, intersections, verticalEdges, horizontalEdges, cellSize, threshold, currentCursor
    # 常にIOフィールドをクリアして、クリップボードの内容を貼り付ける
    try:
        s = root.clipboard_get().strip()
        io_entry.delete(0, tk.END)
        io_entry.insert(0, s)
        print("Imported from clipboard.")
    except Exception as e:
        print("Clipboard error:", e)
        return

    try:
        data = json.loads(s)
    except Exception as e:
        print("Import error:", e)
        return

    gridHeight = data["gridHeight"]
    gridWidth = data["gridWidth"]
    cellCenters = data["cellCenters"]
    intersections = data["intersections"]
    verticalEdges = data["verticalEdges"]
    horizontalEdges = data["horizontalEdges"]

    height_entry.delete(0, tk.END)
    height_entry.insert(0, str(gridHeight))
    width_entry.delete(0, tk.END)
    width_entry.insert(0, str(gridWidth))
    cellSize = min(500 / gridWidth, 500 / gridHeight)
    threshold = cellSize * 0.3
    currentCursor = {"type": CELL, "i": 0, "j": 0}
    drawGrid()
    canvas.focus_set()


# --- 出力 (division 解答反映) ---
def outputArrays():
    problem = (cellCenters, intersections, verticalEdges, horizontalEdges)
    is_sat, region_id, division = SentaiShow.solve_sentai_show(gridHeight, gridWidth, problem)

    # 既存の division 描画は必ず削除
    canvas.delete("division")
    canvas.delete("explore")
    if is_sat:
        drawDivisionSolution(division)
    else:
        drawErrorDivision()


def drawDivisionSolution(division):
    """
    division は BoolGridFrame で、division.vertical と division.horizontal に解答が入っています。
    盤面の外枠は何もしません。
    """
    # 垂直エッジ：対象は j = 1 ... gridWidth-1, i = 0 ... gridHeight-1
    for i in range(gridHeight):
        for j in range(1, gridWidth):
            sol = division.vertical[i, j].sol if hasattr(division.vertical[i, j], "sol") else division.vertical[i, j]
            mid_x = j * cellSize
            mid_y = i * cellSize + cellSize / 2
            if sol is None:
                continue
            elif sol is True:
                # 緑色の縦線を、セル境界全体に沿って描画
                x0 = mid_x
                y0 = i * cellSize
                x1 = mid_x
                y1 = (i + 1) * cellSize
                canvas.create_line(x0, y0, x1, y1, fill="green", width=3, tags="division")
            elif sol is False:
                # 灰色の横線を、エッジ中央に短く描画（全長 cellSize*0.3）
                short = cellSize * 0.3
                x0 = mid_x - short / 2
                y0 = mid_y
                x1 = mid_x + short / 2
                y1 = mid_y
                canvas.create_line(x0, y0, x1, y1, fill="gray", width=3, tags="division")
    # 水平エッジ：対象は i = 1 ... gridHeight-1, j = 0 ... gridWidth-1
    for i in range(1, gridHeight):
        for j in range(gridWidth):
            sol = division.horizontal[i, j].sol if hasattr(division.horizontal[i, j], "sol") else division.horizontal[
                i, j]
            mid_x = j * cellSize + cellSize / 2
            mid_y = i * cellSize
            if sol is None:
                continue
            elif sol is True:
                # 緑色の横線を、セル境界全体に沿って描画
                x0 = j * cellSize
                y0 = mid_y
                x1 = (j + 1) * cellSize
                y1 = mid_y
                canvas.create_line(x0, y0, x1, y1, fill="green", width=3, tags="division")
            elif sol is False:
                # 灰色の縦線を、エッジ中央に短く描画
                short = cellSize * 0.3
                x0 = mid_x
                y0 = mid_y - short / 2
                x1 = mid_x
                y1 = mid_y + short / 2
                canvas.create_line(x0, y0, x1, y1, fill="gray", width=3, tags="division")


def drawErrorDivision():
    # すべての内部エッジに対して緑色の線を描画
    for i in range(gridHeight):
        for j in range(1, gridWidth):
            x0 = j * cellSize
            y0 = i * cellSize
            x1 = j * cellSize
            y1 = (i + 1) * cellSize
            canvas.create_line(x0, y0, x1, y1, fill="green", width=3, tags="division")
    for i in range(1, gridHeight):
        for j in range(gridWidth):
            x0 = j * cellSize
            y0 = i * cellSize
            x1 = (j + 1) * cellSize
            y1 = i * cellSize
            canvas.create_line(x0, y0, x1, y1, fill="green", width=3, tags="division")


# --- UI の構築 ---
root = tk.Tk()

root.title("Sentai Show Solver")

# 上段フレーム： Height, Width, Generate
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

tk.Label(top_frame, text="Height:").pack(side=tk.LEFT)
height_entry = tk.Entry(top_frame, width=5)
height_entry.insert(0, "10")
height_entry.pack(side=tk.LEFT, padx=2)
height_entry.bind("<FocusOut>", lambda e: canvas.focus_set())

tk.Label(top_frame, text="Width:").pack(side=tk.LEFT)
width_entry = tk.Entry(top_frame, width=5)
width_entry.insert(0, "10")
width_entry.pack(side=tk.LEFT, padx=2)
width_entry.bind("<FocusOut>", lambda e: canvas.focus_set())

gen_button = tk.Button(top_frame, text="Generate Grid", command=generateGrid)
gen_button.pack(side=tk.LEFT, padx=5)

# 中段フレーム： IO 入力と Save, Load ボタン
io_frame = tk.Frame(root)
io_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

tk.Label(io_frame, text="IO:").pack(side=tk.LEFT, padx=2)
io_entry = tk.Entry(io_frame, width=50)
io_entry.pack(side=tk.LEFT, padx=2)

save_button = tk.Button(io_frame, text="Save", command=exportProblem)
save_button.pack(side=tk.LEFT, padx=2)
load_button = tk.Button(io_frame, text="Load", command=importProblem)
load_button.pack(side=tk.LEFT, padx=2)

# 下段フレーム： キャンバス
canvas = tk.Canvas(root, width=500, height=500, bg="white")
canvas.pack(padx=5, pady=5)
canvas.bind("<Button-1>", onCanvasClick)
canvas.bind("<Key>", onKeyPress)
canvas.focus_set()

# Solve ボタンはキャンバス下に配置する
solve_frame = tk.Frame(root)
solve_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
out_button = tk.Button(solve_frame, text="Solve", command=outputArrays)
out_button.pack()

explore_button = tk.Button(solve_frame, text="search", command=exploreZeroCandidates)
explore_button.pack()

# 初回グリッド生成
generateGrid()

root.mainloop()
