from typing import Callable

from app.interface import global_constants
from lightwidgets.stock_widgets.buttons import click_left_button_wrapper, \
    OrderedButtons
from lightwidgets.stock_widgets.layout import SetAlignment, Alignment
from lightwidgets.stock_widgets.root import MainWindow, Root


class GridButtons(OrderedButtons):

    def __init__(self, background_color=global_constants.background,
                 **kwargs):
        super().__init__([
            ["Undo", "Edit"],
            ["Load"],
            ["Save"],
            ["Quit"]
        ], background_color)

    def set_undo(self):
        self.set_visible(0, 0)

    def set_edit(self):
        self.set_visible(0, 1)

    @property
    def on_save_action(self) -> Callable[[], None]:
        return self.get_action(2, 0)

    @on_save_action.setter
    def on_save_action(self, value) -> None:
        self.set_action(2, 0, value)

    @property
    def on_undo_action(self) -> Callable[[], None]:
        self.get_action(0, 0)

    @on_undo_action.setter
    def on_undo_action(self, value) -> None:
        self.set_action(0, 0, value)

    @property
    def on_edit_action(self) -> Callable[[], None]:
        self.get_action(0, 1)

    @on_edit_action.setter
    def on_edit_action(self, value) -> None:
        self.set_action(0, 1, value)

    @property
    def on_load_action(self) -> Callable[[], None]:
        return self.get_action(1, 0)

    @on_load_action.setter
    def on_load_action(self, value) -> None:
        self.set_action(1, 0, value)

    @property
    def on_quit_action(self) -> Callable[[], None]:
        return self.get_action(3, 0)

    @on_quit_action.setter
    def on_quit_action(self, value) -> None:
        self.set_action(3, 0, value)


def main():
    main_window = MainWindow(title="Grid buttons")
    root = Root()
    root.set_main_window(main_window)
    root.set_min_size(100, 100)

    grid_buttons = OrderedButtons([["Save", "Edit"], ["Load"]])

    def action():
        grid_buttons.next_visible(0)
    grid_buttons.set_action(0, 0, click_left_button_wrapper(action))
    grid_buttons.set_action(0, 1, click_left_button_wrapper(action))

    root.set_child(SetAlignment(SetAlignment(grid_buttons, Alignment.RIGHT), Alignment.VERTICAL_CENTER))

    main_window.start_main()

if __name__ == '__main__':
    main()
