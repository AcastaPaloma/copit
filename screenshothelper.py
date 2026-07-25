# Future imports
from __future__ import annotations

# Third-party packages
import objc

# macOS frameworks
from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSApplicationActivationPolicyProhibited,
    NSBackingStoreBuffered,
    NSBezierPath,
    NSColor,
    NSEvent,
    NSEventMaskKeyDown,
    NSFloatingWindowLevel,
    NSMakeRect,
    NSRectFill,
    NSScreen,
    NSView,
    NSWindow,
    NSWindowStyleMaskBorderless,
)
from Foundation import NSObject, NSThread

# Local modules
from mathhelper import Rect


class SelectionView(NSView):
    start_point = objc.ivar()
    current_point = objc.ivar()
    selection_callback = objc.ivar()

    def initWithFrame_callback_(self, frame, callback):
        self = objc.super(SelectionView, self).initWithFrame_(frame)
        if self is None:
            return None

        self.start_point = None
        self.current_point = None
        self.selection_callback = callback
        return self

    def acceptsFirstResponder(self):
        return True

    def mouseDown_(self, event):
        point = self.convertPoint_fromView_(event.locationInWindow(), None)
        self.start_point = point
        self.current_point = point
        self.setNeedsDisplay_(True)

    def mouseDragged_(self, event):
        self.current_point = self.convertPoint_fromView_(
            event.locationInWindow(),
            None,
        )
        self.setNeedsDisplay_(True)

    def mouseUp_(self, event):
        self.current_point = self.convertPoint_fromView_(
            event.locationInWindow(),
            None,
        )

        rect = self.selection_rect()

        if rect.size.width > 1 and rect.size.height > 1:
            self.selection_callback(rect)
        else:
            self.selection_callback(None)

    def keyDown_(self, event):
        if event.charactersIgnoringModifiers() == "\x1b" or event.keyCode() == 53:
            self.cancelOperation_(self)
            return

        objc.super(SelectionView, self).keyDown_(event)

    def cancelOperation_(self, sender):
        """Handle AppKit's standard cancellation action, including Escape."""
        self.selection_callback(None)

    def selection_rect(self):
        if self.start_point is None or self.current_point is None:
            return NSMakeRect(0, 0, 0, 0)

        x = min(self.start_point.x, self.current_point.x)
        y = min(self.start_point.y, self.current_point.y)
        width = abs(self.current_point.x - self.start_point.x)
        height = abs(self.current_point.y - self.start_point.y)

        return NSMakeRect(x, y, width, height)

    def drawRect_(self, dirty_rect):
        # Darken the complete overlay.
        NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.30).setFill()
        NSRectFill(self.bounds())

        if self.start_point is None or self.current_point is None:
            return

        selection = self.selection_rect()

        # Make the selected region mostly transparent.
        NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.12).setFill()
        NSRectFill(selection)

        # Draw the rectangle border.
        NSColor.whiteColor().setStroke()

        path = NSBezierPath.bezierPathWithRect_(selection)
        path.setLineWidth_(2.0)
        path.stroke()


class SelectionWindow(NSWindow):
    def canBecomeKeyWindow(self):
        """Allow this borderless window to receive keyboard events."""
        return True


class RectangleSelector(NSObject):
    window = objc.ivar()
    result = objc.ivar()
    app = objc.ivar()
    event_monitor = objc.ivar()
    finished = objc.ivar()

    def select(self) -> Rect | None:
        self.result = None
        self.app = NSApplication.sharedApplication()
        self.event_monitor = None
        self.finished = False

        if self.app.activationPolicy() == NSApplicationActivationPolicyProhibited:
            if not self.app.setActivationPolicy_(
                NSApplicationActivationPolicyAccessory
            ):
                raise RuntimeError("Could not enable keyboard input for the selector")

        # Primary screen. See below for multi-monitor handling.
        screen = NSScreen.mainScreen()
        screen_frame = screen.frame()

        self.window = SelectionWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            screen_frame,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False,
        )

        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setIgnoresMouseEvents_(False)
        self.window.setAcceptsMouseMovedEvents_(True)

        # Show over Spaces and fullscreen applications.
        self.window.setCollectionBehavior_(
            (1 << 0) |  # NSWindowCollectionBehaviorCanJoinAllSpaces
            (1 << 4)    # NSWindowCollectionBehaviorFullScreenAuxiliary
        )

        view_frame = NSMakeRect(
            0,
            0,
            screen_frame.size.width,
            screen_frame.size.height,
        )

        view = SelectionView.alloc().initWithFrame_callback_(
            view_frame,
            self.finish_selection,
        )

        self.window.setContentView_(view)
        self.app.activateIgnoringOtherApps_(True)
        self.window.makeKeyAndOrderFront_(None)
        if not self.window.makeFirstResponder_(view):
            self.window.orderOut_(None)
            raise RuntimeError("Selection view could not become first responder")

        self.event_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSEventMaskKeyDown,
            self.handleKeyEvent_,
        )

        try:
            self.app.runModalForWindow_(self.window)
        finally:
            if self.event_monitor is not None:
                NSEvent.removeMonitor_(self.event_monitor)
                self.event_monitor = None
            self.window.orderOut_(None)

        return self.result

    def handleKeyEvent_(self, event):
        if event.charactersIgnoringModifiers() == "\x1b" or event.keyCode() == 53:
            self.finish_selection(None)
            return None

        return event

    def cancel(self):
        """Cancel selection from outside the modal window's event callbacks."""
        if self.finished:
            return

        self.finished = True
        self.result = None
        self.app.abortModal()

    def finish_selection(self, appkit_rect):
        if self.finished:
            return

        self.finished = True

        if appkit_rect is None:
            self.result = None
        else:
            screen = NSScreen.mainScreen()
            screen_frame = screen.frame()

            # AppKit view coordinates begin at the bottom-left.
            # screencapture -R coordinates begin at the top-left.
            x = appkit_rect.origin.x
            y = (
                screen_frame.size.height
                - appkit_rect.origin.y
                - appkit_rect.size.height
            )

            self.result = Rect(
                x=round(x),
                y=round(y),
                width=round(appkit_rect.size.width),
                height=round(appkit_rect.size.height),
            )

        self.app.stopModal()


def select_rectangle() -> Rect | None:
    if not NSThread.isMainThread():
        raise RuntimeError("select_rectangle() must be called on the main thread")

    selector = RectangleSelector.alloc().init()
    return selector.select()


if __name__ == "__main__":
    rectangle = select_rectangle()
    print(rectangle)
