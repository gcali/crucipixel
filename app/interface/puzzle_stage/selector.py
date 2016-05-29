'''
Created on May 19, 2015

@author: giovanni
'''
from typing import List, Iterable, Callable

from gi.repository import cairo

from lightwidgets.geometry import Point, Rectangle
from collections import OrderedDict

from lightwidgets.stock_widgets.buttons import BetterButton
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRoundedRectangle, \
    DrawableRectangle
from lightwidgets.events import MouseEvent, MouseButton
import math
from app.interface import global_constants
from lightwidgets.stock_widgets.root import MainWindow
from lightwidgets.stock_widgets.root import Root
from lightwidgets.stock_widgets.widget import Widget

from gi.repository import Gtk
from gi.repository import Gdk

from lightwidgets.support import DefaultDict


class BetterSelector(UncheckedContainer):

    def __init__(self, size=20):

        super().__init__()

        self.option_colours = [
            global_constants.start_selected,
            global_constants.start_empty,
            global_constants.start_default
        ]

        self._buttons = [
            BetterButton("",
                         padding=size/2,
                         background_color=colour,
                         origin=BetterButton.LEFT)
            for colour in self.option_colours
        ]

        for b in self._buttons:
            self.add(b)

        self.bounding_rectangle = None

        self.size = size
        self.padding = 5

        self._handle_layout()

    def set_click_action(self, index: int, action: Callable[[MouseButton], None]):
        print("Setting selector for:", index)
        self._buttons[index].on_click_action = action

    def _handle_layout(self):
        start_y = self.padding
        for button in self._buttons:
            button.set_translate(self.padding, start_y)
            start_y += self.size + self.padding

        self.bounding_rectangle = DrawableRectangle(
            Point(0, 0),
            self.padding * 2 + self.size,
            start_y
        )

        self.shape = self.bounding_rectangle

    @property
    def width(self) -> int:
        return self.bounding_rectangle.width + 1

    def on_draw(self, widget: Widget, context: cairo.Context):
        context.save()
        context.set_line_width(1)
        self.bounding_rectangle.draw_on_context(context)
        context.set_source_rgb(*global_constants.background)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()
        context.restore()
        super().on_draw(widget, context)


class Selector(Widget):

    def __init__(self,start=Point(0,0),options=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "SelectorWindow"
        self.start = start
        self.padding = 5
        self.font_size = 20
        if options is None:
            self.options = OrderedDict(
                                [("Left",(.4,.4,.4)),
                                 ("Right",(1,1,1)),
                                 ("Middle",(.8,.8,.8))])
        else:
            self.options = options
        self._total_height = 0
        self._total_width = 0


    @property
    def total_height(self):
        last_rectangle = self._get_rectangle_list(self.options.keys())[-1]
        return last_rectangle.start.y + last_rectangle.height + 2 #add line width
    @property
    def total_width(self):
        rectangle = self._get_rectangle_list(self.options.keys())[0]
        return rectangle.start.x + rectangle.width + self.padding + self.maxW

    def _get_rectangle_list(self,lines) -> "None//Raises: AttributeError":
        size = self._get_rectangle_size()
        return [DrawableRoundedRectangle(Point(self.padding,
                                self.padding*(1+i) + size* i),
                                size,
                                size) for i in range(len(lines))]

    def _get_rectangle_size(self) -> "num//Raises: AttributeError":
        if not hasattr(self, "maxW") or not hasattr(self, "maxH"):
            raise AttributeError("Can't get cell_size until first drawn")
        return math.floor(self.maxH * .6)

    def _get_text_max_size(self, context, lines):
        sizes = []
        for l in lines:
            xb, yb, width, height, _, _ = context.text_extents(l)
            sizes.append(Rectangle(Point(xb, yb), width, height))

        maxW, maxH = 0, 0
        for s in sizes:
            maxW = max(maxW, s.width - s.start.x)
            maxH = max(maxH, s.height - s.start.y)

        return maxH, maxW

    def on_mouse_down(self, w, e):
        new_colors = { "left" : "empty",
                       "right" : "selected",
                       "middle" : "default"}
        rectangle_list = self._get_rectangle_list(self.options.keys())
        r = 0
        found = False
        for i,rectangle in enumerate(rectangle_list):
            if rectangle.is_point_in(Point(e.x,e.y),delta=2):
                r=i
                found = True
                break
        if found:
            selected = (list(self.options.keys())[r]).lower()
            self.broadcast_lw_signal("select_color",selected,new_colors[selected])
            return True
        else:
            return False

    def is_point_in(self, p:"Point",category=MouseEvent.UNKNOWN):
        try:
            return p.x >= 0 and p.x <= self.total_width and\
                   p.y >= 0 and p.y <= self.total_height
        except AttributeError:
            return False

    def on_draw(self,widget,context):
        context.save()
        context.set_font_size(self.font_size)
        context.set_line_width(1)
        lines = self.options.keys()
        maxH, maxW = self._get_text_max_size(context, lines)
        self.maxH = maxH
        self.maxW = maxW
        rectangle_size = self._get_rectangle_size()
        self._total_height = maxH
        self._total_width = self.padding * 2 + rectangle_size + maxW
        context.rectangle(-2,-2,self.total_width + 8, self.total_height + 6)
        context.set_source_rgb(0,0,0)
        context.stroke_preserve()
        context.set_source_rgb(*global_constants.background)
        context.fill()
        line_color_rectangle = zip(self.options.items(),self._get_rectangle_list(self.options.keys()))
        for (line,color),rectangle in line_color_rectangle:
            rectangle.draw_on_context(context)
            context.set_source_rgb(*color)
            context.fill_preserve()
            context.set_source_rgb(0,0,0)
            context.stroke()
            context.move_to(rectangle.start.x + rectangle.width + self.padding,
                      math.floor(rectangle.start.y + rectangle.height * .9))
            context.show_text(line)
        context.restore()


def main() -> int:
    root = Root()
    main_window = MainWindow(title="Guide")
    main_window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    root.set_main_window(main_window)

    root.set_child(BetterSelector(20))

    main_window.start_main()

    return 0

if __name__ == '__main__':
    main()
