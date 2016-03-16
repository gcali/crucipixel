from crucipixel.interface import global_constants
from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Rectangle, Point
from lightwidgets.stock_widgets.arrow import Arrow
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget


class Navigator(UncheckedContainer):

    def __init__(self, side=40, protrusion=30):
        super().__init__()
        base_size = side
        height = protrusion
        colour = global_constants._start_selected
        arrow_up = Arrow(base_size, height, Arrow.UP, colour)
        arrow_down = Arrow(base_size, height, Arrow.DOWN, colour)
        arrow_left = Arrow(base_size, height, Arrow.LEFT, colour)
        arrow_right = Arrow(base_size, height, Arrow.RIGHT, colour)
        factor=6
        center = height + base_size/2 + (base_size/factor)
        distance = (base_size + height)/2 + (base_size/factor)

        arrow_up.translate(center, center - distance)
        arrow_left.translate(center - distance, center)
        arrow_right.translate(center + distance, center)
        arrow_down.translate(center, center + distance)

        self.background_rectangle = Rectangle(Point(0,0), center * 2, center * 2)

        self.add(arrow_up)
        self.add(arrow_down)
        self.add(arrow_left)
        self.add(arrow_right)

        self._should_pass_move = False

    def on_mouse_up(self, w, e):
        self._should_pass_move = False
        super().on_mouse_up(w, e)
        return False

    def on_mouse_enter(self) -> bool:
        print(self.mouse_is_down)
        if self.mouse_is_down:
            self._should_pass_move = True
        return super().on_mouse_enter()

    def on_mouse_exit(self) -> bool:
        self._should_pass_move = False
        return super().on_mouse_exit()

    def on_mouse_move(self, w, e):
        super().on_mouse_move(w, e)
        return not self._should_pass_move

    def on_mouse_down(self, w, e):
        super().on_mouse_down(w, e)
        return True

    @property
    def fromWidgetCoords(self):
        width = self.background_rectangle.width
        height = self.background_rectangle.height
        total_width, total_height = self.container_size
        transl_width, transl_height = self._fromScale.transform_point(width, height)
        self.set_translate(total_width - transl_width, total_height - transl_height)
        return super().fromWidgetCoords

    @property
    def width(self):
        return self.background_rectangle.width

    def on_draw(self,widget,context):

        start = self.background_rectangle.start
        width = self.background_rectangle.width
        height = self.background_rectangle.height

        context.save()
        context.rectangle(start.x,start.y,width,height)
        context.set_source_rgb(0,0,0)
        context.stroke_preserve()
        context.set_source_rgb(*global_constants._background)
        context.fill()
        context.restore()

        super().on_draw(widget,context)

    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        return self.background_rectangle.is_point_in(p)


def main() -> int:
    main_window = MainWindow(title="prova")
    root = Root()
    main_window.add(root)
    navigator = Navigator()
    navigator.scale(.5, .5)
    container = UncheckedContainer()
    container.add(navigator)
    root.set_child(container)

    main_window.start_main()

if __name__ == '__main__':
    main()
