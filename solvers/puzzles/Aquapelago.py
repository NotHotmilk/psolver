import cspuz
from cspuz import Solver, graph
from cspuz.constraints import count_true, fold_and, fold_or, then
from cspuz.puzzle.util import stringify_grid_frame, stringify_array, encode_array
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
import common_rules

#     let (h, w) = util::infer_shape(problem);
#
#     let mut solver = Solver::new();
#     let is_black = &solver.bool_var_2d((h, w));
#     solver.add_answer_key_bool(is_black);
#     solver.add_expr(!is_black.conv2d_and((1, 2))); // not adjacent black cells
#     solver.add_expr(!is_black.conv2d_and((2, 1)));
#     solver.add_expr(is_black.conv2d_or((2, 2))); // 2x2 white cells are not allowed
#     graph::active_vertices_connected_2d(&mut solver, !is_black);
#
#     let mut aux_graph = vec![];
#     let mut aux_sizes = vec![];
#     let mut aux_edges = vec![];
#
#     for y in 0..h {
#         for x in 0..w {
#             if let Some(n) = problem[y][x] {
#                 solver.add_expr(is_black.at((y, x)));
#                 if n > 0 {
#                     aux_sizes.push(Some(int_constant(n)));
#                 } else {
#                     aux_sizes.push(None);
#                 }
#             } else {
#                 aux_sizes.push(None);
#             }
#
#             if y < h - 1 {
#                 if x < w - 1 {
#                     aux_graph.push((y * w + x, (y + 1) * w + x + 1));
#                     aux_edges.push(!(is_black.at((y, x)) & is_black.at((y + 1, x + 1))));
#                 }
#                 if x > 0 {
#                     aux_graph.push((y * w + x, (y + 1) * w + x - 1));
#                     aux_edges.push(!(is_black.at((y, x)) & is_black.at((y + 1, x - 1))));
#                 }
#             }
#         }
#     }
#     solver.add_graph_division(&aux_sizes, &aux_graph, &aux_edges);

def solve_aquapelago(height, width, problem):
    solver = Solver()
    is_black = solver.bool_array((height, width))
    solver.add_answer_key(is_black)

    graph.active_vertices_not_adjacent(solver, is_black)
    common_rules.not_forming_2by2_square(solver, ~is_black)
    graph.active_vertices_connected(solver, ~is_black)

