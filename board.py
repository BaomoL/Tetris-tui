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
        piece_colors['2'] = all_pieces
        piece_colors['3'] = all_pieces
        piece_colors['4'] = all_pieces
        piece_colors['5'] = all_pieces
        piece_colors['6'] = all_pieces
        piece_colors['7'] = all_pieces
        piece_colors['8'] = all_pieces

    return piece_colors

# function for converting time to time format

def format_time(seconds):

    minutes, seconds = divmod(int(seconds), 60)

    return f'{minutes:02d}:{seconds:02d}'

# board class represents current active board

class Board:

    piece_colors = piece_color(t, z, s, i, l, j, o, all_pieces)

    # create 22x12 board, 3s represent borders and 0s represent empty space

    def __init__(self):
        self.grid = [['100000000001'] for x in range ( 21)] + [['111111111111']]
        self.grid = [list(row[0]) for row in self.grid]
        self.placed_pieces = 0

    # render is in charge of displaying current game state; called whenever there is a change

    def render(self, piece, held_piece, upcoming, 
               combo, score, elapsed_time, place_type, 
               game_mode, lines_cleared, level, sprint, ultra):

        #create duplicate board to make changes (display the piece) to before printing

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

        while self.is_valid(piece, dy=ghost_y - piece.y + 1):
            ghost_y += 1
            
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
                new_line = ''
                for x in range(len(held_piece.shape[y])):
                    if held_piece.shape[y][x]:
                        new_line += Board.piece_colors[str(held_piece.shape[y][x])]
                    else:
                        new_line += space
                new_line += space * (5 - len(held_piece.shape[y]))
                hold_lines.append(new_line)

        upcoming_pieces = []

        # same process for upcoming pieces

        for piece in upcoming:

            upcoming_pieces.append(Piece(piece, 0, 0))

        next_lines = [space * 5] * 2

        for piece in upcoming_pieces:
            for y in range(len(piece.shape)):
                new_line = ''
                for x in range(len(piece.shape[y])):
                    if piece.shape[y][x]:
                        new_line += Board.piece_colors[str(piece.shape[y][x])]
                    else:
                        new_line += space
                next_lines.append(new_line)
            next_lines.append('')

        # turns current piece and ghost piece (as determined from earlier) into characters (along with everything else)
        
        for y in bored:
            row = ''
            for x in y:
                if x in Board.piece_colors:
                    row += Board.piece_colors[x]
                elif x == '9':
                    row += ghost_piece 
                elif x == '1':
                    row += border
                else:
                    row += space
            board_lines.append(row)

        # appends both held piece and queued pieces to left and right by appending each row's list at a time

        for i in range(len(board_lines)):

            left = hold_lines[i] if i < len(hold_lines) else space * 5
            right = next_lines[i] if i < len(next_lines) else ''
            board_lines[i] = left + board_lines[i] + space * 2 + right

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
            '\n'.join('\033[2K' + row for row in board_lines))        
        sys.stdout.flush()

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
                self.grid.insert(0, list('100000000001'))
                cleared += 1

        return cleared
