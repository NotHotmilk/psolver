import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then, alldifferent, cond
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D

solver = Solver()

# 箱の定数
colors = ["RED", "BLUE", "GREEN", "YELLOW", "GRAY"]

AA = 0
BB = 1
CC = 2
DD = 3
EE = 4
P1 = 0
P2 = 1
P3 = 2
P4 = 3
P5 = 4
RED = 0
BLUE = 1
GREEN = 2
YELLOW = 3
GRAY = 4

# 正直者、嘘つき
is_honest = solver.bool_array(5)
solver.add_answer_key(is_honest)

# yがNAME、xがPRICE
NAMEandPRICEofRED = solver.bool_array((5, 5))
NAMEandPRICEofBLUE = solver.bool_array((5, 5))
NAMEandPRICEofGREEN = solver.bool_array((5, 5))
NAMEandPRICEofYELLOW = solver.bool_array((5, 5))
NAMEandPRICEofGRAY = solver.bool_array((5, 5))

layers = [NAMEandPRICEofRED, NAMEandPRICEofBLUE, NAMEandPRICEofGREEN, NAMEandPRICEofYELLOW, NAMEandPRICEofGRAY]

NAMEandPRICE = solver.bool_array((5, 5))
NAMEandCOLOR = solver.bool_array((5, 5))
COLORandPRICE = solver.bool_array((5, 5))

for layer in layers:
    solver.add_answer_key(layer)
solver.add_answer_key(NAMEandPRICE)
solver.add_answer_key(NAMEandCOLOR)
solver.add_answer_key(COLORandPRICE)

# それぞれの平面について、1つだけTrueであることを保証
for layer in layers:
    solver.ensure(count_true(layer) == 1)
for i in range(5):
    v1layer = []
    v2layer = []
    for layer in layers:
        v1layer.append(layer[i])
        v2layer.append(layer[:, i])
    solver.ensure(count_true(v1layer) == 1)
    solver.ensure(count_true(v2layer) == 1)

# NAMEandPRICEの制約
for y in range(5):
    for x in range(5):
        vline = []
        for layer in layers:
            vline.append(layer[y, x])
        solver.ensure(NAMEandPRICE[y, x] == fold_or(vline))

# NAMEandCOLORの制約
for y in range(5):
    for x in range(5):
        vline = layers[x][y]
        solver.ensure(NAMEandCOLOR[y, x] == fold_or(vline))

# COLORandPRICEの制約
for y in range(5):
    for x in range(5):
        vline = []
        vline = layers[y][:, x]
        solver.ensure(COLORandPRICE[y, x] == fold_or(vline))

# ここに問題のセリフを追加 カンマで区切ると特殊なandを意味する 文区切りでfold_andで囲う必要あり
# 簡単のためにすべて真実の箱とする
solver.ensure(fold_and(is_honest))

# AAの箱「AとDは同種の箱　AとBの箱は奇数ドルではない（偶数）　AAの箱は赤か青　　　実際は AとDは異種　AとBの箱は偶数ドルではない AAの箱は赤でも青でもない
ensuresA = [
    fold_and(
        ~NAMEandPRICE[AA, P2] & ~NAMEandPRICE[AA, P4],
        ~NAMEandPRICE[BB, P2] & ~NAMEandPRICE[BB, P4],
    ),
    ~NAMEandCOLOR[AA, RED] & ~NAMEandCOLOR[AA, BLUE],  # AAの箱は赤か青
]

# BBの箱「DとEは同類　赤と青にはの値段差は２ドル以下」　実際は　DとEは異種　赤の箱と青の箱には3ドル以上の値段差がある
ensuresB = [
    fold_or(
        (COLORandPRICE[RED, P1] & COLORandPRICE[BLUE, P4]),
        (COLORandPRICE[RED, P1] & COLORandPRICE[BLUE, P5]),
        (COLORandPRICE[RED, P2] & COLORandPRICE[BLUE, P5]),
        (COLORandPRICE[RED, P4] & COLORandPRICE[BLUE, P1]),
        (COLORandPRICE[RED, P5] & COLORandPRICE[BLUE, P2]),
    )
]

# CCの箱「AがCを虚偽の箱だといった　DとEの箱のどちらかが緑の箱である　Eの箱は4ドルである　真実
ensuresC = [
    NAMEandCOLOR[DD, GREEN] | NAMEandCOLOR[EE, GREEN],
    NAMEandPRICE[EE, P4],
]

# DDの箱「緑の箱と黄色の箱には奇数ドルある 真実
ensuresD = [
    fold_and(
        ~COLORandPRICE[GREEN, P4],
        ~COLORandPRICE[YELLOW, P4],
        ~COLORandPRICE[GREEN, P2],
        ~COLORandPRICE[YELLOW, P2],
    )
]

import itertools

# EEの箱「Eは緑の箱だ　Dの箱のほうがBより高い　Bは5ドルだ」　実際は Eは緑の箱ではない　Bの箱のほうがDの箱より高い値段である　Bは5ドルではない
ensuresE = [
    fold_or(
        NAMEandPRICE[BB, b] & NAMEandPRICE[DD, d] for b, d in itertools.product(range(5), range(5)) if b > d
    ),
    ~COLORandPRICE[BB, P5],
]

# 割り振りしないといけない
solver.ensure(
)

# ここまで

# すべてのルールをsolverに追加
EnsuresABCDE = [ensuresA, ensuresB, ensuresC, ensuresD, ensuresE]
AllEnsures = []

# 真実と虚偽の制約を追加
for i in range(5):
    ensuresX = EnsuresABCDE[i]
    if len(ensuresX) != 0:
        AllEnsures.append(then(is_honest[i], fold_and(ensuresX)))  # 真実の場合　すべてのセリフが正しい
        AllEnsures.append(then(~is_honest[i], ~fold_or(ensuresX)))  # 虚偽の場合　すべてのセリフが正しくない

# まとめる
for ensure in AllEnsures:
    solver.ensure(ensure)

is_sat = solver.solve()
if is_sat is False:
    print("No answer")
    exit()

MAP = {True: "o", False: "x", None: "_"}

for i in range(len(layers)):
    print(colors[i])
    print(stringify_array(layers[i], MAP))

print()
print("ANSWER")

for i in range(5):
    name = chr(ord("A") + i)
    if is_honest[i].sol == True:
        print(name + "は真実の箱")
    elif is_honest[i].sol == False:
        print(name + "は虚偽の箱")
    else:
        print(name + "は不明")

nap = stringify_array(NAMEandPRICE, MAP).split()
nap2 = [nap[5 * i:5 * (i + 1)] for i in range(5)]
nac = stringify_array(NAMEandCOLOR, MAP).split()
nac2 = [nac[5 * i:5 * (i + 1)] for i in range(5)]
cap = stringify_array(COLORandPRICE, MAP)

for i in range(5):
    print(*nap2[i], " ", *nac2[i])
print()
print(cap)
