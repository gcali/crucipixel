import math
from typing import List, Tuple

from lightwidgets import geometry
from lightwidgets.events import MouseEvent
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

    @property
    def _vertexes(self) -> Tuple[Point, Point, Point]:
        w = self.base_size
        h = self.height

        return Point(-w/2, h/2), Point(0, -h/2), Point(w/2, h/2)

    def on_mouse_down(self,w,e):
        super().on_mouse_down(w, e)
        print("I'm a mouse down!", self.is_point_in(e))
        return True

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
