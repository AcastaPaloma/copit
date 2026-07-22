
from pathlib import Path
from datetime import datetime
import subprocess
from pynput import keyboard

from typing import List, Dict, Set

## Screen Read
import Quartz
from AppKit import NSWorkspace

### CONFIGS ###
output_dir = Path.home() / "Downloads"
output_dir.mkdir(parents=True, exist_ok=True)

class MathHelper():
    def __init__(self):
        pass

    def union(self):
        """
        Calculates the union of two windows
        """

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

        self.app = NSWorkspace.sharedWorkspace().frontmostApplication()

    def get_bounds(self) -> Dict[str, List[tuple]]:
        programs = dict()

        for window in self.windows:
            if window.get(Quartz.kCGWindowLayer, 1) != 0:
                continue

            if not window.get(Quartz.kCGWindowIsOnscreen, False):
                continue

            bounds = window[Quartz.kCGWindowBounds]
            owner = window.get(Quartz.kCGWindowOwnerName)
            title = window.get(Quartz.kCGWindowName)

            x = bounds["X"]
            y = bounds["Y"]
            width = bounds["Width"]
            height = bounds["Height"]

            programs[owner] = [(x, y), (x + width, y + height)]

        return programs

    def get_top_level(self):
        program_name = self.app.localizedName()
        pid = self.app.processIdentifier()

        return(program_name, pid)

    def get_layers(self):
        for z_index, window in enumerate(self.windows):
            bundle_id = window.get(Quartz.kCGWindowOwnerName)

            if bundle_id not in ["Control Center"]:
                print({
                    "z_index": z_index,
                    "program": bundle_id,
                    "title": window.get(Quartz.kCGWindowName),
                    "layer": window.get(Quartz.kCGWindowLayer),
                    "pid": window.get(Quartz.kCGWindowOwnerPID)
                })

    def get_programs(self, xmin, xmax, ymin, ymax):
        """
        Determine which programs are included in the screenshot
        xmin, xmax, ymin, ymax: locators for selected region in screenshot
        """


class SmartScreenshot():
    def __init__(self):
        self.hotkeys = keyboard.GlobalHotKeys({
            "<caps_lock>+s": self.take_screenshot,
        })
        self.hotkeys.start()
        self.hotkeys.join()

    def find_app_name(self):
        pass

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
        pass


wh = WindowHelper()
print(wh.get_bounds())
print(wh.get_top_level())
wh.get_layers()