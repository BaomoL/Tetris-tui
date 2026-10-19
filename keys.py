from pynput.keyboard import Key, Listener

# add/remove pressed key from a set

pressed = set()

def on_press(key):
    if hasattr(key, 'char') and key.char:
        pressed.add(key.char.lower())
    else:
        pressed.add(key)

def on_release(key):
    if hasattr(key, 'char') and key.char:
        pressed.discard(key.char.lower())
    else:
        pressed.discard(key)

# detect key presses and releases

listener = Listener(on_press=on_press, on_release=on_release)