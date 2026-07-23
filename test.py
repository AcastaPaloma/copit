import Quartz


Rect = tuple[float, float, float, float]


def _intersection(a: Rect, b: Rect) -> Rect | None:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    return (left, top, right, bottom) if left < right and top < bottom else None


def _subtract(rect: Rect, blocker: Rect) -> list[Rect]:
    """Return the rectangular pieces of rect not covered by blocker."""
    overlap = _intersection(rect, blocker)
    if overlap is None:
        return [rect]

    left, top, right, bottom = rect
    overlap_left, overlap_top, overlap_right, overlap_bottom = overlap
    pieces = []

    if top < overlap_top:
        pieces.append((left, top, right, overlap_top))
    if overlap_bottom < bottom:
        pieces.append((left, overlap_bottom, right, bottom))
    if left < overlap_left:
        pieces.append((left, overlap_top, overlap_left, overlap_bottom))
    if overlap_right < right:
        pieces.append((overlap_right, overlap_top, right, overlap_bottom))

    return pieces


def _display_rectangles() -> list[Rect]:
    error, display_ids, _ = Quartz.CGGetActiveDisplayList(32, None, None)
    if error != Quartz.kCGErrorSuccess:
        raise RuntimeError(f"CGGetActiveDisplayList failed with error {error}")

    rectangles = []
    for display_id in display_ids:
        bounds = Quartz.CGDisplayBounds(display_id)
        rectangles.append(
            (
                float(bounds.origin.x),
                float(bounds.origin.y),
                float(bounds.origin.x + bounds.size.width),
                float(bounds.origin.y + bounds.size.height),
            )
        )
    return rectangles


def get_visible_windows(
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
    displays = _display_rectangles()

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

        window_rect = (
            float(bounds["X"]),
            float(bounds["Y"]),
            float(bounds["X"] + bounds["Width"]),
            float(bounds["Y"] + bounds["Height"]),
        )

        # Clip the window to the union of all active displays.
        visible_parts = [
            clipped
            for display in displays
            if (clipped := _intersection(window_rect, display)) is not None
        ]

        # Remove areas occupied by opaque normal windows in front.
        for blocker in opaque_windows_in_front:
            visible_parts = [
                piece
                for part in visible_parts
                for piece in _subtract(part, blocker)
            ]
            if not visible_parts:
                break

        meaningful_parts = [
            part
            for part in visible_parts
            if part[2] - part[0] >= min_visible_edge
            and part[3] - part[1] >= min_visible_edge
        ]
        visible_area = sum(
            (right - left) * (bottom - top)
            for left, top, right, bottom in meaningful_parts
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
