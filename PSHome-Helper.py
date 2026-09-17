#!/usr/bin/env python3
"""
PSHome-Helper.py — top bar that toggles mutually exclusive web panes.
"""
import gi
gi.require_version("Gtk", "3.0")
try:
    gi.require_version("WebKit2", "4.1")
except ValueError:
    gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, Gdk, WebKit2, GLib

# width/height: int pixels, or "25%" / "50%" of the primary monitor
# x: left | center | right
# y: top | middle | bottom
PANES = {
    "who": {
        "title": "Who's Online",
        "url": "https://destinationhome.online/players",
        "width": "70%",
        "height": "70%",
        "x": "center",
        "y": "middle",
    },
    "shop": {
        "title": "Shop",
        "url": "https://destinationhome.online/catalogue",
        "width": "70%",
        "height": "70%",
        "x": "center",
        "y": "middle",
    },
    "rewards": {
        "title": "Rewards",
        "url": "https://stores.yourpshome.net/index.php?route=common/home",
        "width": "70%",
        "height": "70%",
        "x": "center",
        "y": "middle",
    },
}


def primary_geom():
    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor() or display.get_monitor(0)
    return monitor.get_geometry()


def parse_len(value, total):
    if isinstance(value, str) and value.endswith("%"):
        return max(1, int(total * float(value[:-1]) / 100.0))
    return max(1, int(value))


def pane_rect(spec):
    g = primary_geom()
    w = parse_len(spec.get("width", "25%"), g.width)
    h = parse_len(spec.get("height", "50%"), g.height)
    w = min(w, g.width)
    h = min(h, g.height)

    x_align = spec.get("x", "center")
    y_align = spec.get("y", "middle")
    if x_align == "left":
        x = g.x
    elif x_align == "right":
        x = g.x + g.width - w
    else:
        x = g.x + (g.width - w) // 2

    if y_align == "top":
        y = g.y
    elif y_align == "bottom":
        y = g.y + g.height - h
    else:
        y = g.y + (g.height - h) // 2
    return x, y, w, h


def style_float(win):
    win.set_keep_above(True)
    win.set_skip_taskbar_hint(True)
    win.set_skip_pager_hint(True)
    win.set_type_hint(Gdk.WindowTypeHint.UTILITY)
    win.stick()


def place_window(win, spec):
    x, y, w, h = pane_rect(spec)
    win.resize(w, h)
    win.set_size_request(w, h)
    win.move(x, y)
    return False


class Pane:
    def __init__(self, app, key, spec):
        self.key = key
        self.spec = spec
        self.win = Gtk.ApplicationWindow(application=app, title=spec["title"])
        _x, _y, w, h = pane_rect(spec)
        self.win.set_default_size(w, h)
        self.win.set_size_request(w, h)
        style_float(self.win)
        self.win.connect("delete-event", self._on_close)
        self.win.connect("map-event", lambda *a: place_window(self.win, self.spec) or False)

        view = WebKit2.WebView()
        view.load_uri(spec["url"])
        self.win.add(view)
        self.win.show_all()
        self.win.hide()

    def _on_close(self, *args):
        self.hide()
        return True

    def visible(self):
        return self.win.get_visible()

    def show(self):
        self.win.show()
        self.win.present()
        place_window(self.win, self.spec)
        GLib.idle_add(place_window, self.win, self.spec)
        GLib.timeout_add(50, lambda: place_window(self.win, self.spec))

    def hide(self):
        self.win.hide()


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.webpane.toolbar")
        self.bar = None
        self.panes = {}
        self.buttons = {}

    def do_activate(self):
        if self.bar:
            return
        for key, spec in PANES.items():
            self.panes[key] = Pane(self, key, spec)
        self._build_bar()
        self.bar.show_all()
        GLib.idle_add(self._place_bar)

    def _build_bar(self):
        self.bar = Gtk.ApplicationWindow(application=self, title="webpane")
        self.bar.set_decorated(False)
        self.bar.set_resizable(False)
        style_float(self.bar)
        self.bar.connect("delete-event", lambda *a: self.quit() or True)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(3)
        box.set_margin_bottom(3)

        handle = Gtk.Label(label="☰")
        handle.set_tooltip_text("Drag")
        box.pack_start(handle, False, False, 0)

        for key, spec in PANES.items():
            btn = Gtk.ToggleButton(label=spec["title"])
            btn.connect("toggled", self._on_toggle, key)
            self.buttons[key] = btn
            box.pack_start(btn, False, False, 0)

        quit_btn = Gtk.Button(label="Quit")
        quit_btn.connect("clicked", lambda *_: self.quit())
        box.pack_start(quit_btn, False, False, 0)

        self.bar.add(box)
        for w in (self.bar, handle):
            w.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            w.connect("button-press-event", self._drag_bar)

        GLib.timeout_add(250, self._sync_buttons)

    def show_only(self, key):
        for k, pane in self.panes.items():
            if k == key:
                pane.show()
            else:
                pane.hide()

    def hide_all(self):
        for pane in self.panes.values():
            pane.hide()

    def _on_toggle(self, button, key):
        if button.get_active():
            self.show_only(key)
        elif self.panes[key].visible():
            self.hide_all()

    def _sync_buttons(self):
        for key, pane in self.panes.items():
            btn = self.buttons[key]
            want = pane.visible()
            if btn.get_active() != want:
                btn.handler_block_by_func(self._on_toggle)
                btn.set_active(want)
                btn.handler_unblock_by_func(self._on_toggle)
        return True

    def _place_bar(self):
        g = primary_geom()
        ww, _wh = self.bar.get_size()
        if ww < 2:
            ww = 280
        self.bar.move(g.x + (g.width - ww) // 2, g.y)
        return False

    def _drag_bar(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.bar.begin_move_drag(
                event.button, int(event.x_root), int(event.y_root), event.time
            )
        return False


if __name__ == "__main__":
    App().run(None)
