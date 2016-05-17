from enum import Enum
from typing import Tuple

import cairo
import sys

from lightwidgets.geometry import Rectangle, Point
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
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


class Border(UncheckedContainer):

    def __init__(self, widget, top:int=0, bottom:int=0, right:int=0, left:int=0):
        super().__init__()
        self.__top = top
        self.__bottom = bottom
        self.__right = right
        self.__left = left

        self.widget = widget
        self.__panel = UncheckedContainer()
        self.__panel.translate(left, top)
        self.__panel.add(widget)
        self.add(self.__panel)

    @property
    def container_size(self) -> Tuple[int, int]:
        father_container = self.father.container_size
        return father_container[0] - self.__left - self.__right, \
               father_container[1] - self.__top - self.__bottom

    @property
    def shape(self) -> DrawableRectangle:
        return self.father.shape

    @property
    def layout_shape(self) -> DrawableRectangle:
        base_shape = self.father.shape
        return DrawableRectangle(Point(0, 0),
                                 base_shape.width - self.__left - self.right,
                                 base_shape.height - self.__top - self.bottom)


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
            return self.father.layout_shape
        except AttributeError:
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
                        self.set_translate(value, 0)
                else:
                    container_size = father_shape.height
                    widget_size = shape.height

                    def set_offset(value):
                        self.set_translate(0, value)

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

