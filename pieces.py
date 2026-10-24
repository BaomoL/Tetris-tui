# piece class represents the current active piece, includes methods for movement and attributes for shape

class Piece:

    #kick list determines series of hypothetical positions when rotating; return the first valid one
    # y and x values are switched to account for rows before columns in a list matrix

    jlstz_kicks = {
    (0, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (2, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)]}

    i_kicks = {
    (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
    (1, 0): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
    (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],
    (2, 1): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
    (2, 3): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],
    (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],
    (3, 0): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],
    (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)]}

    mirror_kicks= {
    (0, 2): [(0, 0), (0, -1)],
    (1, 3): [(0, 0), (1, 0)],
    (2, 0): [(0, 0), (0, 1)],
    (3, 1): [(0, 0), (-1, 0)]}
    # number determines character representing piece <- pulled from dictionary set at the beginning
    shapes = {
        't': [[0, 2, 0],
              [2, 2, 2],
              [0, 0, 0]],

        'z': [[3, 3, 0],
              [0, 3, 3],
              [0, 0, 0]],

        's': [[0, 4, 4],
              [4, 4, 0],
              [0, 0, 0]],

        'i': [[0, 0, 0, 0],
              [5, 5, 5, 5],
              [0, 0, 0, 0],
              [0, 0, 0, 0]],

        'l': [[0, 0, 6],
              [6, 6, 6],
              [0, 0, 0]],

        'j': [[7, 0, 0],
              [7, 7, 7],
              [0, 0, 0]],

        'o': [[8, 8],
              [8, 8]],
    }

    def __init__(self, shape, x, y):
        assert shape in Piece.shapes
        self.x = x
        self.y = y
        self.state = 0
        self.type = shape
        self.last_move = None

        # copy piece shape onto shape (list comprehension avoids shallow copy)

        self.shape = [row[:] for row in Piece.shapes[shape]]

    # direction only altered if it passes the validity check

    def move(self, board, direction):
        assert direction in ('left', 'right', 'down')
        if direction == 'left':
            dx = -1
            dy = 0
        elif direction == 'right':
            dx = 1
            dy = 0
        elif direction == 'down':
            dy = 1
            dx = 0
        if board.is_valid(self, dx=dx, dy=dy):
            self.last_move = 'move'
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    # rotation check if new position is valid, if not then tests series of kick positions
    
    def rotate(self, board, direction):
        assert direction in ('c', 'cc', '180')
        if self.type == 'o':
            return
        elif direction == '180':
            kick =self.mirror_kicks
        elif self.type in ('j', 'l', 's', 't', 'z'):
            kick = self.jlstz_kicks
        elif self.type == 'i':
            kick = self.i_kicks

        if direction == 'c':
            new_shape = rotate_c(self.shape)
            new_state = (self.state + 1) % 4

        elif direction == 'cc':
            new_shape = rotate_c(rotate_c(rotate_c(self.shape)))
            new_state = (self.state - 1) % 4

        else:
            new_shape = rotate_c(rotate_c(self.shape))
            new_state = (self.state + 2) % 4

        for dx, dy in kick[(self.state, new_state)]:
            if board.is_valid(self, new_shape, dx, dy):
                self.shape = new_shape
                self.x += dx
                self.y += dy
                self.state = new_state
                self.last_move = 'rotate'
                return True
            
        return False

#rotate piece clockwise

def rotate_c(matrix):
    
    n = len(matrix)
    result = [[0] * n for _ in range(n)]

    for r in range(n):
        for c in range(n):
            result[c][n - 1 - r] = matrix[r][c]

    return result

