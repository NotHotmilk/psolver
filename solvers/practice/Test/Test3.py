from solvers.puzzles.common_rules import *

problem = [
    [-1, -1, -1, -1, -1, -1],
    [-1,  7, -1, -1,  7, -1],
    [-1, -1, -1, -1, -1, -1],
    [-1, -1, -1,  5, -1, -1],
    [-1,  6, -1, -1,  7, -1],
    [-1, -1, -1, -1, -1, -1],

]
height = len(problem)
width = len(problem[0])

solver = Solver()
is_black = solver.bool_array((height, width))
solver.add_answer_key(is_black)

rule_not_forming_2by2_square(solver, is_black)

rule_minesweeper_like_around_number(solver, is_black, problem, height, width)


has_answer = solver.solve()
print(has_answer)

if has_answer:
    print(stringify_array(is_black, {True: '#', False: '.', None: '?'}))
