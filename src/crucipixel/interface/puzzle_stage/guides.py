'''
Created on May 19, 2015

@author: giovanni
'''
from typing import Tuple, List

from crucipixel.data.json_parser import parse_file_name
from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.stock_widgets.root import Root, MainWindow
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.support import rgb_to_gtk

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
        value= super().is_point_in(p,category)
        return value
    
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


def main() -> int:
    root = Root()
    main_window = MainWindow(title="Guide")
    main_window.add(root)

    cruci_scheme = parse_file_name("brachiosauri.json")
    print(cruci_scheme.cols)

    # guide = Guides(cruci_scheme.cols, Point(100, 100), 20, orientation=Guides.HORIZONTAL)
    guide = Guides(cruci_scheme.rows, Point(100, 100), 20, orientation=Guides.VERTICAL)
    root.set_child(guide)

    main_window.start_main()

if __name__ == '__main__':
    main()
