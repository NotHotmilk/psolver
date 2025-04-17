import matplotlib
matplotlib.use("TkAgg")  # または "Qt5Agg"
import matplotlib.pyplot as plt

from fractions import Fraction
from itertools import combinations
import math

# -------------------------------
# パラメータ設定：引く線分の本数（N = 1,2,3,4）
num_segments = 4  # 例: 2本の場合。ここを1,3,4に変更可能。
# -------------------------------

# 上辺の左側を0として、時計回りに0,1,...,7とする点の定義
points = [
    (Fraction(1, 3), Fraction(1)),      # 0: 上辺 左側
    (Fraction(2, 3), Fraction(1)),      # 1: 上辺 右側
    (Fraction(1), Fraction(2, 3)),      # 2: 右辺 上側
    (Fraction(1), Fraction(1, 3)),      # 3: 右辺 下側
    (Fraction(2, 3), Fraction(0)),      # 4: 下辺 右側
    (Fraction(1, 3), Fraction(0)),      # 5: 下辺 左側
    (Fraction(0), Fraction(1, 3)),      # 6: 左辺 下側
    (Fraction(0), Fraction(2, 3))       # 7: 左辺 上側
]

# 回転後の対応を得るための辞書
point_to_index = {p: i for i, p in enumerate(points)}

# 正方形の中心 (1/2, 1/2) 周りに90°回転する関数
def rotate_point(p):
    x, y = p
    return (Fraction(1) - y, x)

# 点を n回（90°ずつ）回転させる
def rotate_point_n(p, n):
    for _ in range(n):
        p = rotate_point(p)
    return p

# 線分は、端点のインデックスの組（小さい順）で表す
# seg を n回回転させたときの線分（対応する端点のインデックス）を返す
def rotate_segment(seg, n):
    i, j = seg
    rp_i = rotate_point_n(points[i], n)
    rp_j = rotate_point_n(points[j], n)
    i_new = point_to_index[rp_i]
    j_new = point_to_index[rp_j]
    return tuple(sorted((i_new, j_new)))

# 8点から2点ずつ選んで作る線分全体（全部で28本）を作成
all_segments = [tuple(sorted(seg)) for seg in combinations(range(8), 2)]

# その中から、端点が重ならない num_segments 本の線分を選ぶ
drawings = []
for segs in combinations(all_segments, num_segments):
    endpoints = set()
    for seg in segs:
        endpoints.update(seg)
    # エンドポイントが重なっていなければ、各線分が独立（2*num_segments 個の点）
    if len(endpoints) == 2 * num_segments:
        drawing = tuple(sorted(segs))
        drawings.append(drawing)
drawings = list(set(drawings))
print("全体の引き方（重複含む）は", len(drawings), "通りです。")

# 各 drawing について、0°,90°,180°,270°回転させたときの表現の中で
# 辞書順（レキシコグラフィック）で最小のものを正準代表として返す。
def canonical(drawing):
    orbit = []
    for n in range(4):
        rotated = tuple(sorted([rotate_segment(seg, n) for seg in drawing]))
        orbit.append(rotated)
    return min(orbit)

# 各 drawing の正準代表を集め、一意なものだけ残す
canonical_set = set(canonical(d) for d in drawings)
# 辞書順に並び替える（canonical representation はタプルなので自然に辞書順ソートされます）
sorted_solutions = sorted(canonical_set)

print("回転対称を考慮した場合の引き方の個数は:", len(sorted_solutions), "通りです。")
print("辞書順に並び替えた解:")
for sol in sorted_solutions:
    print(sol)

# ----------------------------------
# 以下、図示用の関数
# ----------------------------------

# Fraction を float に変換
def to_float(point):
    return (float(point[0]), float(point[1]))

# 正方形と8点を描画する関数
def draw_square(ax):
    square_x = [0, 1, 1, 0, 0]
    square_y = [0, 0, 1, 1, 0]
    ax.plot(square_x, square_y, 'k-')
    for p in points:
        fp = to_float(p)
        ax.plot(fp[0], fp[1], 'ko', markersize=4)

# 指定の drawing（線分群）を描画する関数
def plot_drawing(ax, drawing, title=""):
    draw_square(ax)
    for seg in drawing:
        p1 = to_float(points[seg[0]])
        p2 = to_float(points[seg[1]])
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', linewidth=2)
    ax.set_aspect('equal')
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_title(title, fontsize=10)
    ax.axis('off')

# 図示（例として全解をグリッド表示）
num_drawings = len(sorted_solutions)
ncols = math.ceil(math.sqrt(num_drawings))
nrows = math.ceil(num_drawings / ncols)
fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*2.5, nrows*2.5))
axes = axes.flatten()

for i, sol in enumerate(sorted_solutions):
    plot_drawing(axes[i], sol, title=f"Case {i+1}")
for j in range(i+1, len(axes)):
    axes[j].axis('off')

plt.tight_layout()
plt.show()
