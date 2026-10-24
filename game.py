import time, sys, random
from terminal import raw_mode
from pynput.keyboard import Key

from config import (das, arr, soft_drop_multiplier, stationary_touch_time,
                    horizontal_touch_time, absolute_touch_time,
                    rotate_clockwise, rotate_counter_clockwise, rotate_one_eighty,
                    move_left, move_right, soft_drop, hard_drop, hold)

from keys import pressed
from board import Board, format_time
from pieces import Piece

# game class contains all ongoing game states

class Game:

    # bag is a system where the game randomizes 7 pieces at a time and adds it to a queue; 
    # this implies the same piece cannot show up 3 times in a row

    bag = ['t', 'i', 'o', 'l', 'j', 's', 'z']

    # score tables taken from tetris wiki

    score = {
    0: 0,
    1: 100,
    2: 300,
    3: 500,
    4: 800}

    t_spin_score = {
    0: 0,
    1: 800,
    2: 1200,
    3: 1600}

    perfect_clear_score = {
    1: 800,
    2: 1200,
    3: 1800,
    4: 2000}

    modes = {
    '1': {
        'game_mode': 'Marathon',
        'line_limit': None,
        'time_limit': None,
        'gravity': True
    },
    '2': {
        'game_mode': 'Sprint',
        'line_limit': 40,
        'time_limit': None,
        'gravity': True
    },
    '3': {
        'game_mode': 'Ultra',
        'line_limit': None,
        'time_limit': 120,
        'gravity': True
    },
    '4': {
        'game_mode': 'Hardcore',
        'line_limit': None,
        'time_limit': None,
        'gravity': True
    } }


    def __init__(self, game_mode, sprint=None, ultra=None):

        # game states involve tracking the multipliers, ongoing combos, whether or not the game is running, whether or not a piece is held, and more

        self.board = Board()
        self.running = False
        self.time = None
        self.pieces = random.sample(Game.bag, len(Game.bag))
        self.active_piece = self.new_piece()
        self.held_piece = None
        self.can_hold = True
        self.combo = 0
        self.score = 0
        self.b2b = False
        self.b2b_mul = 1
        self.game_over = False
        self.elapsed_time = 0
        self.last_clear_type = ''
        self.b2b_counter = 0

        # menu decides whether or not the menu should be showing

        self.menu = False

        # game mode tracks the type of game created:

        self.mode = Game.modes[game_mode]['game_mode']
        self.line_limit = Game.modes[game_mode]['line_limit']
        self.time_limit = Game.modes[game_mode]['time_limit']
        self.gravity = Game.modes[game_mode]['gravity']

        # set options from menu
        
        if self.mode == 'Sprint' and sprint is not None:
            self.line_limit = sprint

        if self.mode == 'Ultra' and ultra is not None:
            self.time_limit = ultra

        self.final_results = ''

        self.sprint = self.line_limit or 0
        self.ultra = self.time_limit or 0

        # default settings/stats

        self.total_lines = 0
        self.level = 1

        if self.gravity:
            self.gravity_speed = 1

    def update_mode(self):

        # each update changes final result and tracks current game state <- final results tracked incase player chooses to end game early

        if self.mode in ('Marathon', 'Hardcore'):

            # standard tetris gravity formula

            self.level = min(15, self.total_lines // 10 + 1)

            self.gravity_speed = (0.8 - (self.level - 1) * 0.007) ** (self.level - 1)


            self.final_results = f'{self.mode} \n\nFinal Level: {self.level} \nScore: {int(self.score)}\nTotal Lines Cleared: {self.total_lines} \nTotal Elapsed Time: {format_time(self.elapsed_time)}'

        elif self.mode == 'Sprint':
            if self.total_lines >= self.sprint:
                self.running = False
                self.game_over = True

            self.final_results = f'{self.mode} \n\nTotal Lines Cleared: {self.total_lines}/{self.sprint}\nScore: {int(self.score)} \nTotal Elapsed Time: {format_time(self.elapsed_time)}'

        elif self.mode == 'Ultra':
            if self.elapsed_time >= self.ultra:
                self.running = False
                self.game_over = True

            self.final_results = f'{self.mode} \n\nScore: {int(self.score)}\nTotal Lines Cleared: {self.total_lines} \nTotal Elapsed Time: {format_time(self.elapsed_time)}/{format_time(self.ultra)}'



    def new_piece(self):

        # function that keeps a list of the queue and randomizes more when below 7 (bag system) <- returns the next piece in the queue when called

        if len(self.pieces) < 7:

            self.pieces = random.sample(Game.bag, len(Game.bag)) + self.pieces

        #   specifically the o piece spawns in the middle by default

        if self.pieces[-1] == 'o':
            return Piece(self.pieces.pop(), 5, 0)

        return Piece(self.pieces.pop(), 4, 0)

    def hold_piece(self):

        # allows holding a piece

        if self.can_hold:
            self.gravity_timer = time.perf_counter()
            self.can_hold = False

            # store pieces by default spawn positions so when called they spawn there

            if self.held_piece is None:
                self.active_piece, self.held_piece = (
                    self.new_piece(),
                    Piece(self.active_piece.type, 4, 0)
                )    
            else:
                new_type = self.held_piece.type
                self.held_piece = Piece(self.active_piece.type, 4, 0)

                # makes sure o stays in the middle when stored

                self.active_piece = Piece(new_type, 5 if new_type == 'o' else 4, 0)

            # if trying to spawn a held piece is impossible then the game ends (an edge case)

            if not self.board.is_valid(self.active_piece):
                self.game_over = True
                self.running = False

    def show_game_over(self):

        # for when game ends

        sys.stdout.write('\033[3J\033[2J\033[H')        
        print('\n' * 5)

        print(self.final_results)

        sys.stdout.flush()

    # scoring is calculated using standard tetris system which includes:
    # back to back multiplier (1.5x)
    # combo bonus
    # perfect clear bonus
    # all tracked using states defined into the game instance upon game creation

    def calculate_score(self, lines_clear, combo, t_spin, pc):

        base_score = 0

        if pc:
            base_score = Game.perfect_clear_score[lines_clear]
        if t_spin:
            base_score = base_score + Game.t_spin_score[lines_clear]
        else:
            base_score = base_score + Game.score[lines_clear]

        if lines_clear > 0 and (lines_clear == 4 or t_spin):
            if self.b2b:
                self.b2b_mul = 1.5
            else:
                self.b2b_mul = 1
            self.b2b = True
        else:
            self.b2b_mul = 1
            if lines_clear > 0:
                self.b2b = False

        return (base_score * self.b2b_mul + 50 * max(combo - 1, 0)) * self.level

    # returns a string to be printed by render()

    def clear_type(self, lines, t_spin, pc):
        if t_spin:
            if lines == 1:
                result = 'T-Spin Single'
            elif lines == 2:
                result = 'T-Spin Double'
            elif lines == 3:
                result = 'T-Spin Triple'
            else:
                return None
            
        elif lines == 1:
            result = 'Single'
        elif lines == 2:
            result = 'Double'
        elif lines == 3:
            result = 'Triple'
        elif lines == 4:
            result = 'Tetris'
        else:
            return None

        if t_spin or lines == 4:
            if self.b2b:
                self.b2b_counter += 1
                if self.b2b_counter > 1:
                    result = str(self.b2b_counter) + 'x B2B ' + result
                else:
                    result = 'B2B ' + result
        else:
            self.b2b_counter = 0

        if pc:
            result = result + ' Perfect Clear!'

        return result

    def clear(self):

        # determine if it's a t-spin or a perfect clear, then lock piece and update score

        t_spin = self.board.detect_t_spin(self.active_piece)
        self.board.lock_piece(self.active_piece)

        # check amount of lines were cleared

        lines = self.board.clear_rows()

        self.total_lines += lines

        perfect = self.board.perfect_clear()

        # only update score/combo if lines were cleared

        if lines > 0:
            self.combo += 1
            self.last_clear_type = self.clear_type(lines, t_spin, perfect)

        else:
            self.combo = 0

        self.score += self.calculate_score(lines, self.combo, t_spin, perfect)
        perfect = False
        self.active_piece = self.new_piece()
        self.can_hold = True

        # if a new piece can't exist = end game

        if not self.board.is_valid(self.active_piece):
            self.running = False
            self.game_over = True

        # reset for new piece

        self.stationary_touching_timer = time.perf_counter()
        self.horizontal_touching_timer = time.perf_counter()
        self.absolute_touching_timer = time.perf_counter()
        self.gravity_timer = time.perf_counter()

    # starts and tracks the current game

    def render_board(self):
        self.board.render(self.active_piece, 
            self.held_piece,
            self.pieces[-5:][::-1],
            self.combo,
            self.score,
            self.elapsed_time,
            self.last_clear_type,
            self.mode,
            self.total_lines,
            self.level,
            self.sprint,
            self.ultra)
    
    def start(self):

        self.update_mode()

        self.running = True

        with raw_mode():

            self.time = time.perf_counter()
            sys.stdout.write('\033[2J\033[H')

            self.render_board()

            # because key presses are detected using an "in" statement and the set list, whether or not they are pressed or held
            # must be tracked to ensure something like a piece spinning forever doesn't happen
            # wait for release can't be used because it blocks rest of game loop

            # monotonic timers are used to track time passed

            # changed affects game updates/renders

            changed = True

            left_held = False
            left_start_hold = time.perf_counter()
            left_held_time = time.perf_counter()

            right_held = False
            right_start_hold = time.perf_counter()
            right_held_time = time.perf_counter()

            c_first_time = True
            cc_first_time = True
            mirror_first_time = True
            up_first_time = True
            hold_first_time = True

            space_held = False
            down_held = False

            # whether or not a piece is in contention for being locked

            touching = False

            self.absolute_touching_timer = time.perf_counter()

            self.gravity_timer = time.perf_counter()

            last_render = time.perf_counter()

            start_time = time.perf_counter()

            while self.running:

                # allow game to be reset/quit

                if Key.esc in pressed:
                    self.running = False
                if Key.tab in pressed:
                    self.menu = True
                    self.running = False

                self.elapsed_time = time.perf_counter() - start_time

                # three separate timers determine when a piece must be set in stone; timers start when a piece can no longer move down

                if self.mode != 'Hardcore':

                    if not self.board.is_valid(self.active_piece, dy=1):
                        if not touching:
                            self.stationary_touching_timer = time.perf_counter()
                            self.horizontal_touching_timer = time.perf_counter()
                            self.absolute_touching_timer = time.perf_counter()  
                        touching = True
                    else:
                        touching = False

                # Hardcore immediately solidifies piees when a piece cannot move down

                elif not self.board.is_valid(self.active_piece, dy=1):
                    self.clear()
                    changed = True

                # if a piece has been unable to move down for longer than the time granted by its respective timer

                if touching:

                    if (time.perf_counter() - self.stationary_touching_timer >= stationary_touch_time 
                        or time.perf_counter() - self.absolute_touching_timer >= absolute_touch_time 
                        or time.perf_counter() - self.horizontal_touching_timer >= horizontal_touch_time):

                        self.clear()
                        changed = True
                        touching = False

                # soft drop multiplies the speed of falling independent of game's 1000 hertz refresh rate

                if (soft_drop in pressed) != down_held:
                    self.gravity_timer = time.perf_counter()

                down_held = soft_drop in pressed

                interval = self.gravity_speed

                if soft_drop in pressed:
                    interval = self.gravity_speed / soft_drop_multiplier

                # soft drop makes gravity interval shorter by a multiplier

                now = time.perf_counter()
                elapsed = now - self.gravity_timer

                if elapsed >= interval:
                    steps = int(elapsed / interval)

                    for _ in range(steps):
                        if not self.active_piece.move(self.board, 'down'):
                            break

                    self.gravity_timer += steps * interval
                    changed = True

                # hard drop bypasses all timers and immediately locks the piece; same code as touching

                if hard_drop in pressed:

                    if not space_held:
                        while self.board.is_valid(self.active_piece, dy =1):
                            self.active_piece.move(self.board, 'down')

                        self.clear()
                        changed = True
                        touching = False
                        space_held = True

                # DAS and ARR implemented with monotonic timers; a key held down for DAS amount of seconds will start repeating at a rate of ARR

                if move_left in pressed and not right_held:

                    if not left_held:

                        if self.active_piece.move(self.board, 'left'):
                            self.stationary_touching_timer = time.perf_counter()

                        changed = True
                        left_start_hold = time.perf_counter()
                        left_held_time = time.perf_counter()
                        left_held = True

                    elif time.perf_counter() - left_start_hold >= das:

                        if time.perf_counter() - left_held_time >= arr:

                            if self.active_piece.move(self.board, 'left'):
                                self.stationary_touching_timer = time.perf_counter()

                            left_held_time = time.perf_counter()
                            changed = True

                if move_right in pressed and not left_held:

                    if not right_held:

                        if self.active_piece.move(self.board, 'right'):
                            self.stationary_touching_timer = time.perf_counter()

                        changed = True
                        right_start_hold = time.perf_counter()
                        right_held_time = time.perf_counter()
                        right_held = True

                    elif time.perf_counter() - right_start_hold >= das:

                        if time.perf_counter() - right_held_time >= arr:

                            if self.active_piece.move(self.board, 'right'):
                                self.stationary_touching_timer = time.perf_counter()
                    
                            right_held_time = time.perf_counter()
                            changed = True

                # ensure that only a new press rotates pieces by recording its current state 

                if rotate_clockwise in pressed:
                    if c_first_time:
                        if self.active_piece.rotate(self.board, 'c'):
                            self.stationary_touching_timer = time.perf_counter()
                            self.horizontal_touching_timer = time.perf_counter()
                        c_first_time = False
                        changed = True

                if rotate_counter_clockwise in pressed:
                    if cc_first_time:
                        if self.active_piece.rotate(self.board, 'cc'):
                            self.stationary_touching_timer = time.perf_counter()
                            self.horizontal_touching_timer = time.perf_counter()
                        cc_first_time = False
                        changed = True

                if rotate_one_eighty in pressed:
                    if mirror_first_time:
                        if self.active_piece.rotate(self.board, '180'):
                            self.stationary_touching_timer = time.perf_counter()
                            self.horizontal_touching_timer = time.perf_counter()
                        mirror_first_time = False
                        changed = True

                if hold in pressed:
                    if hold_first_time:
                        if self.can_hold:
                            self.hold_piece()

                            if not self.running:
                                break

                            touching = False
                            self.stationary_touching_timer = time.perf_counter()
                            self.horizontal_touching_timer = time.perf_counter()
                            self.absolute_touching_timer = time.perf_counter()
                            self.gravity_timer= time.perf_counter()

                            changed = True

                        hold_first_time = False

                if Key.up in pressed:
                    if up_first_time:
                        if self.active_piece.rotate(self.board, 'c'):
                            self.stationary_touching_timer = time.perf_counter()
                            self.horizontal_touching_timer = time.perf_counter()
                        up_first_time = False
                        changed = True

                # reset key states when released
                
                if move_left not in pressed:
                    left_held = False
                    
                if move_right not in pressed:
                    right_held = False

                if hard_drop not in pressed:
                    space_held = False

                if rotate_clockwise not in pressed:
                    c_first_time = True

                if rotate_counter_clockwise not in pressed:
                    cc_first_time = True

                if hold not in pressed:
                    hold_first_time = True

                if rotate_one_eighty not in pressed:
                    mirror_first_time = True

                if Key.up not in pressed:
                    up_first_time = True

                # refresh only at 60 fps to avoid stuttering and cpu overload

                if (changed and now - last_render >= 1/60) or now - last_render >= 1:

                    # update specific mode stats before render
                                        
                    self.update_mode()
                    self.render_board()
                    # track last frame
                    
                    last_render = time.perf_counter()
                    changed = False

                # 200 hertz polling rate

                time.sleep(0.005)



            if self.game_over:
                self.update_mode()
                self.show_game_over()

