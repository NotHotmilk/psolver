import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

#
# problem = [
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1,  3, -1,  3,  3, -1, -1, -1],
#     [-1, -1, -1,  1, -1, -1, -1, -1, -1],
#     [ 2, -1, -1, -1,  2, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
# ]
# problem = [
#     [-1, -1, -1, -1, -1, -1, -1],
#     [-1,  1, -1,  1, -1,  1, -1],
#     [-1, -1, -1, -1, -1, -1, -1],
#     [-1,  1, -1,  1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1,  4, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1],
# ]
# problem = [
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1, -1,  3, -1, -1, -1,  1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1,  2, -1,  3, -1,  3,  3, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1,  3,  1, -1,  3,  2, -1, -1,  1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
#     [-1, -1, -1,  1, -1,  1, -1, -1, -1],
#     [-1, -1, -1, -1, -1, -1, -1, -1, -1],
# ]
# height = len(problem)-1
# width = len(problem[0])-1
#
# solver = Solver()
# is_black = solver.bool_array((height, width))
# solver.add_answer_key(is_black)
#
# common_rules.all_black_blocks_have_same_area(solver, is_black, height, width, 4)
# common_rules.creek_like_around_number(solver, is_black, problem, height, width)
# common_rules.not_forming_2by2_square(solver, is_black, False)
#
#
# has_answer = solver.solve()
# print(has_answer)
#
# if has_answer:
#     print(stringify_array(is_black, {True: '#', False: '.', None: '?'}))

def solve_original(width, height, problem):
    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    common_rules.all_black_blocks_have_same_area(solver, is_black, height, width, 4)
    common_rules.creek_like_around_number(solver, is_black, problem, height, width)
    common_rules.not_forming_2by2_square(solver, is_black, False)

    has_answer = solver.solve()
    return has_answer, is_black

def generate_original(height, width, symmetry=False, verbose=False):
    generated = generate_problem(lambda problem: solve_original(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height+1, width+1, [-1, 0, 1, 2, 3], default=-1, symmetry=symmetry),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=8),
                                 verbose=verbose)
    return generated

if __name__ == "__main__":
    p = generate_original(8, 8, symmetry=False, verbose=True)
    print(p)
    # p = [
    #  [-1, -1, -1, -1, -1, -1, -1],
    #  [-1, -1, -1, -1, -1, -1, -1],
    #  [-1,  4, -1, -1, -1,  1, -1],
    #  [-1, -1, -1, -1,  4, -1, -1],
    #  [-1, -1, -1, -1, -1, -1, -1],
    #  [-1, -1, -1, -1, -1, -1, -1],
    #  [-1,  1,  1, -1, -1, -1, -1]
    #  ]
    print(stringify_array(solve_original(8, 8, p)[1], {True: '#', False: '.', None: '?'}))
[[-1, -1, -1, -1, -1,  0, -1, -1, -1],
 [-1, -1, -1,  3, -1, -1,  2, -1, -1],
 [-1, -1, -1, -1,  2, -1, -1, -1, -1],
 [ 1, -1, -1, -1,  3, -1, -1, -1,  0],
 [-1,  3,  3, -1,  1, -1, -1, -1, -1],
 [-1, -1,  1, -1, -1, -1, -1, -1, -1],
 [-1, -1, -1, -1, -1, -1, -1, -1, -1],
 [-1, -1,  1, -1, -1, -1, -1, -1,  2],
 [ 1, -1, -1, -1, -1, -1, -1, -1, -1]]

