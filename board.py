import sys
from config import space, height, border, ghost_piece, padding, t, z, s, i, l, j, o, all_pieces
from pieces import Piece

# determine the character representing each piece; taken from config

def piece_color(t = None, z = None, s = None, i = None, l = None, j = None, o = None, all_pieces = None):

    piece_colors = {}

    if not all_pieces:
        piece_colors['2'] = t
        piece_colors['3'] = z
        piece_colors['4'] = s
        piece_colors['5'] = i
        piece_colors['6'] = l
        piece_colors['7'] = j
        piece_colors['8'] = o
    else:
        for x in range(2, 9):
            piece_colors[str(x)] = all_pieces

    return piece_colors

# function for converting time to time format

def format_time(seconds):

    minutes, seconds = divmod(int(seconds), 60)

    return f'{minutes:02d}:{seconds:02d}'

# board class represents current active board

class Board:

    piece_colors = piece_color(t, z, s, i, l, j, o, all_pieces)
    empty_row = '100000000001'
    floor_row = '111111111111'

    # create 22x12 board, 1s represent borders and 0s represent empty space

    def __init__(self):
        self.grid = [list(Board.empty_row) for _ in range ( 21)] + [list(Board.floor_row)]
        self.placed_pieces = 0

    # render is in charge of displaying current game state; called whenever there is a change

    def render(self, piece, held_piece, upcoming, 
               combo, score, elapsed_time, place_type, 
               game_mode, lines_cleared, level, sprint, ultra):

        #create duplicate board (bored) to make changes (display the piece) to before printing

        bored = [row[:] for row in self.grid]

        for y in range(2):
            bored[y][0] = '0'
            bored[y][-1] = '0'

        for piece_y in range(len(piece.shape)):
            for piece_x in range(len(piece.shape[piece_y])):
                
                board_x = piece.x + piece_x
                board_y = piece.y + piece_y
                if piece.shape[piece_y][piece_x]:
                    bored[board_y][board_x] = str(piece.shape[piece_y][piece_x])

        #simulate an extra piece that falls until it can't anymore; displayed as ghost piece

        ghost_y = piece.y

        ghost_y += self.drop_distance(piece)
            
        for y in range(len(piece.shape)):
            for x in range(len(piece.shape[y])):
                if piece.shape[y][x]:
                    if bored[ghost_y + y][piece.x + x] not in self.piece_colors:
                        bored[ghost_y + y][piece.x + x] = '9'

        board_lines = []

        hold_lines = [space * 5] * 2

        # creates held piece and makes a list matrix to display it

        if held_piece:
            for y in range(len(held_piece.shape)):
                parts = []
                for x in range(len(held_piece.shape[y])):
                    if held_piece.shape[y][x]:
                        parts.append(Board.piece_colors[str(held_piece.shape[y][x])])
                    else:
                        parts.append(space)
                parts.append(space * (5 - len(held_piece.shape[y])))
                hold_lines.append(''.join(parts))

        # same process for upcoming pieces

        next_lines = [space * 5] * 2

        # grab just the shapes of the pieces from dictionary

        for pieces in upcoming:
            pieces = [row[:] for row in Piece.shapes[pieces]]
            for y in range(len(pieces)):
                parts = []
                for x in range(len(pieces[y])):
                    if pieces[y][x]:
                        parts.append(Board.piece_colors[str(pieces[y][x])])
                    else:
                        parts.append(space)
                next_lines.append(''.join(parts))
            next_lines.append('')

        # turns current piece and ghost piece (as determined from earlier) into characters (along with everything else)
        
        for y in bored:
            parts = []
            for x in y:
                if x in Board.piece_colors:
                    parts.append(Board.piece_colors[x])
                elif x == '9':
                    parts.append(ghost_piece)
                elif x == '1':
                    parts.append(border)
                else:
                    parts.append(space)
            board_lines.append(''.join(parts))

        # appends both held piece and queued pieces to left and right by appending each row's list at a time

        for i in range(len(board_lines)):

            left = hold_lines[i] if i < len(hold_lines) else space * 5
            right = next_lines[i] if i < len(next_lines) else ''
            board_lines[i] = ''.join([left, board_lines[i], space * 2, right])

        board_lines = [row for row in board_lines for _ in range(height)]

        board_lines = ['', '', ''] + board_lines
        row = board_lines[2 + height * 1]

        # get width to ensure proper spacing before the "next"

        right_width = len(space * 5)

        board_lines[2 + height * 1] = ' HOLD'.ljust(10) + row[10:len(row) - right_width] + 'NEXT'

        # append all game states to the bottom of the board (with a space to keep it centered)

        board_lines.append('')

        # print specific game mode stats

        if game_mode == 'Sprint':
            board_lines.append(space * 7 + f'{game_mode} | {lines_cleared}/{sprint}')

        if game_mode == 'Marathon':
            board_lines.append(space * 7 + f'{game_mode} | Level: {level}')

        if game_mode == 'Hardcore':
            board_lines.append(space * 7 + f'{game_mode} | Level: {level}')

        if game_mode == 'Ultra':
            board_lines.append(space * 7 + f'{game_mode} | {format_time(elapsed_time)}/{format_time(ultra)}')

        board_lines.append('')
        board_lines.append(space * 7 + f'Score: {int(score)}')
        board_lines.append(space * 7 + f'Elapsed Time: {format_time(elapsed_time)}')
        board_lines.append(space * 7 + f'Combo: {combo}')
        board_lines.append(space * 7 + f'Placed: {self.placed_pieces}')

        board_lines.insert(0, '')
        board_lines.insert(0, '')

        if elapsed_time > 0:
            board_lines.append(space * 7 + f'PPS: {round(self.placed_pieces/elapsed_time, 2)}')
        else:
            board_lines.append(space * 7 + 'PPS:')
        if place_type:
            board_lines.append(space * 7 + place_type)
        else:
            board_lines.append('')

        board_lines.append('')
        board_lines.append('')

        # potentially shift everything to the right if the player so chooses (padding)

        board_lines = [space * padding + row for row in board_lines]

        # display the board
        
        sys.stdout.write(
            '\033[H' +
            '\n'.join(row + '\033[K' for row in board_lines) +
            '\033[J')      
        sys.stdout.flush()

    # gauge how far a piece can drop

    def drop_distance(self, piece):

        distance = 1

        while self.is_valid(piece, dy = distance):
            distance += 1

        return distance - 1

    # permanently append the piece to the real board

    def lock_piece(self, piece):

        for piece_y in range(len(piece.shape)):
            for piece_x in range(len(piece.shape[piece_y])):
                
                board_x = piece.x + piece_x
                board_y = piece.y + piece_y

                if piece.shape[piece_y][piece_x]:
                    self.grid[board_y][board_x] = str(piece.shape[piece_y][piece_x])

        self.placed_pieces += 1

    # check if a clear is a perfect clear (clears entire board)

    def perfect_clear(self):

        return all(cell == '0' for row in self.grid[:-1] for cell in row[1:-1])

    # checks if any given move is valid (allows a proposed shape if a spin is involved <- used for kick positions)

    def is_valid(self, piece, proposed = None, dx=0, dy=0):

        shape = proposed if proposed is not None else piece.shape

        for piece_y in range(len(shape)):
            for piece_x in range(len(shape[piece_y])):
                if shape[piece_y][piece_x]:

                    board_x = piece.x + piece_x + dx
                    board_y = piece.y + piece_y + dy

                    if not (0 <= board_x < len(self.grid[0]) and
                            0 <= board_y < len(self.grid)):
                        return False

                    if self.grid[board_y][board_x] == '1' or self.grid[board_y][board_x] in self.piece_colors:
                        return False
        return True

    # check of conditions for a t-spin is met: last successful move was a spin AND at least 3 corners are covered

    def detect_t_spin(self, piece):
        corners_covered = 0
        if piece.type == 't':
            for x in [0, 2]:
                for y in [0, 2]:
                    if self.grid[piece.y + y][piece.x + x] != '0':
                        corners_covered += 1
    
        if piece.last_move == 'rotate' and corners_covered >= 3:

            return True

        return False

    # check and clear rows that are filled

    def clear_rows(self):

        cleared = 0

        for y in range(0, len(self.grid) - 1):
            if all(x in self.piece_colors for x in self.grid[y][1:-1]):
                self.grid.pop(y)
                self.grid.insert(0, list(Board.empty_row))
                cleared += 1

        return cleared
