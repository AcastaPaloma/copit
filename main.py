from pathlib import Path
from datetime import datetime
import subprocess
from pynput import keyboard

## Helpers
from typing import List, Dict, Set
from collections import defaultdict

## Utilities
from mathhelper import MathHelper

## Screen Read
import Quartz
from AppKit import NSWorkspace

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

        self.app = NSWorkspace.sharedWorkspace().frontmostApplication()
        self.math = MathHelper()

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

    def get_layers(self) -> Dict[int, int]:
        """
        Returns the smallest (most top-level) layer of any given program.
        Returns Dict[PID, min. LAYER]
        """
        res = defaultdict()
        for z_index, window in enumerate(self.windows):
            bundle_id = window.get(Quartz.kCGWindowOwnerName)

            if bundle_id not in ["Control Center"]:
                meta = {
                    "z_index": z_index,
                    "program": bundle_id,
                    "title": window.get(Quartz.kCGWindowName),
                    "layer": window.get(Quartz.kCGWindowLayer),
                    "pid": window.get(Quartz.kCGWindowOwnerPID)
                }
                print(meta)
                curr = meta["pid"] if meta["pid"] else 1000
                res[meta["pid"]] = min(meta["layer"], curr)

        return res

    def get_foreground_programs(self):
        pass

    def get_screenshotted_programs(self, xmin, xmax, ymin, ymax) -> List[str]:
        """
        Determines which programs are included in the screenshot
        xmin, xmax, ymin, ymax: locators for selected region in screenshot
        Returns list of program name strings.
        """
        layers = self.get_layers()

        return self.math.algo()

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
print(wh.get_bounds(), end="\n")
print(dict(wh.get_layers()))