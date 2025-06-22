import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

_ = -1
X = 1
O = 0


def solve_isowatari(problem: list[list[any]], size: int):
    height, width = len(problem), len(problem[0])
    solver = Solver()

    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    graph.active_vertices_connected(solver, ~is_black)

    group_size = solver.int_array((height, width), 0, height * width)

    solver.ensure(is_black.then(group_size == size))
    common_rules.not_forming_2by2_square(solver, ~is_black)

    for y in range(height):
        for x in range(width):
            if problem[y][x] == X:
                solver.ensure(is_black[y, x])
            elif problem[y][x] == O:
                solver.ensure(~is_black[y, x])

    division_id = graph.division_connected_variable_groups(solver, shape=(height, width), group_size=group_size)

    for y in range(height - 1):
        for x in range(width):
            solver.ensure((is_black[y, x] == is_black[y + 1, x]) ==
                          (division_id[y, x] == division_id[y + 1, x]))

    for y in range(height):
        for x in range(width - 1):
            solver.ensure((is_black[y, x] == is_black[y, x + 1]) ==
                          (division_id[y, x] == division_id[y, x + 1]))

    is_sat = solver.solve()
    return is_sat, is_black


def generate_isowatari(height, width, size, verbose=True):
    generated = generate_problem(lambda problem: solve_isowatari(problem, size),
                                 builder_pattern=ArrayBuilder2D(height, width, [_, X, O], default=_),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=_, weight=5),
                                 verbose=verbose)
    return generated



from concurrent.futures import ProcessPoolExecutor

def solve_single(args):
    problem, size = args
    return solve_isowatari(problem, size)

def solve_mixed_isowatari(problem):
    sizes = [1, 2, 3, 4, 5, 6]
    with ProcessPoolExecutor() as executor:
        futures = executor.map(solve_single, [(problem, size) for size in sizes])
        results = list(futures)

    is_sat_all = all(result[0] for result in results)
    is_blacks = [result[1] for result in results]

    return is_sat_all, *is_blacks


def generate_mixed_isowatari(height, width, verbose=True):
    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] == X:
                    ret += 5
                elif problem[y][x] == O:
                    ret += 6
        return ret

    generated = generate_problem(lambda problem: solve_mixed_isowatari(problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [_, X, O], default=_),
                                 clue_penalty=penalty,
                                 verbose=verbose)
    return generated



def solve_wrapper(args):
    problem, i = args
    is_sat, is_black = solve_isowatari(problem, i)
    return i, is_sat, is_black

if __name__ == "__main__":
    # problem = [
    #     [_, _, _, _, X],
    #     [_, _, O, _, _],
    #     [_, _, _, _, _],
    #     [_, _, O, X, _],
    #     [_, _, _, O, _],
    # ]
    # 
    # with ProcessPoolExecutor() as executor:
    #     args_list = [(problem, i) for i in range(2, 6)]
    #     futures = [executor.submit(solve_wrapper, args) for args in args_list]
    #     for future in futures:
    #         i, is_sat, is_black = future.result()
    #         print(f"\ni = {i}")
    #         if is_sat:
    #             print("SAT")
    #             print(stringify_array(is_black, common_rules.BW_MAP))
    #         else:
    #             print("UNSAT")

    
    problem = generate_mixed_isowatari(4, 4, verbose=True)
    print("Generated problem:")
    print(stringify_array(problem, {_:".", X:"X", O:"O"}))

    for i in range(1, 7):
        print()
        is_sat, is_black = solve_isowatari(problem, i)
        if is_sat:
            print(stringify_array(is_black, common_rules.BW_MAP))