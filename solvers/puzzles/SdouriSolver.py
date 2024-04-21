import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D


def solve_sdouri(height, width, problem):
    solver = Solver()
    grid_frame = graph.BoolGridFrame(solver, height - 1, width - 1)
    solver.add_answer_key(grid_frame)

    is_passed = graph.active_edges_single_cycle(solver, grid_frame)

    # 点y,xで線がまっすぐに伸びるbool
    def is_straight(y, x):
        v = grid_frame.vertical[y - 1:y + 1, x]
        h = grid_frame.horizontal[y, x - 1:x + 1]
        return (count_true(v) == 2) ^ (count_true(h) == 2)

    for y in range(height):
        for x in range(width):
            if problem[y][x] != -1:
                solver.ensure(~is_passed[y, x])
                cells = [(y + dy, x + dx)
                         for dy in range(-1, 2)
                         for dx in range(-1, 2)
                         if 0 <= y + dy < height and 0 <= x + dx < width]
                solver.ensure(count_true([is_straight(y, x) for y, x in cells]) == problem[y][x])

    has_answer = solver.solve()
    return has_answer, grid_frame


def generate_sdouri(height, width, symmetry=False, verbose=False):
    def penalty(problem):
        ret = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] == 0:
                    ret += 16
                elif problem[y][x] == 6:
                    ret += 14
                elif problem[y][x] != -1:
                    ret += 10
        return ret

    def compute_score(ans: cspuz.grid_frame.BoolGridFrame):
        score = 0
        for a in ans:
            if a.sol is not None:
                score += 1
                if a.sol:
                    score += 1
        return score

    generated = generate_problem(lambda problem: solve_sdouri(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, [i for i in range(-1, 7)], default=-1,
                                                                symmetry=symmetry),
                                 clue_penalty=penalty,
                                 # lambda problem: count_non_default_values(problem, default=-1, weight=10),
                                 score=compute_score,
                                 verbose=verbose)
    return generated


def generatehxw(height, width):
    print("Generating")
    problem = generate_sdouri(height, width, symmetry=False, verbose=True)
    print(stringify_array(problem, str))
    link = 'https://puzz.link/p?tapaloop/{}/{}/{}'.format(width, height, encode_array(
        list(map(lambda row: list(map(lambda x: '_' if x == -1 else x, row)), problem))
    ))
    print(link)
    print(stringify_grid_frame(solve_sdouri(height, width, problem)[1]))
    return link


import multiprocessing


def parallel_generatehxw():
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(generatehxw_wrapper, range(4))
    return results


def generatehxw_wrapper(i):
    return generatehxw(8, 8)


if __name__ == '__main__':
    results = parallel_generatehxw()
    for result in results:
        print(result)
