import math
from typing import List, Tuple

from gi.overrides import GLib

from lightwidgets import geometry
from lightwidgets.events import MouseEvent, MouseButton
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget


class Arrow(Widget):

    UP= 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def __init__(self, base_size: int=50, height: int=20,
                       direction: int=UP, colour: Tuple[int,int,int]=(0,0,0)):

        super().__init__()

        self.base_size = base_size
        self.height = height
        self.direction = direction
        self.colour = colour

        self.action = lambda: None

    @property
    def _vertexes(self) -> Tuple[Point, Point, Point]:
        w = self.base_size
        h = self.height

        return Point(-w/2, h/2), Point(0, -h/2), Point(w/2, h/2)

    def on_click(self, widget: Widget, button: MouseButton):
        self.action()

    def on_draw(self, widget: Widget, c):

        super().on_draw(widget, c)

        c.save()

        c.set_source_rgb(*self.colour)

        w = self.base_size
        h = self.height

        c.rotate(self.direction * (math.pi / 2))

        c.move_to(-w/2, h/2)
        c.line_to(0, -h/2)
        c.line_to(w/2, h/2)
        c.fill()

        c.restore()

    def is_point_in(self,p: Point,category=MouseEvent.UNKNOWN):
        a, b, c = self._vertexes
        return geometry.is_point_inside_triangle(p, a, b, c)


class KeepPressingArrow(Arrow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__is_moving = False
        self.__skip = 0

    def on_click(self, widget: Widget, button: MouseButton):
        pass

    def on_mouse_down(self, widget: "Widget", event: MouseEvent):
        self.__is_moving = True
        self.__skip = 4
        def timeout_function() -> bool:
            if self.__skip > 0:
                self.__skip -= 1
            else:
                super(KeepPressingArrow, self).on_click(widget, event)
            return self.__is_moving
        super().on_click(widget, event)
        GLib.timeout_add(100, timeout_function)
        super().on_mouse_down(widget, event)

    def on_mouse_up(self, widget: "Widget", event: MouseEvent):
        self.__is_moving = False
        super().on_mouse_up(widget, event)


def main() -> int:
    mainWindow = MainWindow(title="Prova")
    root = Root()
    mainWindow.add(root)
    arr = Arrow(direction=Arrow.RIGHT)
    cont = UncheckedContainer()
    cont.add(arr)

    arr.translate(100,100)
    root.set_child(cont)

    mainWindow.start_main()

if __name__ == '__main__':
    main()
