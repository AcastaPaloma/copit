from AppKit import NSWorkspace

from pathlib import Path
from datetime import datetime
import subprocess
from pynput import keyboard

## Screen Read
import Quartz

### CONFIGS ###
output_dir = Path.home() / "Downloads"
output_dir.mkdir(parents=True, exist_ok=True)



class WindowHelper():
    def __init__(self):
        self.options = (
            Quartz.kCGWindowListOptionOnScreenOnly |
            Quartz.kCGWindowListExcludeDesktopElements
        )

        self.windows = Quartz.CGWindowListCopyWindowInfo(
            self.options,
            Quartz.kCGNullWindowID
        )


class SmartScreenshot():
    def __init__(self):
        self.hotkeys = keyboard.GlobalHotKeys({
            "<caps_lock>+s": self.take_screenshot,
        })
        self.hotkeys.start()
        self.hotkeys.join()

    def find_app_name(self):


    def take_screenshot(self):
        filename = datetime.now().strftime("Screenshot-%Y%m%d-%H%M%S.png")
        output = output_dir / filename

        res = subprocess.run([
            "/usr/sbin/screencapture",
            "-i",  # click-and-drag selection
            "-x",  # suppress sound
            str(output),
        ], 
        check=True,
        timeout=5)

        self.process_screenshot()

    def process_screenshot(self):

