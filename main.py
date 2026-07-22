from pathlib import Path
from datetime import datetime
import subprocess
from pynput import keyboard

output_dir = Path.home() / "Pictures" / "Screenshots"
output_dir.mkdir(parents=True, exist_ok=True)

def take_screenshot():
    filename = datetime.now().strftime("Screenshot-%Y%m%d-%H%M%S.png")
    output = output_dir / filename

    subprocess.run([
        "/usr/sbin/screencapture",
        "-i",  # click-and-drag selection
        "-x",  # suppress sound
        str(output),
    ], check=True)

    print(f"Saved: {output}")

hotkeys = keyboard.GlobalHotKeys({
    "<caps_lock>+s": take_screenshot,
})

print("Press Ctrl+Option+S to select a screenshoSt. Ctrl+C to quit.")
hotkeys.start()
hotkeys.join()