import sys, os
from contextlib import contextmanager

if sys.platform == 'win32':
    import msvcrt

    # makes ansi colors and cursor codes work in the older windows console
    os.system('')

    # throw away keypresses that piled up while nothing was reading input
    def flush_input():
        while msvcrt.kbhit():
            msvcrt.getch()

    @contextmanager
    def raw_mode():
        try:
            yield
        finally:
            flush_input()

else:
    import termios, tty

    @contextmanager
    def raw_mode():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            yield
        finally:
            termios.tcflush(fd, termios.TCIFLUSH)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)