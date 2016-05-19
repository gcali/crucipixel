import cairo

from crucipixel.interface import global_constants
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.buttons import BetterButton
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
from lightwidgets.stock_widgets.layout import SetAlignment, Alignment
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget


class Zoom(UncheckedContainer):

    def __init__(self, font_size=15, padding=10):

        super().__init__()

        self.padding = padding

        self.__plus_button = BetterButton("+", font_size, origin=BetterButton.LEFT)
        self.__minus_button = BetterButton("‒", font_size, origin=BetterButton.LEFT)
        # self.__minus_button = BetterButton("—", font_size, origin=BetterButton.LEFT)

        self.add(self.__plus_button)
        self.add(self.__minus_button)

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
    root.set_main_window(win)
    root.set_child(
        SetAlignment(
            SetAlignment(
                Zoom(),
                Alignment.TOP
            ),
            Alignment.LEFT
        )
    )

    win.start_main()

if __name__ == '__main__':
    main()
