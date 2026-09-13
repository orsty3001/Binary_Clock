#!/usr/bin/env python3
"""A native Linux binary clock inspired by Newson's Electronics' watch."""
import argparse
import datetime as dt
import math
from pathlib import Path

WEIGHTS = (32, 16, 8, 4, 2, 1)
COLORS = ((1, .22, .28), (1, .85, .24), (.13, .95, .55))


def time_bits(hour, minute, second):
    """Return columns H/M/S, each ordered from 32 down to 1."""
    if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
        raise ValueError('Time must be within 00:00:00–23:59:59')
    return tuple(tuple(bool(value & bit) for bit in WEIGHTS)
                 for value in (hour, minute, second))


def draw_clock(ctx, width, height, now, brightness=1.0, labels=True, readout=True):
    """Shared screen/offscreen renderer; all coordinates scale with the window."""
    ctx.set_source_rgb(.035, .06, .06)
    ctx.paint()
    scale = min(width / 420, height / 640)
    ctx.save()
    ctx.translate((width - 420 * scale) / 2, (height - 640 * scale) / 2)
    ctx.scale(scale, scale)

    def rect(x, y, w, h, color):
        ctx.set_source_rgb(*color)
        ctx.rectangle(x, y, w, h)
        ctx.fill()

    def text(x, y, value, size, color=(.65, .76, .73)):
        ctx.select_font_face('monospace')
        ctx.set_font_size(size)
        ctx.set_source_rgb(*color)
        ext = ctx.text_extents(value)
        ctx.move_to(x - ext.width / 2 - ext.x_bearing, y)
        ctx.show_text(value)

    def circle(x, y, r, color):
        ctx.set_source_rgb(*color)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.fill()

    text(210, 37, 'B I N A R Y   W A T C H', 16, (.88, .94, .9))
    text(210, 62, 'LOCAL TIME / 24 HOUR', 10)
    # Green board, metal fasteners, subtle circuit traces.
    rect(42, 85, 336, 442, (.055, .23, .19))
    for x in (54, 366):
        for y in (97, 515):
            circle(x, y, 4, (.45, .56, .51))
            rect(x - 2, y - .6, 4, 1.2, (.15, .22, .2))
    for x in (125, 210, 295):
        rect(x - 28, 110, 1, 380, (.09, .30, .25))
    columns = time_bits(now.hour, now.minute, now.second)
    for col, bits in enumerate(columns):
        x = 125 + col * 85
        for row, on in enumerate(bits):
            y = 137 + row * 62
            rect(x - 24, y - 24, 48, 48, (.42, .49, .42))
            rect(x - 21, y - 21, 42, 42, (.16, .23, .19))
            color = tuple(c * brightness for c in COLORS[col]) if on else (.19, .27, .22)
            if on:
                circle(x, y, 20, tuple(c * .30 for c in color))
                circle(x, y, 17, tuple(c * .62 for c in color))
            circle(x, y, 14, color)
            if on:
                circle(x - 4, y - 4, 4, tuple(min(1, c + .28 * brightness) for c in color))
        text(x, 506, ('H', 'M', 'S')[col], 17)
    if labels:
        for row, weight in enumerate(WEIGHTS):
            for x in (72, 349):
                text(x, 142 + row * 62, f'{weight:02}', 13)
    if readout:
        text(210, 574, now.strftime('%H:%M:%S'), 32, (.91, .96, .91))
        text(210, 602, now.strftime('%a, %d %b %Y'), 12)
    else:
        text(210, 574, 'ADD THE LIT VALUES IN EACH COLUMN', 11)
    text(210, 629, 'H  HOURS     M  MINUTES     S  SECONDS', 10)
    ctx.restore()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', type=Path, help='Render a PNG without opening a window')
    parser.add_argument('--time', default='18:42:13', help='Time for --render (HH:MM:SS)')
    args = parser.parse_args()
    if args.render:
        import cairo
        try:
            value = dt.datetime.combine(dt.date(2026, 1, 1), dt.time.fromisoformat(args.time))
        except ValueError:
            parser.error('--time must be a valid HH:MM:SS time')
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 420, 640)
        draw_clock(cairo.Context(surface), 420, 640, value)
        surface.write_to_png(str(args.render))
        return

    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib, Gdk

    class Clock(Gtk.Application):
        def __init__(self):
            super().__init__(application_id='local.binarywatch.Clock')
            self.window = None
            self.brightness = 1.0
            self.labels = True
            self.readout = True
            self.fullscreen = False

        def do_activate(self):
            if self.window:
                self.window.present()
                return
            self.window = Gtk.ApplicationWindow(application=self, title='Binary Watch')
            self.window.set_default_size(420, 730)
            self.window.set_size_request(320, 520)
            self.window.connect('key-press-event', self.key)
            self.window.connect('destroy', self.closed)
            layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.window.add(layout)
            self.canvas = Gtk.DrawingArea()
            self.canvas.set_hexpand(True)
            self.canvas.set_vexpand(True)
            self.canvas.connect('draw', self.draw)
            layout.pack_start(self.canvas, True, True, 0)
            controls = Gtk.Box(spacing=10, margin=10)
            for label, field in [('Values', 'labels'), ('Digital time', 'readout')]:
                button = Gtk.CheckButton(label=label)
                button.set_active(True)
                button.connect('toggled', self.toggle, field)
                controls.pack_start(button, False, False, 0)
            top = Gtk.CheckButton(label='Keep above')
            top.set_tooltip_text('Keep above other windows (depends on your desktop)')
            top.connect('toggled', lambda b: self.window.set_keep_above(b.get_active()))
            controls.pack_start(top, False, False, 0)
            layout.pack_start(controls, False, False, 0)
            bottom = Gtk.Box(spacing=10, margin_start=12, margin_end=12, margin_bottom=10)
            bottom.pack_start(Gtk.Label(label='Brightness'), False, False, 0)
            slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 20, 100, 5)
            slider.set_value(100)
            slider.set_draw_value(False)
            slider.set_tooltip_text('LED brightness')
            slider.connect('value-changed', self.set_brightness)
            bottom.pack_start(slider, True, True, 0)
            help_button = Gtk.Button(label='How to read')
            help_button.connect('clicked', self.help)
            bottom.pack_end(help_button, False, False, 0)
            layout.pack_start(bottom, False, False, 0)
            self.window.show_all()
            self.timer = GLib.timeout_add(100, self.tick)
            self.last_second = None

        def draw(self, widget, ctx):
            size = widget.get_allocation()
            draw_clock(ctx, size.width, size.height, dt.datetime.now(),
                       self.brightness, self.labels, self.readout)

        def tick(self):
            now = dt.datetime.now().replace(microsecond=0)
            if now != self.last_second:
                self.last_second = now
                self.canvas.queue_draw()
            return True

        def closed(self, *_):
            GLib.source_remove(self.timer)
            self.window = None

        def toggle(self, button, field):
            setattr(self, field, button.get_active())
            self.canvas.queue_draw()

        def set_brightness(self, slider):
            self.brightness = slider.get_value() / 100
            self.canvas.queue_draw()

        def key(self, _window, event):
            if event.keyval == Gdk.KEY_F11:
                self.fullscreen = not self.fullscreen
                (self.window.fullscreen if self.fullscreen else self.window.unfullscreen)()
                return True
            if event.keyval == Gdk.KEY_Escape and self.fullscreen:
                self.fullscreen = False
                self.window.unfullscreen()
                return True
            return False

        def help(self, *_):
            dialog = Gtk.MessageDialog(transient_for=self.window, modal=True,
                message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.CLOSE,
                text='Read time like the binary watch')
            dialog.format_secondary_text(
                'This program lets you see how the original binary watch would look '
                'running in real time. The watch design originated with Newson’s Electronics, '
                'whose project “A Watch for Nerds: the Binary Watch” is published on Instructables.\n\n'
                'Left to right: hours (red), minutes (yellow), seconds (green).\n\n'
                'Top to bottom: 32, 16, 8, 4, 2, 1. Add the lit values in each column. '
                'For example, 16 + 2 = 18 hours.\n\n'
                'Uses your computer’s local time in 24-hour format. The watch’s blue '
                'battery warning is not simulated.\n\nF11: fullscreen. Escape: leave fullscreen.')
            source_link = Gtk.LinkButton.new_with_label(
                'https://www.instructables.com/A-Watch-for-Nerds-the-Binary-Watch',
                'View the original watch project by Newson’s Electronics')
            source_link.set_halign(Gtk.Align.CENTER)
            dialog.get_content_area().pack_start(source_link, False, False, 8)
            source_link.show()
            dialog.run()
            dialog.destroy()

    Clock().run(None)


if __name__ == '__main__':
    main()
