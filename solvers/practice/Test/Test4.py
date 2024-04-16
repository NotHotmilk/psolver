from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
import common_rules

problem = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1,  3, -1,  3,  3, -1, -1, -1],
    [-1, -1, -1,  1, -1, -1, -1, -1, -1],
    [ 2, -1, -1, -1,  2, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
]
height = len(problem)-1
width = len(problem[0])-1

solver = Solver()
is_black = solver.bool_array((height, width))
solver.add_answer_key(is_black)

common_rules.all_black_blocks_have_same_area(solver, is_black, height, width, 4)
common_rules.creek_like_around_number(solver, is_black, problem, height, width)
common_rules.not_forming_2by2_square(solver, is_black, False)


has_answer = solver.solve()
print(has_answer)

if has_answer:
    print(stringify_array(is_black, {True: '#', False: '.', None: '?'}))