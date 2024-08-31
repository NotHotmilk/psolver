import numpy as np


def rotate_90(matrix):
    return list(zip(*matrix[::-1]))


def rotate_180(matrix):
    return rotate_90(rotate_90(matrix))


def rotate_270(matrix):
    return rotate_90(rotate_180(matrix))


def transform_matrix(matrix):
    l = len(matrix) // 2
    top_left = [row[:l] for row in matrix[:l]]
    top_right = [row[l:] for row in matrix[:l]]
    bottom_left = [row[:l] for row in matrix[l:]]
    bottom_right = [row[l:] for row in matrix[l:]]

    top_right_rotated = rotate_90(top_right)
    bottom_right_rotated = rotate_180(bottom_right)
    bottom_left_rotated = rotate_270(bottom_left)

    new_matrix = []

    for i in range(l):
        new_matrix.append(list(top_left[i]) + list(top_right_rotated[i]))
    for i in range(l):
        new_matrix.append(list(bottom_left_rotated[i]) + list(bottom_right_rotated[i]))

    return new_matrix


def transform_matrix_with_fixed_edges(matrix, l):
    size = 2 * l + 3
    new_matrix = [row[:] for row in matrix]

    # Extract submatrices
    top_left = [row[1:l + 1] for row in matrix[1:l + 1]]
    top_right = [row[l + 2:2 * l + 2] for row in matrix[1:l + 1]]
    bottom_left = [row[1:l + 1] for row in matrix[l + 2:2 * l + 2]]
    bottom_right = [row[l + 2:2 * l + 2] for row in matrix[l + 2:2 * l + 2]]

    # Rotate submatrices
    top_right_rotated = rotate_90(top_right)
    bottom_right_rotated = rotate_180(bottom_right)
    bottom_left_rotated = rotate_270(bottom_left)

    # Place rotated submatrices back into the new matrix
    for i in range(l):
        new_matrix[1 + i][l + 2:2 * l + 2] = top_right_rotated[i]
        new_matrix[l + 2 + i][l + 2:2 * l + 2] = bottom_right_rotated[i]
        new_matrix[l + 2 + i][1:l + 1] = bottom_left_rotated[i]

    return new_matrix

#
#
# input_matrix = [
#     [ 1,  2,  3,  4,  5,  6,  7,  8],
#     [ 9, 10, 11, 12, 13, 14, 15, 16],
#     [17, 18, 19, 20, 21, 22, 23, 24],
#     [25, 26, 27, 28, 29, 30, 31, 32],
#     [33, 34, 35, 36, 37, 38, 39, 40],
#     [41, 42, 43, 44, 45, 46, 47, 48],
#     [49, 50, 51, 52, 53, 54, 55, 56],
#     [57, 58, 59, 60, 61, 62, 63, 64]
# ]
#
#
# output_matrix = transform_matrix(input_matrix)
# for row in output_matrix:
#     print(row)


#
# # Test case
# l = 2
# input_matrix = [
#     [0, 1, 2, 3, 4, 5, 6],
#     [7, 8, 9, 10, 11, 12, 13],
#     [14, 15, 16, 17, 18, 19, 20],
#     [21, 22, 23, 24, 25, 26, 27],
#     [28, 29, 30, 31, 32, 33, 34],
#     [35, 36, 37, 38, 39, 40, 41],
#     [42, 43, 44, 45, 46, 47, 48]
# ]
#
# output_matrix = transform_matrix_with_fixed_edges(input_matrix, l)
# for row in output_matrix:
#     print(row)
