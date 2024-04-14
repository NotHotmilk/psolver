from cspuz import Solver, graph
from cspuz.constraints import fold_or, fold_and, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.array import BoolArray2D
# 2*2禁
def not_forming_2by2_square(solver: Solver, height, width, array2d: cspuz.array.BoolArray2D):
    solver.ensure(
        array2d
    )