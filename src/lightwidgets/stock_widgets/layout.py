from enum import Enum

import cairo

from lightwidgets.geometry import Rectangle
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.widget import Widget


class Alignment(Enum):

    LEFT = 0,
    TOP = 1,
    VERTICAL_CENTER = 2,
    HORIZONTAL_CENTER = 3,
    RIGHT = 4,
    BOTTOM = 5

    @property
    def is_horizontal(self) -> bool:
        return self == Alignment.LEFT or \
               self == Alignment.HORIZONTAL_CENTER or \
               self == Alignment.RIGHT

    @property
    def is_vertical(self) -> bool:
        return not self.is_horizontal


class VerticalCenter(UncheckedContainer):

    def __init__(self, widget: Widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widget
        self.add(widget)

    def layout(self, context: cairo.Context):
        super().layout(context)
        shape = self.widget.shape
        if shape is not None and self.father is not None:
            container_height = self.container_size[1]
            widget_height = shape.height
            offset_y = max(container_height - widget_height, 0) / 2
            self.widget.set_translate(0, offset_y)


class SetAlignment(UncheckedContainer):

    def __init__(self, widget: Widget, alignment: Alignment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widget
        self.add(widget)
        self.alignment = alignment

    @property
    def layout_shape(self) -> Rectangle:
        try:
            return self.father.shape
        except AttributeError:
            return None

    @property
    def shape(self) -> Rectangle:
        return self.widget.shape

    def layout(self, context: cairo.Context):
        super().layout(context)
        if self.father is not None:
            try:
                father_shape = self.father.layout_shape
            except AttributeError:
                father_shape = self.father.shape
            shape = self.widget.shape
            if shape is not None and father_shape is not None:
                alignment = self.alignment
                if alignment.is_horizontal:
                    container_size = father_shape.width
                    widget_size = shape.width

                    def set_offset(value):
                        self.widget.set_translate(value, 0)
                else:
                    container_size = father_shape.height
                    widget_size = shape.height

                    def set_offset(value):
                        self.widget.set_translate(0, value)

                if alignment == Alignment.RIGHT:
                    alignment = Alignment.BOTTOM
                elif alignment == Alignment.LEFT:
                    alignment = Alignment.TOP
                elif alignment == Alignment.HORIZONTAL_CENTER:
                    alignment = Alignment.VERTICAL_CENTER

                if alignment == Alignment.VERTICAL_CENTER:
                    set_offset((container_size - widget_size) / 2)
                elif alignment == Alignment.TOP:
                    set_offset(0)
                else:
                    set_offset(container_size - widget_size)

