import string
from typing import Callable, Tuple

import cairo

from crucipixel.interface import global_constants
from lightwidgets.animator import RepeatedAction
from lightwidgets.events import MouseButton, MouseEvent, KeyboardEvent
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.stock_widgets.arrow import Arrow, KeepPressingArrow
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
from lightwidgets.stock_widgets.layout import VerticalCenter
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget


class WrapTitle(UncheckedContainer):

    def __init__(self, widget: Widget, title: str, font_size: int=20, distance: int=5):
        super().__init__()
        self.__outer_font_box = None
        self.__wrapper_shape = None
        self.__title_start_point = None
        self.widget = widget
        self.title = title
        self.font_size = font_size
        self.distance = distance
        self.add(widget)

    @property
    def container_size(self) -> Tuple[int, int]:
        size = super().container_size
        x_offset = self.fromWidgetCoords.transform_point(0, 0)[0]
        return size[0] - self.distance * 3 - x_offset, size[1]

    def layout(self, context: cairo.Context):
        super().layout(context)
        context.set_font_size(self.font_size)
        xb, yb, w, h, xa, ya = context.text_extents(self.title)
        font_shape = Rectangle(Point(h/2 + self.distance, self.distance), xa, h)
        self.__title_start_point = Point(font_shape.start.x,
                                         font_shape.start.y + h)
        outer_font_box = DrawableRectangle(
            Point(font_shape.start.x - self.distance,
                  font_shape.start.y - self.distance),
            font_shape.width + 2 * self.distance,
            font_shape.height + 2 * self.distance
        )
        self.__outer_font_box = outer_font_box
        wrapper_shape = DrawableRectangle(
            Point(0, outer_font_box.start.y + outer_font_box.height / 2),
            outer_font_box.start.x + max(
                outer_font_box.width,
                self.widget.shape.width
            ) + self.distance,
            outer_font_box.height/2 + 2*self.distance +
                self.widget.shape.height
        )

        self.widget.set_translate(
            outer_font_box.start.x,
            outer_font_box.start.y + outer_font_box.height + self.distance
        )

        self.__wrapper_shape = wrapper_shape
        self.shape = DrawableRectangle(
            Point(0, 0),
            wrapper_shape.width,
            wrapper_shape.start.y + wrapper_shape.height
        )

    def on_draw(self, widget: Widget, context: cairo.Context):
        super().on_draw(widget, context)
        if self.shape is not None:
            self.__wrapper_shape.draw_on_context(context)
            context.stroke()
            context.set_source_rgb(*global_constants.background)
            self.__outer_font_box.draw_on_context(context)
            context.fill_preserve()
            context.set_source_rgb(0, 0, 0)
            context.stroke()
            context.move_to(self.__title_start_point.x,
                            self.__title_start_point.y)
            context.set_font_size(self.font_size)
            context.show_text(self.title)


class Text(Widget):

    def __init__(self,
                 label: str="",
                 width: int=50,
                 font_size: int=20,
                 padding: int=5):
        super().__init__()
        self.label = label
        self._width = None
        self.width = width
        self.font_size = font_size
        self.padding = padding
        self.shape = None
        def default_acceptable(c: str) -> bool:
            if c in string.digits or c in string.punctuation \
                    or c in string.ascii_letters or c == ' ':
                return True
            else:
                return False
        self.acceptable = default_acceptable

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value
        self.shape = None

    def layout(self, context: cairo.Context):
        if self.shape is None:
            context.save()
            context.set_font_size(self.font_size)
            generator = (context.text_extents(chr(letter) * 10)
                         for letter in range(ord('A'), ord('Z') + 1))
            context.restore()
            sizes = [(xa, h) for xb, yb, w, h, xa, ya in generator]
            max_height = 0
            for w, h in sizes:
                max_height = max(h, max_height)

            # print(max_height)

            width = self.width
            height = self.padding * 3 + max_height

            self.shape = DrawableRectangle(Point(0, 0), width, height)
            # self.clip_rectangle = self.shape

    def on_draw(self, widget: Widget, context: cairo.Context):
        if self.shape is None:
            self.layout(context)

        context.set_font_size(self.font_size)

        self.shape.draw_on_context(context)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()
        shape = self.shape

        label = self.label
        if len(label) > 0 and label[-1] == ' ':
            label += '.'
        xb, yb, w, h, xa, ya = context.text_extents(label)
        context.rectangle(shape.start.x + self.padding,
                          shape.start.y,
                          shape.width - self.padding,
                          shape.height)
        context.clip()
        context.move_to(shape.start.x + shape.width - self.padding - w,
                        shape.start.y + shape.height - self.padding)
        context.show_text(self.label)

    def on_key_down(self, widget: "Widget", event: KeyboardEvent):
        print("Hi from me!")
        if self.is_focused:
            c = event.key
            if c == 'space':
                c = ' '
            if len(c) == 1 and self.acceptable(c):
                if 'shift' in event.modifiers:
                    c = c.upper()
                self.label += c
                self.invalidate()
            elif c == 'backspace':
                self.label = self.label[:-1]
                self.invalidate()

class TextExpandable(Text):

    def __init__(self, *args, expansion_padding: int=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.expansion_padding = expansion_padding

    def layout(self, context: cairo.Context):
        if self.father is not None:
            self.width = self.container_size[0] - self.expansion_padding
        super().layout(context)


class Number(Widget):

    def __init__(self, digits=2, font_size=20, padding=5):
        super().__init__()
        self.digits = digits
        self.font_size = font_size
        self.padding = padding
        self._min_value = 1
        self._value = 1
        self.shape = None

    @property
    def max_value(self) -> int:
        return 10 ** self.digits - 1

    @property
    def min_value(self) -> int:
        return self._min_value

    @min_value.setter
    def min_value(self, value):
        self._min_value = value
        self._value = max(value, self._value)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int):
        self._value = min(self.max_value, max(self.min_value, value))

    def layout(self, context: cairo.Context):
        context.save()
        context.set_font_size(self.font_size)
        generator = (context.text_extents(str(digit) * self.digits)
                     for digit in range(10))
        sizes = [(xa, h) for xb, yb, w, h, xa, ya in generator]
        max_width = 0
        max_height = 0
        for w, h in sizes:
            max_width = max(w, max_width)
            max_height = max(h, max_height)

        width = self.padding * 2 + max_width
        height = self.padding * 2 + max_height

        self.shape = DrawableRectangle(Point(0, 0), width, height)
        context.restore()

    def on_draw(self, widget: Widget, context: cairo.Context):
        shape = self.shape
        if shape is None:
            self.layout(context)
            shape = self.shape
        shape.draw_on_context(context)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        text = str(self.value)
        context.set_font_size(self.font_size)
        xb, yb, w, h, xa, ya = context.text_extents(text)
        context.move_to(shape.start.x + shape.width - w - self.padding,
                        shape.start.y + shape.height - self.padding)
        context.show_text(text)

    def is_point_in(self, p: "Point", category=MouseEvent.UNKNOWN):
        if self.shape is None:
            return False
        else:
            return self.shape.is_point_in(p)

class IncrementDecrement(UncheckedContainer):

    def __init__(self, height=40, width=None, padding=None, distance=None):
        super().__init__()

        if width is None:
            # width = (height / 15) * 7
            width = (height / 5) * 3
        if distance is None:
            distance = height / 5
        if padding is None:
            padding = height / 8

        arrow_width = width - 2 * padding
        arrow_height = (height - 2 * padding - distance) / 2
        self.up_arrow = Arrow(arrow_width,
                              arrow_height,
                              direction=Arrow.UP)
        self.down_arrow = Arrow(arrow_width,
                                arrow_height,
                                direction=Arrow.DOWN)

        self.up_arrow.translate(arrow_width / 2 + padding,
                                padding + arrow_height / 2)
        self.down_arrow.translate(arrow_width / 2 + padding,
                                  height - padding - arrow_height/2)

        self.add(self.up_arrow)
        self.add(self.down_arrow)
        self.shape = DrawableRectangle(Point(0, 0), width, height)

        self.increment_action = lambda: None
        self.decrement_action = lambda: None

        self.__moving_action = None
        self.__skip = 0

    def set_increment_action(self, action: Callable[[], None]):
        self.increment_action = action

    def set_decrement_action(self, action: Callable[[], None]):
        self.decrement_action = action

    def on_draw(self, widget: Widget, context: cairo.Context):
        context.save()
        self.shape.draw_on_context(context)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()
        context.restore()
        super().on_draw(widget, context)

    def is_point_in(self, p: Point, category=MouseEvent.UNKNOWN):
        return self.shape.is_point_in(p)

    def on_mouse_down(self, widget: "Widget", event: MouseEvent):
        # self.__skip = 4
        if event.y <= self.shape.height / 2:
            action = self.increment_action
        else:
            action = self.decrement_action
        self.__moving_action = RepeatedAction(action,
                                              skip=10,
                                              interval=50,
                                              first=True).start()
        return True

    def on_mouse_up(self, widget: "Widget", event: MouseEvent):
        if self.__moving_action is not None:
            self.__moving_action.end = True
        return False


class NumberSelector(UncheckedContainer):

    def __init__(self, digits=2, font_size=20, padding=5):
        super().__init__()
        self.number = Number(digits, font_size, padding)
        self.increment_decrement = None
        self.add(self.number)

    def layout(self, context: cairo.Context):
        super().layout(context)
        if self.increment_decrement is None:
            self.increment_decrement = IncrementDecrement(
                height=self.number.shape.height
            )
            self.increment_decrement.set_translate(self.number.shape.width, 0)
            self.add(self.increment_decrement)
            self._select_actions()
            self.shape = DrawableRectangle(
                Point(0, 0),
                self.number.shape.width + self.increment_decrement.shape.width,
                self.number.shape.height
            )

    def _select_actions(self):
        def create_change_value(change: int):
            def change_value() -> bool:
                self.number.value += change
                self.number.invalidate()
                return True
            return change_value
        self.increment_decrement.set_increment_action(create_change_value(1))
        self.increment_decrement.set_decrement_action(create_change_value(-1))

    def on_draw(self, widget: Widget, context: cairo.Context):
        if self.increment_decrement is None:
            self.layout(context)
        super().on_draw(widget, context)


class EditorInputWidgets(UncheckedContainer):

    def __init__(self):
        super().__init__()
        self.rows_cols_distance = 40
        self.rows = WrapTitle(NumberSelector(2), "Rows")
        self.cols = WrapTitle(NumberSelector(2), "Cols")
        self.text = WrapTitle(TextExpandable(expansion_padding=2), "Title")
        self.add(self.rows)
        self.add(self.cols)
        self.add(self.text)
        self._width = 0

    @property
    def container_size(self):
        cs = super().container_size
        return self._width, cs[1]


    def layout(self, context: cairo.Context):
        self.rows.layout(context)
        self.cols.layout(context)
        container_width = super().container_size[0]
        offset_x = self.rows.shape.width + max(
            self.rows_cols_distance,
            container_width - self.rows.shape.width - self.cols.shape.width
        )

        self.cols.set_translate(
            offset_x,
            0
        )
        self._width = offset_x + self.cols.shape.width
        self.text.layout(context)
        self.text.set_translate(0, self.rows.shape.height + self.rows_cols_distance)
        self.shape = DrawableRectangle(
            Point(0, 0),
            self._width,
            self.rows.shape.height + self.rows_cols_distance + self.text.shape.height
        )

class EditorInput(WrapTitle):

    def __init__(self):
        self.widgets = EditorInputWidgets()
        super().__init__(self.widgets, "Ciao")

def main() -> int:
    main_window = MainWindow(title="Number test")
    root = Root(100, 100)
    root.set_main_window(main_window)
    # ns = NumberSelector()
    # ns.translate(50, 50)
    #
    # t = WrapTitle(WrapTitle(TextExpandable(label="Ciao come stai ti sembra un giorno felice per andare al mare"), "Ciao"), "Come")
    # # t = WrapTitle(ns, "Ciao")
    # t.translate(50, 50)
    # root.set_child(t)
    root.set_child(VerticalCenter(EditorInput()))

    main_window.start_main()
    return 0

if __name__ == '__main__':
    main()
