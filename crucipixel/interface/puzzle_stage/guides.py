'''
Created on May 19, 2015

@author: giovanni
'''
import random
from enum import Enum
from typing import Tuple, List

import cairo
import math

from gi.repository import Gtk
from gi.repository import Gdk

from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.root import Root, MainWindow
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.support import rgb_to_gtk

class GuideStatus(Enum):

    DONE = 0
    WRONG = 1
    DEFAULT = 2

class GuideCell:
    
    def __init__(self, coordinates: Tuple[int, int],
                 cell: Rectangle, text: str, wide_cell: Rectangle=None):
        """

        :param coordinates: (line, pos)
        :param cell:
        :param text:
        :param wide_cell:
        :return:
        """
        self.cell = cell
        self.coordinates = coordinates
        self.text = text
        self.wide_cell = wide_cell

class GuideElement:
    
    def __init__(self, coordinates:"(line,pos)",
                 value: int,
                 done: bool=False,
                 wrong: bool=False,
                 cancelled: bool=False,
                 cell: Rectangle=None,
                 wide_cell: Rectangle=None):
        self.coordinates = coordinates
        self.value = value
        self.done = done
        self.wrong = wrong
        self.cancelled = cancelled 
        self.cell = cell
        self.wide_cell = wide_cell

    @property
    def text(self):
        return str(self.value)


class Orientation(Enum):

    VERTICAL = 0
    HORIZONTAL = 1


_color_map = {
    "normal": rgb_to_gtk(0, 0, 0),
    "done": rgb_to_gtk(46,139,87),
    "wrong": rgb_to_gtk(178,34,34),
    "cancelled": rgb_to_gtk(139,134,130)
}

class _GuideElement:

    def __init__(self, label: str, position: Point=Point(0, 0)):
        self.label = label
        self.position = position
        self.is_wrong = False
        self.is_done = False
        self.is_cancelled = False
        self.width = 0
        self.height = 0

    @property
    def color(self) -> Tuple[int, int, int]:
        if self.is_wrong:
            return _color_map["wrong"]
        elif self.is_done:
            return _color_map["done"]
        elif self.is_cancelled:
            return _color_map["cancelled"]
        else:
            return _color_map["normal"]



class _GuideLine(Widget):

    def __init__(self, elements: List[int],
                 orientation: Orientation, line_thickness: int,
                 font_size: int, max_size: int = None,
                 element_distance: int=10, line_distance: int=1.8,
                 **kwargs):
        super().__init__(**kwargs)

        if not elements:
            elements = [0]
        self._elements = [_GuideElement(str(e)) for e in elements]
        self.orientation = orientation
        self.line_thickness = line_thickness
        self.font_size = font_size
        self.shape = None
        self.max_size = max_size
        self.element_distance = element_distance
        self.line_distance = line_distance
        self.mouse_was_down = False

        self.line_extension = 0
        self._selected_cell = None

    def set_done(self):
        for e in self._elements:
            e.is_done = True
            e.is_wrong = False

    def set_wrong(self):
        for e in self._elements:
            e.is_wrong = True
            e.is_done = False

    def set_default(self):
        for e in self._elements:
            e.is_wrong = False
            e.is_done = False

    def set_cancelled(self, is_it: bool, index: int):
        self._elements[index].is_cancelled = is_it

    def toggle_cancelled(self, index: int):
        e = self._elements[index]
        e.is_cancelled = not e.is_cancelled

    def set_shape_from_context(self, context: cairo.Context):

        widths_heights = []

        done = False

        while not done:
            max_width = 0
            max_height = 0
            context.set_font_size(self.font_size)

            for e in reversed(self._elements):
                xb, yb, w, h, xa, ya = context.text_extents(e.label)
                widths_heights.append((xa, h))
                e.width = xa
                e.height = h
                max_width = max(max_width, xa)
                max_height = max(max_height, h)


            # adjust font size in case it's too big
            if self.max_size is None:
                done = True
            else:
                if self.orientation == Orientation.HORIZONTAL:
                    reference = max_height
                else:
                    reference = max_width
                if reference + 2 * self.line_distance <= self.max_size:
                    done = True
                else:
                    self.font_size -= 1

        positions = []
        width = self.element_distance
        height = self.element_distance

        def get_padding(actual_size):
            if self.max_size is not None:
                return (self.max_size - actual_size) / 2
            else:
                return self.line_distance

        if self.orientation == Orientation.HORIZONTAL:
            def handle_extents(e: _GuideElement):
                nonlocal width, height, positions, max_height
                width += e.width
                e.position = (-width,
                              max_height + get_padding(max_height))
                width += self.element_distance
        else:
            def handle_extents(e: _GuideElement):
                nonlocal width, height, positions, max_width
                e.position = (get_padding(e.width),
                              -height)
                height += e.height + self.element_distance

        # for w, h in widths_heights:
        #     handle_extents(w, h)

        for element in reversed(self._elements):
            handle_extents(element)

        if self.orientation == Orientation.HORIZONTAL:
            height = max_height + get_padding(max_height) * 2
            width = width - self.element_distance + self.line_distance
            base_point = Point(-width, 0)
        else:
            width = max_width + get_padding(max_width) * 2
            height = height - self.element_distance + self.line_distance
            base_point = Point(0, -height)

        self.shape = Rectangle(base_point, width, height)
        # for e, p in zip(self._elements, reversed(positions)):
        #     e.position = p

    def on_draw(self, widget: Widget, context: cairo.Context):

        self.set_shape_from_context(context)
        shape = self.shape

        context.set_line_width(self.line_thickness)
        if self.orientation == Orientation.HORIZONTAL:
            context.move_to(shape.start.x - self.line_extension, shape.start.y)
            context.line_to(shape.start.x + shape.width, shape.start.y)
        else:
            context.move_to(shape.start.x, shape.start.y - self.line_extension)
            context.line_to(shape.start.x, shape.start.y + shape.height)
        context.stroke()

        for element in self._elements:
            context.move_to(*element.position)
            context.set_source_rgb(*element.color)
            context.show_text(element.label)

    def get_cell(self, p: Point):
        delta = self.line_distance
        for index, element in enumerate(self._elements):
            if Rectangle(Point(*element.position) + Point(-delta, delta),
                         element.width + 2 * delta,
                         -element.height - 2 * delta).is_point_in(p):
                return index
        return None

    def on_mouse_down(self, widget: Widget, event: MouseEvent):
        self._selected_cell = self.get_cell(event)

    def on_mouse_up(self, widget: Widget, event: MouseEvent):
        if self._selected_cell is not None and \
                        self._selected_cell == self.get_cell(event):
            self.toggle_cancelled(self._selected_cell)
            self.invalidate()
        self._selected_cell = None

    def is_point_in(self, p: Point, category=MouseEvent.UNKNOWN):
        if self.shape is None:
            return False
        elif (category == MouseEvent.MOUSE_UP and self.mouse_was_down) \
                or self.shape.is_point_in(p):
            return True
        else:
            return False


class BetterGuide(UncheckedContainer):

    THICK_LINE = 2.5
    NORMAL_LINE = 1

    def __init__(self, elements: List[List[int]],
                 orientation: Orientation,
                 cell_size,
                 preferred_font_size: int = 12,
                 **kwargs):

        super().__init__(**kwargs)

        self._orientation = orientation
        self.preferred_font_size = preferred_font_size

        if orientation == Orientation.HORIZONTAL:
            orientation = Orientation.VERTICAL
        else:
            orientation = Orientation.HORIZONTAL

        self._lines = [
            _GuideLine(elements[i], orientation,
                       self.NORMAL_LINE if i % 5 != 0 else self.THICK_LINE,
                       self.preferred_font_size,
                       cell_size)
            for i in range(len(elements))
        ]

        for line in self._lines:
            self.add(line)


        def activate_status(status_line: List[Tuple[str, int]]):
            for line in self._lines:
                line.set_done(False)
                line.set_wrong(False)
            for (status, line) in status_line:
                change_status(line, status, True)
            self.invalidate()

        if self._orientation == Orientation.HORIZONTAL:
            self.register_signal("activate-hor-status", activate_status)
        else:
            self.register_signal("activate-ver-status", activate_status)

    def change_status(self, index: int, status: GuideStatus):
        if status == GuideStatus.WRONG:
            self._lines[index].set_wrong()
        elif status == GuideStatus.DONE:
            self._lines[index].set_done()
        else:
            self._lines[index].set_default()

    def on_draw(self, widget: Widget, context: cairo.Context):

        max_height = 0
        max_width = 0
        for line in self._lines:
            line.set_shape_from_context(context)
            max_height = max(max_height, line.shape.height)
            max_width = max(max_width, line.shape.width)


        offset = 0
        if self._orientation == Orientation.HORIZONTAL:
            def handle_line(line: _GuideLine):
                nonlocal offset
                line.line_extension = max_height - line.shape.height
                line.set_translate(offset, 0)
                offset += line.shape.width
        else:
            def handle_line(line: _GuideLine):
                nonlocal offset
                line.line_extension = max_width - line.shape.width
                line.set_translate(0, offset)
                offset += line.shape.height

        for line in self._lines:
            handle_line(line)

        super().on_draw(self, context)

        context.set_line_width(self.THICK_LINE)
        if self._orientation == Orientation.HORIZONTAL:
            context.move_to(offset, 0)
            context.line_to(offset, -max_height)
        else:
            context.move_to(0, offset)
            context.line_to(-max_width, offset)
        context.stroke()


class Guides(Widget):
    VERTICAL = 0
    HORIZONTAL = 1

    @staticmethod
    def _elements_from_list(elements):
        new_elements = []
        for line_index,line in enumerate(elements):
            new_line = []
            for position,e in enumerate(line):
                new_e = GuideElement(coordinates=(line_index,position),
                                     value=e)
                new_line.append(new_e)
            new_elements.append(new_line)
        return new_elements

    def __init__(self, elements: List[List[int]],
                 start:"Point", size: int, orientation=HORIZONTAL):
        super().__init__()
        self.translate(start.x, start.y)
        self.orientation = orientation
        self.elements = Guides._elements_from_list([list(e) for e in elements])
        self.cell_size = size
        self.line_length = 50
        self.width=self.line_length
        self.font_size = 13
        self._number_height = None
        self._number_width = None
        self._cell_list_to_update = True
        self._cell_list = []
        def change_status(line,status,value):
            if status == "wrong":
                for e in self.elements[line]:
                    e.wrong = value
            elif status == "done":
                for e in self.elements[line]:
                    e.done = value
        def activate_status(status_line:"[(status,line)]"):
            for line in self.elements:
                for e in line:
                    e.wrong = False
                    e.done = False
            for (status,line) in status_line:
                change_status(line,status,True)
            self.invalidate()
        if self.orientation == Guides.HORIZONTAL:
            self.register_signal("activate-hor-status", activate_status)
        else:
            self.register_signal("activate-ver-status", activate_status)

        self._update_clip()
        self.color_map = {
            "done" : rgb_to_gtk(46,139,87),
            "wrong" : rgb_to_gtk(178,34,34),
            "cancelled" : rgb_to_gtk(139,134,130)
            }

    def _update_clip(self):
        if self.orientation == Guides.HORIZONTAL:
            self.height = self.line_length
            # self.clip_rectangle = Rectangle(Point(0,-.5), self.cell_size * len(self.elements) + 2, -self.height)
        else:
            self.width = self.line_length
            # self.clip_rectangle = Rectangle(Point(-.5,0),-self.width,self.cell_size * len(self.elements) + 2)
        self.clip_rectangle = None

        
    def _update_cell_list(self):
        """Should be called only after on_draw has been called at least once"""
        self._cell_list = []
        for (line_index,element_list) in enumerate(self.elements): 
            line = self._line_coordinates(line_index)
            if self.orientation == Guides.HORIZONTAL:
                next_x = line[0].x - self.font_size//2
                next_y = line[0].y - (2*self.font_size)//3
            elif self.orientation == Guides.VERTICAL:
                next_x = line[0].x - self.font_size//2
                next_y = line[0].y - self.font_size//2
            total_length = 0
            #self.line_length = max_numbers * (self._number_height + self.font_size // 2) + 5
            for element in reversed(element_list):
                text = str(element.value)
                if self.orientation == Guides.HORIZONTAL:
                    width = self._number_width * len(text)
                    height = self._number_height
                    rectangle = Rectangle(Point(next_x-width,next_y),
                                          width,
                                          -height)
                    wide_rectangle = Rectangle(Point(line[0].x,next_y),
                                               -self.cell_size,
                                               -height)
                    next_y = next_y - height - self.font_size//2
                    total_length += height + self.font_size // 2
                elif self.orientation == Guides.VERTICAL:
                    width = self._number_width * (len(text) + 1)
                    height = self._number_height
                    rectangle = Rectangle(Point(next_x - width,next_y),
                                          width,
                                          -height)
                    wide_rectangle = Rectangle(Point(next_x - width,line[0].y),
                                               width,
                                               -self.cell_size)
                    next_x -= width + self.font_size//2
                    total_length += width + self.font_size // 2
                element.cell = rectangle
                element.wide_cell = wide_rectangle
            self.line_length = max(total_length + 5, self.line_length)
        self._update_clip()

    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        if self.elements:
            for line in self.elements:
                for e in line:
                    if e.wide_cell.is_point_in(p):
                        return True
        return False

    def on_mouse_down(self, w, e):
        p = Point(e.x,e.y)
        for line in self.elements:
            for e in line:
                if e.wide_cell.is_point_in(p):
                    e.cancelled = not e.cancelled
                    self.invalidate()
                    return True

    def _line_coordinates(self,line_index):
        if self.orientation == Guides.HORIZONTAL:
            delta_x = (line_index + 1) * self.cell_size
            delta_y = -self.line_length
            return [Point(delta_x,0),Point(delta_x,delta_y)]
        elif self.orientation == Guides.VERTICAL:
            delta_x = -self.line_length
            delta_y = (line_index +1) * self.cell_size
            return [Point(0,delta_y),Point(delta_x,delta_y)]
        else:
            raise ValueError("Invalid orientation: {}".format(str(self.orientation)))
    

    def _draw_element(self, context, e):
        context.save()
        if e.done:
            context.set_source_rgb(*self.color_map["done"])
        elif e.wrong:
            context.set_source_rgb(*self.color_map["wrong"])
        elif e.cancelled:
            context.set_source_rgb(*self.color_map["cancelled"])
        context.move_to(e.cell.start.x, e.cell.start.y)
        context.show_text(e.text)
        context.restore()

    def on_draw(self, widget, context):
        def draw_line(line):
            context.move_to(line[0].x,line[0].y)
            context.line_to(line[1].x,line[1].y)
            context.stroke()
        context.save()
        
        ext = context.text_extents("0")
        self._number_width = int(ext[0] + ext[2])
        self._number_height = -int(ext[1]) 
        if self._cell_list_to_update:
            # max_numbers = max([len(line) for line in self.elements])
            # self.line_length = max_numbers * (self._number_height + self.font_size // 2) + 5
            self._update_cell_list()
            self._cell_list_to_update = False
        
        for (i,e) in enumerate(self.elements):
            line = self._line_coordinates(i)
            if (i+1) % 5 == 0:
                context.set_line_width(2.5)
            else:
                context.set_line_width(1)
            draw_line(line)

        context.set_line_width(1)
        context.set_font_size(self.font_size)
        for line in self.elements:
            for e in line:
                self._draw_element(context, e)

        context.restore()

class _LineTestContainer(UncheckedContainer):

    def __init__(self):
        super().__init__()
        self.guide_line = _GuideLine([1, 2, 3, 15, 3],
                                     Orientation.HORIZONTAL,
                                     line_thickness=1,
                                     font_size=13,
                                     max_size=20,
                                     element_distance=10,
                                     line_distance=2)
        self.add(self.guide_line)

    def on_draw(self, widget: Widget, context: cairo.Context):
        self.guide_line.set_shape_from_context(context)
        shape = self.guide_line.shape
        self.guide_line.set_translate(shape.width + 10, shape.height + 10)

        context.save()
        context.set_source_rgb(1, 1, 1)
        if self.guide_line.orientation == Orientation.HORIZONTAL:
            context.rectangle(10, shape.height + 10, shape.width, 20)
        else:
            context.rectangle(shape.width + 10, 10, 20, shape.height)
        context.fill()
        context.restore()

        super().on_draw(widget, context)


def main() -> int:
    # root = Root()
    # main_window = MainWindow(title="Guide")
    # main_window.add(root)
    #
    # cruci_scheme = parse_file_name("brachiosauri.json")
    # print(cruci_scheme.cols)
    #
    # # guide = Guides(cruci_scheme.cols, Point(100, 100), 20, orientation=Guides.HORIZONTAL)
    # guide = Guides(cruci_scheme.rows, Point(100, 100), 20, orientation=Guides.VERTICAL)
    # root.set_child(guide)
    #
    # main_window.start_main()

    root = Root()
    main_window = MainWindow(title="Guide")
    main_window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    root.set_main_window(main_window)
    # container = _LineTestContainer()
    # container.translate(.5,.5)
    #
    # root.set_child(container)

    guides = BetterGuide([[], [1, 2], [15, 16, 3]], Orientation.HORIZONTAL, 20)

    guides.translate(100.5, 100.5)

    root.set_child(guides)

    main_window.start_main()



if __name__ == '__main__':
    main()
