import sys
import subprocess

import cspuz
from cspuz import Solver, graph
from cspuz.grid_frame import BoolGridFrame
from cspuz.constraints import count_true, fold_or
from cspuz.puzzle import util
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
from cspuz.problem_serializer import (
    Grid,
    OneOf,
    Spaces,
    IntSpaces,
    serialize_problem_as_url,
    deserialize_problem_as_url,
)


def solve_slitherlink(height, width, problem, variant=None):
    solver = Solver()
    grid_frame = BoolGridFrame(solver, height, width)
    solver.add_answer_key(grid_frame)
    solver.ensure(fold_or(grid_frame))
    graph.active_edges_single_cycle(solver, grid_frame)

    for y in range(height):
        for x in range(width):
            if problem[y][x] >= 0:
                solver.ensure(count_true(grid_frame.cell_neighbors(y, x)) == problem[y][x])
    is_sat = solver.solve()
    return is_sat, grid_frame


def solve_slitherlink_variant(height, width, problem):
    solver = Solver()
    grid_frame1 = BoolGridFrame(solver, height, width)
    grid_frame2 = BoolGridFrame(solver, height, width)

    solver.ensure(fold_or(grid_frame1))
    solver.ensure(fold_or(grid_frame2))

    grid_frame = BoolGridFrame(solver, height, width)
    solver.add_answer_key(grid_frame)
    solver.ensure(grid_frame.horizontal == (grid_frame1.horizontal | grid_frame2.horizontal))
    solver.ensure(grid_frame.vertical == (grid_frame1.vertical | grid_frame2.vertical))

    # 通過するかどうか
    path1 = graph.active_edges_single_cycle(solver, grid_frame1)
    path2 = graph.active_edges_single_cycle(solver, grid_frame2)

    # ２つのループは交差・重複してはいけない
    solver.ensure(~(path1 & path2))

    is_inside = solver.bool_array((height, width))
    for y in range(height):
        for x in range(width):
            if y == 0:
                # 一番上のセルは、上方向に交差がなければ外 (False)
                solver.ensure(is_inside[y, x] == grid_frame1.horizontal[y, x])
            else:
                # 上のセルまでの交差の偶奇 XOR その境界上の線分
                solver.ensure(
                    is_inside[y, x]
                    == (is_inside[y - 1, x] != grid_frame1.horizontal[y, x])
                )
    for y in range(height):
        for x in range(width):
            solver.ensure(path2[y, x].then(is_inside[y, x]))

    for y in range(height):
        for x in range(width):
            if problem[y][x] >= 0:
                solver.ensure(
                    (count_true(grid_frame1.cell_neighbors(y, x)) + count_true(grid_frame2.cell_neighbors(y, x)))
                    == problem[y][x])
    is_sat = solver.solve()

    return is_sat, grid_frame


def generate_slitherlink(height, width, symmetry=False, verbose=False, disallow_adjacent=False):
    def no_neighboring_zero(problem):
        for y in range(height):
            for x in range(width):
                if problem[y][x] != 0:
                    continue
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        y2 = y + dy
                        x2 = x + dx
                        if (
                                (dy, dx) != (0, 0)
                                and 0 <= y2 < height
                                and 0 <= x2 < width
                                and problem[y2][x2] == 0
                        ):
                            return False
        return True

    generated = generate_problem(
        lambda problem: solve_slitherlink(height, width, problem),
        builder_pattern=ArrayBuilder2D(
            height,
            width,
            [-1, 0, 1, 2, 3],
            default=-1,
            symmetry=symmetry,
            disallow_adjacent=disallow_adjacent
            # [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            # [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] #disallow_adjacent,
        ),
        clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=5),
        pretest=no_neighboring_zero,
        verbose=verbose,
    )
    return generated


SLITHERLINK_COMBINATOR = Grid(OneOf(Spaces(-1, "g"), IntSpaces(-1, max_int=4, max_num_spaces=2)))


def serialize_slitherlink(problem):
    height = len(problem)
    width = len(problem[0])
    return serialize_problem_as_url(SLITHERLINK_COMBINATOR, "slither", height, width, problem)


def deserialize_slitherlink(url):
    return deserialize_problem_as_url(SLITHERLINK_COMBINATOR, url, allowed_puzzles="slither")


if __name__ == "__main__":
    # height, width = 10, 10
    # problem = generate_slitherlink(height, width, symmetry=True, verbose=True, disallow_adjacent=False)

    _ = -1
    problem = [
        [_, _, _, 3, _, _],
        [_, 3, _, _, _, 3],
        [_, _, 3, 3, _, _],
        [_, 2, _, _, 2, _],
        [2, _, 3, 3, _, _],
        [_, _, _, _, _, _],
    ]

    height = len(problem)
    width = len(problem[0])

    if problem is not None:
        print(util.stringify_array(problem, {-1: ".", 0: "0", 1: "1", 2: "2", 3: "3", 4: "4"}))
        print(flush=True)
        print(serialize_slitherlink(problem))
        
        import time
        start = time.time()

        sat, ans = solve_slitherlink_variant(height, width, problem)
        print(util.stringify_grid_frame(ans))
        
        print("time", time.time() - start)