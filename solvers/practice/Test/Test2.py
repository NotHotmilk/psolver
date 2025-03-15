CENTER = 0
INTERSECTION = 1
VERTICAL = 2
HORIZONTAL = 3


def reflect_cell(pos_type, sym_type, base, cell):
    b_y, b_x = base
    y, x = cell

    y *= 2
    x *= 2

    if pos_type == CENTER:
        b_y = b_y * 2
        b_x = b_x * 2
    elif pos_type == INTERSECTION:
        b_y = b_y * 2 + 1
        b_x = b_x * 2 + 1
    elif pos_type == VERTICAL:
        b_y = b_y * 2
        b_x = b_x * 2 + 1
    elif pos_type == HORIZONTAL:
        b_y = b_y * 2 + 1
        b_x = b_x * 2

    if sym_type == 1:
        # 水平反転：y成分だけ反転
        new_y = 2 * b_y - y
        new_x = x
    elif sym_type == 2:
        # 垂直反転：x成分だけ反転
        new_y = y
        new_x = 2 * b_x - x
    elif sym_type == 3:
        # 斜め "/" の反転：
        # 反転後の座標は (b_y - (x - b_x), b_x - (y - b_y))
        new_y = b_y - (x - b_x)
        new_x = b_x - (y - b_y)
    elif sym_type == 4:
        # 斜め "\" の反転：
        # 反転後の座標は (b_y + (x - b_x), b_x + (y - b_y))
        new_y = b_y + (x - b_x)
        new_x = b_x + (y - b_y)
    else:
        raise ValueError("Invalid symmetry type. Must be 1, 2, 3, or 4.")

    if new_y % 2 != 0 or new_x % 2 != 0:
        raise ValueError("Symmetry reflection is not an integer.")

    ry = new_y // 2
    rx = new_x // 2

    return (ry, rx)

