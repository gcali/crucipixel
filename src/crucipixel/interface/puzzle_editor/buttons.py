from typing import Callable

from lightwidgets.stock_widgets.buttons import OrderedButtons, \
    click_left_button_wrapper
from lightwidgets.stock_widgets.root import MainWindow, Root


class EditorButtons(OrderedButtons):

    def __init__(self):
        super().__init__([
            ["Undo", "Edit"],
            ["Save"],
            ["Quit"]
        ])

    def set_undo(self):
        self.set_visible(0, 0)

    def set_edit(self):
        self.set_visible(0, 1)

    def set_undo_action(self, action: Callable[[], None]):
        self.set_action(0, 0, click_left_button_wrapper(action))

    def set_edit_action(self, action: Callable[[], None]):
        self.set_action(0, 1, click_left_button_wrapper(action))

    def set_save_action(self, action: Callable[[], None]):
        self.set_action(1, 0, click_left_button_wrapper(action))

    def set_quit_action(self, action: Callable[[], None]):
        self.set_action(2, 0, click_left_button_wrapper(action))

    def set_save_clickable(self, clickable: bool):
        self.set_clickable(1, 0, clickable)


def main():

    main_window = MainWindow("OrderedButtons test")
    root = Root(500, 500)
    ordered_buttons = EditorButtons()
    ordered_buttons.translate(100, 100)

    def wrap(action):
        def inner():
            action()
            ordered_buttons.invalidate()
        return inner

    ordered_buttons.set_undo_action(wrap(lambda: ordered_buttons.set_edit()))
    ordered_buttons.set_edit_action(wrap(lambda: ordered_buttons.set_undo()))

    ordered_buttons.set_quit_action(wrap(lambda: ordered_buttons.set_save_clickable(True)))
    ordered_buttons.set_save_action(wrap(lambda: ordered_buttons.set_save_clickable(False)))
    root.set_child(ordered_buttons)
    root.set_main_window(main_window)

    main_window.start_main()

if __name__ == '__main__':
    main()
