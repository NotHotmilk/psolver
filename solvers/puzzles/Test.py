import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

WHITE = 0
BLACK = 1
GRAY = 2


def solve_test(height, width, problem):
    solver = Solver()
    cells = solver.int_array((height, width), 0, 2)
    solver.add_answer_key(cells)

    # for y in range(height):
    #     for x in range(width):
    #         if problem[y][x] != -1:
    #             solver.ensure(cells[y, x] == problem[y][x])

    for y in range(height):
        for x in range(width):
            if problem[y][x] != -1:
                solver.ensure(cells[y, x] == WHITE)
                solver.ensure(count_true(
                    cells[max(0, y - 1):min(y + 2, height), max(0, x - 1):min(x + 2, width)] == GRAY
                ) == problem[y][x])

    # for y in range(height):
    #     for x in range(width):
    #         solver.ensure(
    #             count_true(
    #                 cells[max(0, y - 1):min(y + 2, height), max(0, x - 1):min(x + 2, width)] == GRAY
    #             )
    #             <= 1
    #         )

    common_rules.not_forming_2by2_square(solver, (cells == WHITE) | (cells == GRAY))
    graph.active_vertices_not_adjacent(solver, cells == GRAY)
    graph.active_vertices_connected(solver, (cells == GRAY) | (cells == BLACK))
    graph.active_vertices_connected(solver, (cells == WHITE) | (cells == GRAY))

    # for y in range(height):
    #     for x in range(width):
    #         solver.ensure(then(cells[y, x] == BLACK, count_true(
    #             cells[max(0, y - 1):min(y + 2, height), x] == BLACK,
    #             cells[y, max(0, x - 1):min(x + 2, width)] == BLACK
    #         ) == 3))

    common_rules.all_black_blocks_have_same_area_2(solver, cells == BLACK, problem, height, width)

    has_answer = solver.solve()
    return has_answer, cells


def generate_test(height, width, symmetry=False, verbose=False):
    generated = generate_problem(lambda problem: solve_test(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [-1, 0, 1, 2, 3, 4], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=10),
                                 verbose=verbose)
    return generated


from Shugaku import serialize_shugaku


def generatehxw(height, width):
    print("Generating")
    problem = generate_test(height, width, symmetry=False, verbose=True)
    has_answer, answer = solve_test(height, width, problem)

    print(stringify_array(problem, {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "x", -1: "."}))
    print()
    print(stringify_array(answer, {BLACK: '##', WHITE: '..', GRAY: '()', None: '??'}))
    print()
    print(serialize_shugaku(problem))

    return serialize_shugaku(problem)


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(generatehxw_wrapper, range(4))
    return results


def generatehxw_wrapper(_):
    return generatehxw(8, 8)


if __name__ == "__main__":
    results = parallel_generatehxw()
    print("Result")
    for result in results:
        print(result)

# if __name__ == '__main__':
#     height = 6
#     width = 6
#     problem = [
#         [-1, 3, -1, -1, 1, -1],
#         [-1, -1, -1, 2, -1, -1],
#         [-1, -1, -1, -1, -1, -1],
#         [-1, -1, 0, -1, -1, -1],
#         [-1, -1, -1, -1, 2, -1],
#         [-1, -1, -1, -1, -1, -1],
#     ]
#
#     height = 6
#     width = 6
#     problem = [
#         [-1, -1, -1, -1, -1, 0],
#         [1, -1, 4, -1, -1, -1],
#         [-1, -1, -1, -1, 1, -1],
#         [-1, -1, -1, -1, -1, -1],
#         [-1, 2, -1, -1, -1, -1],
#         [-1, -1, -1, -1, -1, -1],
#     ]
#
#     has_answer, answer = solve_test(height, width, problem)
#     if has_answer:
#         print(stringify_array(answer, {
#             BLACK: '##',
#             WHITE: '..',
#             GRAY: '()',
#             None: '??'
#         }))
#     else:
#         print('no answer')
