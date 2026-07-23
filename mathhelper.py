# Standard library
from dataclasses import dataclass

# macOS frameworks
import Quartz


@dataclass(frozen=True)
class Rect:
    """A rectangle represented by its top-left origin and dimensions."""

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

class MathHelper():
    def __init__(self):
        pass

    @classmethod
    def _intersection(cls, a: Rect, b: Rect) -> Rect | None:
        left = max(a.x, b.x)
        top = max(a.y, b.y)
        right = min(a.right, b.right)
        bottom = min(a.bottom, b.bottom)
        return Rect(left, top, right - left, bottom - top) if left < right and top < bottom else None

    @classmethod
    def _subtract(cls, rect: Rect, blocker: Rect) -> list[Rect]:
        """Return the rectangular pieces of rect not covered by blocker."""
        overlap = cls._intersection(rect, blocker)
        if overlap is None:
            return [rect]

        pieces = []

        if rect.y < overlap.y:
            pieces.append(Rect(rect.x, rect.y, rect.width, overlap.y - rect.y))
        if overlap.bottom < rect.bottom:
            pieces.append(Rect(rect.x, overlap.bottom, rect.width, rect.bottom - overlap.bottom))
        if rect.x < overlap.x:
            pieces.append(Rect(rect.x, overlap.y, overlap.x - rect.x, overlap.height))
        if overlap.right < rect.right:
            pieces.append(Rect(overlap.right, overlap.y, rect.right - overlap.right, overlap.height))

        return pieces

    @classmethod
    def _display_rectangles(cls) -> list[Rect]:
        error, display_ids, _ = Quartz.CGGetActiveDisplayList(32, None, None)
        if error != Quartz.kCGErrorSuccess:
            raise RuntimeError(f"CGGetActiveDisplayList failed with error {error}")

        rectangles = []
        for display_id in display_ids:
            bounds = Quartz.CGDisplayBounds(display_id)
            rectangles.append(Rect(
                float(bounds.origin.x),
                float(bounds.origin.y),
                float(bounds.size.width),
                float(bounds.size.height),
            ))
        return rectangles

    def get_visible_windows(
        self,
        *,
        min_visible_fraction: float = 0.01,
        min_visible_edge: float = 8.0,
    ) -> list[dict]:
        """Return normal app windows with a meaningful unobscured screen region.

        Core Graphics reports windows front-to-back. For each normal, opaque app
        window, this subtracts the rectangles of normal windows in front of it.
        The small default thresholds discard exposed borders/shadows such as the
        7-point strip reported for a window behind a macOS split-screen window.
        """
        options = (
            Quartz.kCGWindowListOptionOnScreenOnly
            | Quartz.kCGWindowListExcludeDesktopElements
        )
        windows = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        displays = MathHelper._display_rectangles()

        result = []
        opaque_windows_in_front: list[Rect] = []

        for z_index, window in enumerate(windows):
            if window.get(Quartz.kCGWindowLayer) != 0:
                continue
            if not window.get(Quartz.kCGWindowIsOnscreen, False):
                continue

            bounds = window.get(Quartz.kCGWindowBounds)
            if not bounds or bounds["Width"] <= 0 or bounds["Height"] <= 0:
                continue

            window_rect = Rect(
                float(bounds["X"]),
                float(bounds["Y"]),
                float(bounds["Width"]),
                float(bounds["Height"]),
            )

            # Clip the window to the union of all active displays.
            visible_parts = [
                clipped
                for display in displays
                if (clipped := MathHelper._intersection(window_rect, display)) is not None
            ]

            # Remove areas occupied by opaque normal windows in front.
            for blocker in opaque_windows_in_front:
                visible_parts = [
                    piece
                    for part in visible_parts
                    for piece in MathHelper._subtract(part, blocker)
                ]
                if not visible_parts:
                    break

            meaningful_parts = [
                part
                for part in visible_parts
                if part.width >= min_visible_edge
                and part.height >= min_visible_edge
            ]
            visible_area = sum(
                part.width * part.height
                for part in meaningful_parts
            )
            window_area = float(bounds["Width"] * bounds["Height"])

            if visible_area > 0 and visible_area / window_area >= min_visible_fraction:
                result.append(
                    {
                        "z_index": z_index,
                        "program": window.get(Quartz.kCGWindowOwnerName),
                        "title": window.get(Quartz.kCGWindowName),
                        "pid": window.get(Quartz.kCGWindowOwnerPID),
                        "window_id": window.get(Quartz.kCGWindowNumber),
                        "bounds": dict(bounds),
                        "visible_rectangles": meaningful_parts,
                        "visible_fraction": visible_area / window_area,
                    }
                )

            # Global window alpha is the only public opacity signal available here.
            if window.get(Quartz.kCGWindowAlpha, 1.0) >= 0.99:
                opaque_windows_in_front.append(window_rect)

        return result

    if __name__ == "__main__":
        for visible_window in get_visible_windows():
            print(
                visible_window["program"],
                repr(visible_window["title"]),
                f'{visible_window["visible_fraction"]:.1%} visible',
            )
