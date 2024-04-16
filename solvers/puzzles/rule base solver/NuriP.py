# 前提条件


from z3 import *

problem = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]
y_keys = [0, 0, 0, 0]
x_keys = [0, 0, 0, 0]

height = len(problem)
width = len(problem[0])


def validate_problem():  # すべてのkeyやproblemは1以上の整数である
    for y in range(height):
        for x in range(width):
            if problem[y][x] < 0:
                return False
    for key in y_keys:
        if key < 0:
            return False
    for key in x_keys:
        if key < 0:
            return False
    return True


P = [[Bool(f"P_{y}_{x}") for x in range(width)] for y in range(height)]
s = Solver()


def rule_1_1():  # key<clueなマスは塗りつぶす
    for y in range(height):
        for x in range(width):
            if P[y][x] != True and P[y][x] != False:
                continue
            if problem[y][x] > y_keys or problem[y][x] > x_keys:
                s.add(P[y][x] == True)
                print(f"rule_1_1: P_{y}_{x} == True")
                return True


# def rule_1_2():  # 残ったマスの総和がkeyと一致するなら塗りつぶさない
#     for y in range(height):
#         for x in range(width):
#             if P[y][x] != True and P[y][x] != False:
#                 continue
#             if sum(P[y]) == y_keys[y]:


# rules_1が適用されなくなるまで繰り返す
def try_rules():
    while rule_1_1():
        pass
    # while rule_1_2():
