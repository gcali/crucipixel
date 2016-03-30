from numbers import Number
from typing import Tuple

import cairo


from gi.repository import Gtk
from gi.repository import Gdk

from crucipixel.interface import global_constants
from lightwidgets.events import MouseEvent, MouseButton
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget


class TextOverlay(Widget):

    def __init__(self,
                 label: str,
                 font_size: int=20,
                 background_color: Tuple[Number, Number, Number]=(.3, .3, .3),
                 background_alpha: Number=.5):
        super().__init__()
        self.background_color = background_color
        self.background_alpha = background_alpha
        self.label = label
        self.font_size = font_size
        self.on_click_action = None

    def is_point_in(self,p: Point, category=MouseEvent.UNKNOWN):
        return True

    def on_click(self, widget: "Widget", button: MouseButton):
        if self.on_click_action is not None:
            self.on_click_action()

    def on_draw(self, widget: Widget, context: cairo.Context):
        width, height = self.container_size
        background_rectangle = DrawableRectangle(Point(0, 0), width, height)
        context.set_source_rgba(*self.background_color, self.background_alpha)
        background_rectangle.draw_on_context(context)
        context.fill()

        context.set_font_size(self.font_size)

        xb, yb, w, h, xa, ya = context.text_extents(self.label)
        padding = 20

        rectangle_width = xa + 2 * padding
        rectangle_height = padding + h
        start_x = (width - rectangle_width) / 2
        start_y = (height - rectangle_height) / 2
        label_rectangle = DrawableRectangle(Point(start_x, start_y),
                                            rectangle_width,
                                            rectangle_height)
        label_rectangle.draw_on_context(context)
        context.set_source_rgb(.3, .3, .3)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        context.move_to(start_x + padding, start_y + padding/2 + h)
        context.show_text(self.label)

    def on_mouse_down(self, widget: "Widget", event: MouseEvent) -> bool:
        super().on_mouse_down(widget, event)
        return True

    # def on_mouse_up(self, widget: "Widget", event: MouseEvent) -> bool:
    #     super().on_mouse_up(widget, event)
    #     return True

    def on_mouse_move(self, widget: "Widget", event: MouseEvent) -> bool:
        super().on_mouse_move(widget, event)
        return True




def main() -> int:
    main_window = MainWindow(title="Test Overlay")
    # main_window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    # print(Gdk.RGBA)
    main_window.set_background_rgba(.9, .9, .9, 1)
    root = Root()
    root.set_main_window(main_window)
    text_overlay = TextOverlay("PUZZLE SOLVED")
    text_overlay.on_click_action = lambda: print("Puzzle Solved!")
    root.set_child(text_overlay)

    root.set_min_size(100, 100)

    main_window.start_main()
    return 0

if __name__ == '__main__':
    main()
