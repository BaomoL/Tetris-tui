import sys, time
from terminal import raw_mode
from pynput.keyboard import Key
from game import Game
from keys import pressed, listener

# main menu items

mode_menu = ['Marathon', 'Sprint', 'Ultra', 'Hardcore']

# second menu for modes with an option

options = {
    '2': ('Sprint: how many lines?', [('20 lines', 20), ('40 lines', 40), ('100 lines', 100)]),
    '3': ('Ultra: how long?', [('1 minute', 60), ('2 minutes', 120), ('5 minutes', 300)])
}

# stop at current key until it's released so the input isn't transferred to the next screen

def wait_for_release(key):
    while key in pressed:
        time.sleep(0.01)

# show a numbered menu; return the pressed number as a string

def select_menu(title, labels, footer):

    keys = [str(n + 1) for n in range(len(labels))]

    with raw_mode():

        sys.stdout.write('\033[2J\033[H')
        print('\n' + title)
        for key, label in zip(keys, labels):
            print(f'{key}. {label}')
        print('\n' + footer)

        while True:

            if Key.esc in pressed:
                wait_for_release(Key.esc)
                return None

            for key in keys:
                if key in pressed:
                    wait_for_release(key)
                    return key

            time.sleep(0.01)


def main():

    listener.start()

    try:
        # each return statement cancels the loop before the next one is reached
        while True:
            mode = select_menu('Choose mode:', mode_menu, 'ESC to quit')
            if mode is None:
                return
            # sprint and ultra get a second menu; esc there goes back to the first
            
            sprint = None
            ultra = None

            if mode in options:
                title, choices = options[mode]
                pick = select_menu(title, [label for label, _ in choices], 'ESC to go back')
                if pick is None:
                    continue

                value = choices[int(pick) - 1][1]

                if mode == '2':
                    sprint = value
                else:
                    ultra = value

            game = Game(mode, sprint, ultra)

            while True:
                game.start()

                # tab during play goes back to the menu

                if game.menu:
                    wait_for_release(Key.tab)
                    break

                # esc during play quits (game never ended)

                if not game.game_over:
                    return

                print("\nPress ENTER to restart, TAB to select mode, ESC to quit")

                while (Key.enter not in pressed
                       and Key.tab not in pressed
                       and Key.esc not in pressed):
                    time.sleep(0.01)

                # esc skips the restart

                if Key.esc in pressed:
                    return

                if Key.tab in pressed:
                    wait_for_release(Key.tab)
                    break

                # enter restarts with the same mode and option

                wait_for_release(Key.enter)
                
                game = Game(mode, sprint, ultra)

    finally:
        listener.stop()


if __name__ == '__main__':
    main()