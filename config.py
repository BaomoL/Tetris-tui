# customize your game!

from pynput.keyboard import Key

t, z, s, i ,l, j, o = None, None, None, None, None, None, None


"""Game Settings"""
das = 0.1
arr = 0.01
soft_drop_multiplier = 100
stationary_touch_time = 0.5
horizontal_touch_time = 5
absolute_touch_time =  20

"""Rotations"""
rotate_clockwise =          's'
rotate_counter_clockwise =  'a'
rotate_one_eighty =         'w'

"""Movement"""
move_left =     Key.left
move_right =    Key.right
soft_drop =     Key.down
hard_drop =     Key.space
hold =          Key.shift 
  
"""Graphics"""
padding = 0


# commented out sections are options; only one can be uncommented at a time (Ansi is default)
# customizable however unicode characters and emojis are 2x1 to make a square thus space must be doubled to accommodate!

"""Default"""
# space =         '  '
# height =          2
# border =        '@@'
# ghost_piece =   '..'
# all_pieces =    '##'

"""Emojis"""

# all_pieces = None

# space = '  '
# height = 1

# all_pieces = None

# border = '⬛'
# ghost_piece =   '▒▒'

# t = '🟪'
# z = '🟥'
# s = '🟩'
# i = '⬜'
# l = '🟧'
# j = '🟦'
# o = '🟨'

"""Ansi"""
space = '  '
height = 1

all_pieces = None

border =        '\033[38;2;90;100;115m██\033[0m'
ghost_piece =   '▒▒'

t = '\033[38;2;175;65;230m██\033[0m'   #Purple
z = '\033[38;2;235;55;55m██\033[0m'    #Red
s = '\033[38;2;65;205;75m██\033[0m'    #Green
i = '\033[38;2;0;220;240m██\033[0m'    #Cyan
l = '\033[38;2;255;155;25m██\033[0m'   #Orange
j = '\033[38;2;45;90;235m██\033[0m'    #Blue
o = '\033[38;2;250;215;35m██\033[0m'   #Yellow