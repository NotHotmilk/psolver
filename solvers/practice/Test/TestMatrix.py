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
P1 = 5
P2 = 6
P3 = 7
P4 = 8
P5 = 9
RED = 10
BLUE = 11
GREEN = 12
YELLOW = 13
ASH = 14

def e名前と値段(name, price):
    if AA <= name <= EE and P1 <= price <= P5:
        return NAMEandPRICE[name, price%5]
    else:
        print("e名前と値段 Error")
        exit()

def e名前と色(name, color):
    if AA <= name <= EE and RED <= color <= ASH:
        return NAMEandCOLOR[name, color%5]
    else:
        print("e名前と色 Error")
        exit()

def e色と値段(color, price):
    if RED <= color <= ASH and P1 <= price <= P5:
        return COLORandPRICE[color%5, price%5]
    else:
        print("e色と値段 Error")
        exit()

# 正直者、嘘つき
is_honest = solver.bool_array(5)
solver.add_answer_key(is_honest)

# yがNAME、xがPRICE
NAMEandPRICEofRED = solver.bool_array((5, 5))
NAMEandPRICEofBLUE = solver.bool_array((5, 5))
NAMEandPRICEofGREEN = solver.bool_array((5, 5))
NAMEandPRICEofYELLOW = solver.bool_array((5, 5))
NAMEandPRICEofASH = solver.bool_array((5, 5))

layers = [NAMEandPRICEofRED, NAMEandPRICEofBLUE, NAMEandPRICEofGREEN, NAMEandPRICEofYELLOW, NAMEandPRICEofASH]

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

# AAの箱
ensuresA = [
    e名前と色(EE, RED)
]

# BBの箱
ensuresB = [
]

# CCの箱
ensuresC = [

]

# DDの箱
ensuresD = [

]

# EEの箱
ensuresE = [

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
