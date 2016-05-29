from typing import Callable

from crucipixel.interface.puzzle_editor.buttons import EditorButtons
from crucipixel.interface.puzzle_stage.grid import CrucipixelGrid
from crucipixel.interface.puzzle_stage.selector import BetterSelector
from crucipixel.logic import core
from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.layout import SetAlignment, Alignment
from lightwidgets.stock_widgets.overlay import ButtonedTextOverlay


"""
Salve,

Sono Giovanni Calì, uno studente del corso di laurea di Informatica.

A Gennaio ho sostenuto l'esame di Esperienze di Programmazione
"""

class EditorScreen(UncheckedContainer):

    def __init__(self, core_crucipixel: core.CrucipixelEditor):
        super().__init__()

        self.__selector = BetterSelector()
        self.__buttons = EditorButtons()
        self.__grid = CrucipixelGrid(core_crucipixel)
        self.__grid.translate(100, 100)
        self.__overlay = ButtonedTextOverlay("File already existing; overwrite?")

        def back_action():
            self.__overlay.visible = False

        def ok_action():
            core_crucipixel.save(force=True)
            self.__overlay.visible = False

        self.__overlay.set_back_action(back_action)
        self.__overlay.set_ok_action(ok_action)
        self.__overlay.visible = False
        self.add(self.__grid)
        self.add(self.__overlay, -2)
        self.add(SetAlignment(
            SetAlignment(
                self.__buttons, Alignment.RIGHT,
            ),
            Alignment.TOP
        ), -1)

        self.add(SetAlignment(
            SetAlignment(
                self.__selector, Alignment.LEFT,
            ),
            Alignment.TOP
        ), -1)

        self.__buttons.set_save_clickable(False)

        def save_action():
            try:
                core_crucipixel.save()
            except FileExistsError:
                self.__overlay.visible = True
        self.__buttons.set_save_action(save_action)
        self.__buttons.set_undo_action(lambda: self.__grid.undo())

        def create_lambda(index):
            return lambda button: self.__grid.handle_selector(index, button)

        for i in range(3):
            self.__selector.set_click_action(i, create_lambda(i))

        def full_scheme_callback(is_full: bool) -> bool:
            self.__buttons.set_save_clickable(is_full)
            return False

        core_crucipixel.on_won_change_callbacks_list.append(full_scheme_callback)

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

    def on_mouse_move(self, widget, event):
        if self.__mouse_down:
            delta_x = int(event.x - self.__click_point.x)
            delta_y = int(event.y - self.__click_point.y)
            self.__grid.set_translate(self.__translate_vector.x + delta_x,
                                      self.__translate_vector.y + delta_y)
            self.invalidate()
        super().on_mouse_move(widget, event)

    def on_mouse_up(self, widget, event):
        if self.__mouse_down:
            self.__mouse_down = False
        super().on_mouse_up(widget, event)
