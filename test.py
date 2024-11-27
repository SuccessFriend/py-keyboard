import sys
import time
from threading import Thread
from pynput import keyboard

# Platform-specific imports
if sys.platform == "win32":
    import win32gui
    import win32process
elif sys.platform == "darwin":
    from AppKit import NSWorkspace
elif sys.platform.startswith("linux"):
    from Xlib import display

# Set to store pressed keys
pressed_keys = set()

# Function to get foreground window details
def get_foreground_window():
    if sys.platform == "win32":
        hwnd = win32gui.GetForegroundWindow()
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        title = win32gui.GetWindowText(hwnd)
        return {"pid": pid, "title": title}
    elif sys.platform == "darwin":
        info = NSWorkspace.sharedWorkspace().activeApplication()
        return {"pid": info["NSApplicationProcessIdentifier"], "title": info["NSApplicationName"]}
    elif sys.platform.startswith("linux"):
        try:
            d = display.Display()
            window = d.get_input_focus().focus
            while window:
                wm_name = window.get_wm_name()
                if wm_name:
                    pid = window.id
                    return {"pid": pid, "title": wm_name}
                window = window.query_tree().parent
        except Exception:
            pass
    return {"pid": None, "title": None}

# Function to format pressed keys
def format_keys(key, pressed=True):
    global pressed_keys
    try:
        if pressed:
            # Add key to pressed set
            pressed_keys.add(key.char if hasattr(key, 'char') and key.char else f"<{key.name}>")
        else:
            # Remove key from pressed set
            pressed_keys.discard(key.char if hasattr(key, 'char') and key.char else f"<{key.name}>")
    except AttributeError:
        if pressed:
            pressed_keys.add(f"<{key.name}>")
        else:
            pressed_keys.discard(f"<{key.name}>")
    return "".join(sorted(pressed_keys))

# Key press event
def on_press(key):
    formatted_keys = format_keys(key, pressed=True)
    print(f"Keys pressed: {formatted_keys}")

# Key release event
def on_release(key):
    formatted_keys = format_keys(key, pressed=False)
    print(f"Keys released: {formatted_keys}")
    if key == keyboard.Key.esc:
        # Stop listener on ESC
        return False

# Function to track foreground window in real-time
def foreground_window_tracker():
    current_window = None
    while True:
        details = get_foreground_window()
        if details and details != current_window:
            current_window = details
            print(f"Foreground Window - PID: {details['pid']}, Title: {details['title']}")
        time.sleep(1)

# Main function
def main():
    # Start foreground window tracker in a separate thread
    Thread(target=foreground_window_tracker, daemon=True).start()

    # Start listening for key events
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Listening for key events... (Press ESC to quit)")
        listener.join()

if __name__ == "__main__":
    main()
