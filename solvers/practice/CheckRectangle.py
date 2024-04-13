import unittest

def is_rectangle_formed2(problem):
    height = len(problem)
    width = len(problem[0])
    visited = [[False for _ in range(width)] for _ in range(height)]

    def dfs(x, y, block):
        if x < 0 or y < 0 or x >= height or y >= width or visited[x][y] or problem[x][y] == 0:
            return
        visited[x][y] = True
        block.append((x, y))

        dfs(x + 1, y, block)
        dfs(x - 1, y, block)
        dfs(x, y + 1, block)
        dfs(x, y - 1, block)

    def check_rectangle(block):
        if not block:
            return True
        min_x = min(block, key=lambda x: x[0])[0]
        max_x = max(block, key=lambda x: x[0])[0]
        min_y = min(block, key=lambda x: x[1])[1]
        max_y = max(block, key=lambda x: x[1])[1]

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if (x, y) not in block:
                    return False
        return True

    for i in range(height):
        for j in range(width):
            if problem[i][j] == 1 and not visited[i][j]:
                block = []
                dfs(i, j, block)
                if not check_rectangle(block):
                    return False
    return True


#   11
#   10 のパターンを許さない
def is_rectangle_formed(problem):
    height = len(problem)
    width = len(problem[0])

    for x in range(height - 1):
        for y in range(width - 1):
            if problem[x][y] + problem[x + 1][y] + problem[x][y + 1] + problem[x + 1][y + 1] == 3:
                return False
    return True



class TestCheckRectangle(unittest.TestCase):
    def test_1(self):
        problem = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_2(self):
        problem = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
        self.assertFalse(is_rectangle_formed(problem))

    def test_3(self):
        problem = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_4(self):
        problem = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_5(self):
        problem = [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_6(self):
        problem = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_7(self):
        problem = [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_8(self):
        problem = [[1, 1, 0], [1, 1, 1], [0, 1, 1]]
        self.assertFalse(is_rectangle_formed(problem))

    def test_9(self):
        problem = [[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]]
        self.assertFalse(is_rectangle_formed(problem))

    def test_10(self):
        problem = [[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]]
        self.assertFalse(is_rectangle_formed(problem))

    def test_11(self):
        problem = [[1, 1, 1, 1, 1]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_12(self):
        problem = [[1], [1], [1], [1], [1]]
        self.assertTrue(is_rectangle_formed(problem))

    def test_13(self):
        problem = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
        self.assertFalse(is_rectangle_formed(problem))

    def test_14(self):
        problem = [
            [1, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
        ]
        self.assertFalse(is_rectangle_formed(problem))

    def test_15(self):
        problem = [
            [1, 0, 0, 0],
            [0, 1, 1, 1],
            [0, 1, 1, 1],
            [0, 1, 1, 0],
        ]
        self.assertFalse(is_rectangle_formed(problem))

    def test_16(self):
        problem = [
            [1, 0, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 1, 0, 0],
        ]
        self.assertTrue(is_rectangle_formed(problem))


if __name__ == '__main__':
    unittest.main()
