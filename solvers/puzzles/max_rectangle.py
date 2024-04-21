def max_histogram_area_with_dimensions(heights):
    stack = []
    max_area = 0
    max_dims = (0, 0)  # (height, width)

    index = 0
    while index < len(heights):
        if not stack or heights[index] >= heights[stack[-1]]:
            stack.append(index)
            index += 1
        else:
            top_of_stack = stack.pop()
            width = index if not stack else index - stack[-1] - 1
            area = heights[top_of_stack] * width
            if area > max_area:
                max_area = area
                max_dims = (heights[top_of_stack], width)

    while stack:
        top_of_stack = stack.pop()
        width = index if not stack else index - stack[-1] - 1
        area = heights[top_of_stack] * width
        if area > max_area:
            max_area = area
            max_dims = (heights[top_of_stack], width)

    return max_area, max_dims

def max_rectangle_area_with_dimensions(problem):
    if not problem or not problem[0]:
        return 0, (0, 0)

    max_area = 0
    max_dims = (0, 0)
    height = len(problem)
    width = len(problem[0])
    histogram = [0] * width

    for i in range(height):
        for j in range(width):
            if problem[i][j]:
                histogram[j] += 1
            else:
                histogram[j] = 0
        # Calculate maximum area and dimensions for the current row's histogram
        area, dims = max_histogram_area_with_dimensions(histogram)
        if area > max_area:
            max_area = area
            max_dims = dims

    return max_area, max_dims

