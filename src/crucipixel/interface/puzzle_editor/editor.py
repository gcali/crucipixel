from typing import Callable

from crucipixel.interface.puzzle_editor.buttons import EditorButtons
from crucipixel.interface.puzzle_stage.grid import CrucipixelGrid
from crucipixel.logic import core
from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.layout import SetAlignment, Alignment


class EditorScreen(UncheckedContainer):

    def __init__(self, core_crucipixel: core.CrucipixelEditor):
        super().__init__()

        self.__buttons = EditorButtons()
        self.__grid = CrucipixelGrid(core_crucipixel)
        self.__grid.translate(100, 100)
        self.add(self.__grid)
        self.add(SetAlignment(
            SetAlignment(
                self.__buttons, Alignment.RIGHT,
            ),
            Alignment.TOP
        ))

        self.__mouse_down = False
        self.__click_point = Point(0, 0)
        self.__translate_vector = Point(0, 0)

    def set_quit_button_action(self, action: Callable[[], None]):
        self.__buttons.set_quit_action(action)

    def on_mouse_down(self, widget, event: MouseEvent):
        handled = False
        if 'ctrl' not in event.modifiers:
            handled = super().on_mouse_down(widget, event)
        if not handled:
            self.__mouse_down = True
            self.__click_point = Point(event.x, event.y)
            self.__translate_vector = Point(
                self.__grid.fromWidgetCoords.transform_point(0, 0)
            )

    def on_mouse_move(self, w, e):
        if self.__mouse_down:
            delta_x = int(e.x - self.__click_point.x)
            delta_y = int(e.y - self.__click_point.y)
            self.__grid.set_translate(self.__translate_vector.x + delta_x,
                                      self.__translate_vector.y + delta_y)
            self.invalidate()
        super().on_mouse_move(w, e)

    def on_mouse_up(self, widget, event):
        if self.__mouse_down:
            self.__mouse_down = False
        super().on_mouse_up(widget, event)
