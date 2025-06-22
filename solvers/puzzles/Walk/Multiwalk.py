from cspuz.puzzle.util import stringify_grid_frame
from cspuz.generator import generate_problem, ArrayBuilder2D
import Icewalk, Waterwalk, Forestwalk
from psolver.solvers.puzzles.Walk import Firewalk

from concurrent.futures import ProcessPoolExecutor, as_completed


def _solve_component(args):
    """
    Helper to call each walk solver in a separate process.
    args: tuple(name: str, height: int, width: int, field: list, num: list)
    returns: tuple(name, result tuple)
    """
    name, height, width, field, num = args
    if name == 'ice':
        return name, Icewalk.solve_icewalk(field, num)
    elif name == 'water':
        return name, Waterwalk.solve_waterwalk(field, num)
    elif name == 'fire':
        return name, Firewalk.solve_firewalk(field, num)
    elif name == 'forest':
        return name, Forestwalk.solve_forestwalk(field, num)
    else:
        raise ValueError(f"Unknown walk type: {name}")


def solve_multiwalk(height, width, problem):
    # Build initial field mask and clue numbers
    # field = [[problem[y][x] == -1 for x in range(width)] for y in range(height)]

    T = True
    F = False
    field_default = [
        [F, F, F, F, F, F, F],
        [F, T, T, T, T, T, F],
        [F, T, T, T, T, T, F],
        [F, F, F, F, F, F, F],
        [F, T, T, T, T, T, F],
        [F, T, T, T, T, T, F],
        [F, F, F, F, F, F, F],
    ]

    field = [[False for __ in range(width)] for __ in range(height)]

    for y in range(height):
        for x in range(width):
            if problem[y][x] == -2:
                field[y][x] = field_default[y][x]
            elif problem[y][x] == -1:
                field[y][x] = not field_default[y][x]
            else:
                field[y][x] = False

    num = [[problem[y][x] if problem[y][x] > 0 else 0 for x in range(width)] for y in range(height)]

    # Prepare tasks for parallel execution
    component_names = ['ice', 'fire', 'forest']
    args_list = [(name, height, width, field, num) for name in component_names]

    results = {}
    # Execute in parallel
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(_solve_component, args): name for args, name in zip(args_list, component_names)}
        for future in as_completed(futures):
            name = futures[future]
            try:
                comp_name, comp_result = future.result()
                results[comp_name] = comp_result
            except Exception as e:
                raise RuntimeError(f"Error in {name} solver: {e}")

    # Unpack results
    is_sat_ice, line_ice = results['ice']
    is_sat_fire, line_fire, fire_mode = results['fire']
    is_sat_forest, line_forest = results['forest']

    # Overall satisfiability
    is_sat = all([is_sat_ice, is_sat_fire, is_sat_forest])
    return is_sat, line_ice, line_fire, fire_mode, line_forest


def generate_multiwalk(height, width, verbose=False):
    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] == -1:
                    ret += 8
                elif problem[y][x] != -2:
                    ret += 10
        return ret

    # Use the parallelized solver
    generated = generate_problem(
        lambda problem: solve_multiwalk(height, width, problem),
        builder_pattern=ArrayBuilder2D(height, width,
                                       [-2, -1, 1, 2, 3, 4, 5, 6], default=-2),
        clue_penalty=penalty,
        verbose=verbose,
    )
    return generated


if __name__ == '__main__':
    height, width = 7, 7

    problem = generate_multiwalk(height, width, verbose=True)
    is_sat, line_ice, line_fire, fire_mode, line_forest = solve_multiwalk(height, width, problem)

    for y in range(height):
        print(problem[y])
    print()
    print("Icewalk line:\n", stringify_grid_frame(line_ice))
    print()
    print("Firewalk line:\n", stringify_grid_frame(line_fire))
    print()
    print("Forestwalk line:\n", stringify_grid_frame(line_forest))
