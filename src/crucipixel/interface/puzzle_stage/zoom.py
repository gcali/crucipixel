from typing import Callable

import cairo

from crucipixel.interface import global_constants
from lightwidgets.animator import RepeatedAction
from lightwidgets.events import MouseButton
from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.buttons import BetterButton
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
from lightwidgets.stock_widgets.layout import SetAlignment, Alignment
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget

class ZoomButton(BetterButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__zoom_action = None
        self.action = lambda: None

    def on_click(self, widget: "Widget", button: MouseButton):
        pass

    def on_mouse_up(self, widget: "Widget", event: MouseEvent):
        if self.__zoom_action is not None:
            self.__zoom_action.end = True
        return super().on_mouse_up(widget, event)

    def on_mouse_down(self, widget: "Widget", event: MouseEvent):
        def action_return_true() -> Callable[[], bool]:
            self.action()
            return True
        self.__zoom_action = RepeatedAction(action_return_true,
                                            skip=6,
                                            interval=100,
                                            first=True).start()
        return super().on_mouse_down(widget, event)


class Zoom(UncheckedContainer):

    def __init__(self, font_size=15, padding=10):

        super().__init__()

        self.padding = padding

        self.__plus_button = ZoomButton("+", font_size, origin=BetterButton.LEFT)
        self.__minus_button = ZoomButton("‒", font_size, origin=BetterButton.LEFT)

        self.add(self.__plus_button)
        self.add(self.__minus_button)

    @property
    def plus_action(self) -> Callable[[], None]:
        return self.__plus_button.action

    @plus_action.setter
    def plus_action(self, action: Callable[[], None]):
        self.__plus_button.action = action

    @property
    def minus_action(self) -> Callable[[], None]:
        return self.__minus_button.action

    @minus_action.setter
    def minus_action(self, action: Callable[[], None]):
        self.__minus_button.action = action

    def layout(self, context: cairo.Context):
        super().layout(context)
        context.save()
        self.__plus_button.layout(context)
        context.restore()
        self.__minus_button.min_height = self.__plus_button.shape.height
        context.save()
        self.__minus_button.layout(context)
        context.restore()

        plus_shape = self.__plus_button.shape
        minus_shape = self.__minus_button.shape

        self.__minus_button.set_translate(self.padding, self.padding/2)
        self.__plus_button.set_translate(
            self.padding + minus_shape.width + self.padding,
            self.padding/2
        )

        self.shape = DrawableRectangle(
            Point(0, 0),
            plus_shape.width + minus_shape.width + 3 * self.padding,
            self.padding + max(plus_shape.height, minus_shape.height)
        )

    def on_draw(self, widget: Widget, context: cairo.Context):
        self.shape.draw_on_context(context)
        context.set_source_rgb(*global_constants.background)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()
        super().on_draw(widget, context)


def main():
    win = MainWindow("Test zoom")
    root = Root(200, 200)
    zoom = Zoom()
    zoom.plus_action = lambda: print("I'm a plus")
    zoom.minus_action = lambda: print("I'm a minus")
    root.set_main_window(win)
    root.set_child(
        SetAlignment(
            SetAlignment(
                zoom,
                Alignment.TOP
            ),
            Alignment.LEFT
        )
    )

    win.start_main()

if __name__ == '__main__':
    main()
