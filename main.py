from pathlib import Path
from datetime import datetime
import subprocess
from pynput import keyboard

## Helpers
from typing import List, Dict, Set
from collections import defaultdict

## Utilities
from mathhelper import MathHelper
from screenshothelper import select_rectangle
from ocr import OCR

## Native
from PyObjCTools import AppHelper
import Quartz
from AppKit import NSWorkspace
from Vision import VNRecognizeTextRequest

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
        self.helper = MathHelper()

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

    def get_screenshotted_programs(self) -> List[str]:
        """
        Determines which programs are included in the screenshot
        xmin, xmax, ymin, ymax: locators for selected region in screenshot
        Returns list of program name strings.
        """
        on_screen_programs = self.helper.get_visible_windows()
        return on_screen_programs

class SmartScreenshot():
    def __init__(self):
        self.ocr = OCR()
        self.hotkeys = keyboard.GlobalHotKeys({
            "<cmd>+5": self.request_screenshot,
        })
        self.hotkeys.start()

    def request_screenshot(self):
        AppHelper.callAfter(self.take_screenshot)

    def take_screenshot(self):
        rectangle = select_rectangle()
        if rectangle is None:
            return

        filename = datetime.now().strftime("Screenshot-%Y%m%d-%H%M%S.png")
        screenshot_path = output_dir / filename

        subprocess.run([
            "/usr/sbin/screencapture",
            f"-R{rectangle.x},{rectangle.y},{rectangle.width},{rectangle.height}",
            "-x",
            str(screenshot_path),
        ], 
        check=True,
        timeout=5)

        self.process_screenshot(screenshot_path)

    def process_screenshot(self, screenshot_path: Path) -> str:
        print(f"Processing screenshot: {screenshot_path}", flush=True)
        description = self.ocr.generate(screenshot_path)
        print(f"Description: {description}", flush=True)
        return description


if __name__ == "__main__":
    wh = WindowHelper()
    ss = SmartScreenshot()
    AppHelper.runEventLoop()
