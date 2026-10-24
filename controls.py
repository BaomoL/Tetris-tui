from config import (rotate_clockwise, rotate_counter_clockwise, rotate_one_eighty, rotate_clockwise_backup,
                    move_left, move_right, soft_drop, hard_drop, hold)

from enum import Enum, auto
from keys import pressed

class Action(Enum):
    ROTATE_CW = auto()
    ROTATE_CCW = auto()
    ROTATE_180 = auto()
    LEFT = auto()
    RIGHT = auto()
    SOFT_DROP = auto()
    HARD_DROP = auto()
    HOLD = auto()


keybinds = {rotate_clockwise: Action.ROTATE_CW,
            rotate_counter_clockwise: Action.ROTATE_CCW, 
            rotate_one_eighty: Action.ROTATE_180, 
            rotate_clockwise_backup: Action.ROTATE_CW,
            move_left: Action.LEFT, 
            move_right: Action.RIGHT, 
            soft_drop: Action.SOFT_DROP, 
            hard_drop: Action.HARD_DROP, 
            hold: Action.HOLD
            }

class Controls:

    def __init__(self):
        self.last_held = set()

    def read(self):

        keys_pressed = set(pressed)

        held_actions = set()

        for key in keys_pressed:
            action = keybinds.get(key)
            if action is not None:
                held_actions.add(action)

        new_actions = held_actions - self.last_held

        self.last_held = held_actions


        return new_actions, held_actions

        
    


    
    





    
