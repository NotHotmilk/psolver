import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules


def solve_koburin(height, width, problem):
    solver = Solver()
    grid_frame = graph.BoolGridFrame(solver, height - 1, width - 1)
    is_passed = graph.active_edges_single_cycle(solver, grid_frame)
    black_cell = solver.bool_array((height, width))
    graph.active_vertices_not_adjacent(solver, black_cell)
    solver.add_answer_key(grid_frame)
    solver.add_answer_key(black_cell)

    for y in range(height):
        for x in range(width):
            if 0 <= problem[y][x] <= 5:
                solver.ensure(~is_passed[y, x])
                solver.ensure(~black_cell[y, x])

            if 0 <= problem[y][x] <= 4:
                solver.ensure(count_true(black_cell.four_neighbors(y, x)) == problem[y][x])

            else:
                solver.ensure(is_passed[y, x] != black_cell[y, x])

    is_sat = solver.solve()
    return is_sat, grid_frame, black_cell


def generate_koburin(height, width, verbose=False):

    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] == 5:
                    ret += 12
                # elif problem[y][x] == 4:
                #     ret += 30
                elif problem[y][x] != -1:
                    ret += 15 + problem[y][x] * 2

        return ret


    generated = generate_problem(
        lambda problem: solve_koburin(height, width, problem),
        builder_pattern=ArrayBuilder2D(
            height,
            width,
            range(-1, 6),
            default=-1,
        ),
        clue_penalty=penalty,
        verbose=verbose,
    )
    return generated


from cspuz.problem_serializer import (
    Grid,
    OneOf,
    Spaces,
    HexInt,
    DecInt,
    Dict,
    serialize_problem_as_url,
    deserialize_problem_as_url,
)

KOBULIN_COMBINATOR = Grid(OneOf(Spaces(-1, "g"), DecInt()))

def serialize_koburin(problem):
    height = len(problem)
    width = len(problem[0])
    return serialize_problem_as_url(KOBULIN_COMBINATOR, "koburin", height, width, problem)



if __name__ == '__main__':

    # height = 8
    # width = 8
    # problem = [
    #     [-1, -1, -1, -1, -1, -1, -1, -1],
    #     [-1, 2, -1, -1, -1, -1, -1, -1],
    #     [-1, -1, -1, -1, 2, -1, -1, -1],
    #     [-1, -1, -1, -1, -1, -1, -1, 2],
    #     [-1, -1, -1, -1, -1, -1, -1, -1],
    #     [2, -1, -1, -1, -1, -1, -1, -1],
    #     [-1, -1, -1, -1, -1, -1, -1, -1],
    #     [-1, -1, -1, -1, -1, -1, 2, -1],
    # ]

    height, width = 12, 12
    problem = generate_koburin(height, width, verbose=True)
    print(serialize_koburin(problem))

    is_sat, is_line, black_cell = solve_koburin(height, width, problem)
    print("has answer:", is_sat)
    if is_sat:
        print(stringify_grid_frame(is_line))
        print(stringify_array(black_cell, common_rules.BW_MAP))
