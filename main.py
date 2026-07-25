# Standard library
import argparse
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List

# Third-party packages
from pynput import keyboard

# macOS frameworks
import Quartz
from AppKit import NSWorkspace
from PyObjCTools import AppHelper

# Local modules
from mathhelper import MathHelper, Rect
from screenshothelper import RectangleSelector

### CONFIGS ###
output_dir = Path.home() / "Downloads"
output_dir.mkdir(parents=True, exist_ok=True)
VERSION = "0.1.1"


def _filename_part(value: str) -> str:
    """Convert arbitrary model or application text into a safe filename part."""
    normalized = "".join(char if char.isalnum() else " " for char in value)
    return "_".join(normalized.split())


class WindowHelper:
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

    def get_screenshotted_programs(self, rect: Rect) -> List[str]:
        """
        Determines which programs are included in the screenshot
        xmin, xmax, ymin, ymax: locators for selected region in screenshot
        Returns list of program name strings.
        """
        on_screen_programs = self.helper.get_visible_windows()
        seen: set[str] = set()
        programs_to_include = []

        for program in on_screen_programs:
            program_name = program.get("program")
            if not program_name or program_name in seen:
                continue

            visible_rectangles = program.get("visible_rectangles", [])
            if any(
                MathHelper._intersection(visible_rect, rect) is not None
                for visible_rect in visible_rectangles
            ):
                seen.add(program_name)
                programs_to_include.append(program_name)

        return programs_to_include

class SmartScreenshot:
    def __init__(self):
        self._request_permissions()
        self._state_lock = Lock()
        self._state = "idle"
        self._selector = None
        self._cancel_requested = False
        self.ocr = None
        self.helper = WindowHelper()
        self.hotkeys = keyboard.GlobalHotKeys({
            "<cmd>+`": self.request_screenshot,
            "<esc>": self.request_cancel,
        })
        self.hotkeys.start()
        print("Copit is running. Press Command+` to take a screenshot.", flush=True)

    @staticmethod
    def _request_permissions():
        if not Quartz.CGPreflightListenEventAccess():
            print(
                "Copit needs Input Monitoring permission for its global hotkey.",
                flush=True,
            )
            Quartz.CGRequestListenEventAccess()

        if not Quartz.CGPreflightScreenCaptureAccess():
            print(
                "Copit needs Screen Recording permission to capture screenshots.",
                flush=True,
            )
            Quartz.CGRequestScreenCaptureAccess()

    def _get_ocr(self):
        if self.ocr is None:
            from ocr import OCR

            self.ocr = OCR()
        return self.ocr

    def request_screenshot(self):
        with self._state_lock:
            if self._state != "idle":
                return
            self._state = "selecting"
            self._cancel_requested = False

        try:
            AppHelper.callAfter(self.take_screenshot)
        except Exception:
            with self._state_lock:
                self._state = "idle"
            raise

    def request_cancel(self):
        with self._state_lock:
            if self._state != "selecting" or self._cancel_requested:
                return
            self._cancel_requested = True

        AppHelper.callAfter(self.cancel_selection)

    def cancel_selection(self):
        with self._state_lock:
            if self._state != "selecting":
                return
            selector = self._selector

        if selector is not None:
            selector.cancel()

    def take_screenshot(self):
        try:
            selector = RectangleSelector.alloc().init()
            with self._state_lock:
                if self._state != "selecting":
                    return
                self._selector = selector
                cancel_requested = self._cancel_requested

            if cancel_requested:
                return

            rectangle = selector.select()
            if rectangle is None:
                return

            with self._state_lock:
                self._selector = None
                self._state = "processing"

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

            self.process_screenshot(screenshot_path, rectangle)
        finally:
            with self._state_lock:
                self._selector = None
                self._cancel_requested = False
                self._state = "idle"

    def process_screenshot(self, screenshot_path: Path, rect: Rect) -> str:
        programs = self.helper.get_screenshotted_programs(rect=rect)
        generated_description = self._get_ocr().generate(screenshot_path)
        filename_parts = []
        for part in [*programs, generated_description]:
            if cleaned_part := _filename_part(part):
                filename_parts.append(cleaned_part)

        stem = "_".join(filename_parts) or "Screenshot"
        destination = screenshot_path.with_name(f"{stem}.png")

        suffix = 2
        while destination.exists():
            destination = screenshot_path.with_name(f"{stem}_{suffix}.png")
            suffix += 1

        screenshot_path.rename(destination)
        print(f"Saved screenshot: {destination}", flush=True)
        return destination.name


def run() -> None:
    parser = argparse.ArgumentParser(
        prog="copit",
        description="Capture and automatically name macOS screenshots.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.parse_args()

    SmartScreenshot()
    AppHelper.runEventLoop()


if __name__ == "__main__":
    run()
