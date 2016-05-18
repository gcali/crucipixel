from numbers import Number
from typing import Tuple, Callable

import cairo


# from gi.repository import Gtk
# from gi.repository import Gdk

# from crucipixel.interface import global_constants
from lightwidgets.events import MouseEvent, MouseButton
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.stock_widgets.buttons import BetterButton, \
    click_left_button_wrapper
from lightwidgets.stock_widgets.containers import UncheckedContainer
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
        self.__background_rectangle = None
        self.__label_rectangle = None
        self.padding = 20
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

    def layout(self, context: cairo.Context):
        width, height = self.container_size
        self.__background_rectangle = DrawableRectangle(Point(0, 0), width, height)

        context.set_font_size(self.font_size)

        xb, yb, w, h, xa, ya = context.text_extents(self.label)
        padding = self.padding

        rectangle_width = xa + 2 * padding
        rectangle_height = padding + h
        start_x = (width - rectangle_width) / 2
        start_y = (height - rectangle_height) / 2

        self.__label_rectangle = DrawableRectangle(Point(start_x, start_y),
                                                   rectangle_width,
                                                   rectangle_height)

    def on_draw(self, widget: Widget, context: cairo.Context):

        context.set_source_rgba(*self.background_color, self.background_alpha)
        self.__background_rectangle.draw_on_context(context)
        context.fill()

        context.set_font_size(self.font_size)

        self.__label_rectangle.draw_on_context(context)
        context.set_source_rgb(.3, .3, .3)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        rectangle = self.__label_rectangle
        start = rectangle.start
        context.move_to(start.x + self.padding,
                        start.y + rectangle.height - self.padding/2)
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


class ButtonedTextOverlay(UncheckedContainer):

    def __init__(self,
                 label: str,
                 font_size: int=20,
                 back_label: str="Back",
                 ok_label: str="Ok",
                 background_color: Tuple[Number, Number, Number]=(.3, .3, .3),
                 background_alpha: Number=.5):
        super().__init__()

        self.label = label
        self.font_size = font_size
        self.background_color = background_color
        self.background_alpha = background_alpha
        self.padding = 20

        self.__background_rectangle = None
        self.__overlay_shape = None
        self.__label_start = Point(0, 0)

        button_font_size = font_size * .8
        self.__back_button = BetterButton(back_label, button_font_size, origin=BetterButton.LEFT)
        self.__ok_button = BetterButton(ok_label, button_font_size, origin=BetterButton.RIGHT)

        self.add(self.__back_button)
        self.add(self.__ok_button)

    def set_back_action(self, action: Callable[[], None]):
        self.__back_button.on_click_action = click_left_button_wrapper(action)

    def set_ok_action(self, action: Callable[[], None]):
        self.__ok_button.on_click_action = click_left_button_wrapper(action)

    def layout(self, context: cairo.Context):
        super().layout(context)
        width, height = self.container_size
        self.__background_rectangle = DrawableRectangle(Point(0, 0), width, height)

        context.set_font_size(self.font_size)

        xb, yb, w, h, xa, ya = context.text_extents(self.label)
        padding = self.padding

        label_start = Point((width - xa)/2, (height - h)/2)
        self.__label_start = Point(label_start.x, label_start.y + h)
        label_shape = Rectangle(label_start, xa, h)

        back_shape = self.__back_button.shape
        ok_shape = self.__ok_button.shape

        button_y = label_start.y + label_shape.height + padding/2
        total_height = label_shape.height +\
                       max(back_shape.height, ok_shape.height) +\
                       1.5 * padding
        button_line_width = back_shape.width + ok_shape.width + 2*padding
        if button_line_width + 2*padding <= label_shape.width:
            self.__back_button.set_translate(
                label_start.x + padding,
                # (width - button_line_width)/2 + back_shape.width,
                button_y
            )
            self.__ok_button.set_translate(
                label_start.x + label_shape.width - padding,
                # (width + button_line_width)/2 - ok_shape.width,
                button_y
            )
            self.__overlay_shape = DrawableRectangle(
                Point(label_start.x - padding, label_start.y - padding/2),
                label_shape.width + 2 * padding,
                total_height
            )
        else:
            self.__back_button.set_translate(
                (width - button_line_width)/2,
                button_y
            )
            self.__ok_button.set_translate(
                (width + button_line_width)/2,
                button_y
            )
            self.__overlay_shape = DrawableRectangle(
                Point((width - button_line_width)/2 - padding,
                      label_start.y - padding/2),
                2*padding + button_line_width,
                total_height
            )


    def on_draw(self, widget: Widget, context: cairo.Context):

        context.set_source_rgba(*self.background_color, self.background_alpha)
        self.__background_rectangle.draw_on_context(context)
        context.fill()

        context.set_font_size(self.font_size)

        self.__overlay_shape.draw_on_context(context)
        context.set_source_rgb(.3, .3, .3)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        context.move_to(self.__label_start.x, self.__label_start.y)
        context.show_text(self.label)
        super().on_draw(widget, context)

    def on_mouse_down(self, widget: Widget, event: MouseEvent):
        super().on_mouse_down(widget, event)
        return True

    def on_mouse_move(self, widget: Widget, event: MouseEvent):
        super().on_mouse_move(widget, event)
        return True


def main() -> int:
    main_window = MainWindow(title="Test Overlay")
    # main_window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    # print(Gdk.RGBA)
    main_window.set_background_rgba(.9, .9, .9, 1)
    root = Root()
    root.set_main_window(main_window)
    root.set_min_size(200, 200)
    button_overlay = ButtonedTextOverlay("E con questo?" * 3)
    button_overlay.set_back_action(lambda: print("Back!"))
    button_overlay.set_ok_action(lambda: print("Ok!"))
    root.set_child(button_overlay)
    # text_overlay = TextOverlay("PUZZLE SOLVED")
    # text_overlay.on_click_action = lambda: print("Puzzle Solved!")
    # root.set_child(text_overlay)

    # root.set_min_size(100, 100)

    main_window.start_main()
    return 0

if __name__ == '__main__':
    main()
