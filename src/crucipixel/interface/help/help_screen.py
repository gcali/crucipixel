from typing import Tuple, List

import cairo

from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.buttons import BetterButton
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.text import TextArea
from lightwidgets.stock_widgets.widget import Widget

_help_text = ["Io sono un lunghissimo testo di aiuto. Che scopo ho nella "
              "vita? Principalmente quello di fare il testo di aiuto! Del "
              "resto sono pur sempre un testo di aiuto. Evviva i testi di "
              "aiuto!",
              "Io invece sono il suo cugino piccolo che comincia su un'altra "
              "riga e finisce proprio qua"]

_new_game_help = [
    "Choose a scheme to play by clicking on its row in the table; "
    "if an instance of that scheme has been saved it will be "
    "automatically loaded"
]

_game_loaded_help = [
    "Click (or click and drag) on the grid to select, clear or restore to "
    "default a cell; the three different actions are by default binded "
    "respectively to the left, right and middle click, but the bindings can "
    "be modified by clicking on the selector in the top left corner.",

    "The numbers on the guides can be clicked on to mark a group as "
    "completed; a filled line or column is automatically marked as either "
    "done or wrong.",

    "The current progress can be saved at any time by clicking on the 'Save' "
    "button; any old instance will be overwritten. The saved instance will be "
    "automatically loaded on a new game, or if the 'Load' button is pressed. "
    "Use the 'Undo' button to undo the last move, up to the start of the "
    "game.",

    "The view can be moved by dragging the mouse after having clicked on an "
    "empty section or after having clicked anywhere while pressing the 'Ctrl' "
    "modifier; if needed the zoom can be adjusted with the keys '+' and '-'.",

    "When a scheme is completed the view will be centered and the grid will "
    "be hidden to show the full figure; to return to the gaming view, click "
    "on 'Edit'."
]

# _help_text = [
#
# ]

class HelpSection(UncheckedContainer):

    def __init__(self, title: str, content: List[str]):
        super().__init__()
        self.__title = TextArea(["⊰{}⊱".format(title)], font_size=20, italic=True)
        self.__content = TextArea(content, font_size=15)

        self.add(self.__title)
        self.add(self.__content)

    def layout(self, context: cairo.Context):
        super().layout(context)

        padding = 20
        self.__content.set_translate(padding, self.__title.shape.height + padding/10)

        self.shape = DrawableRectangle(
            Point(0, 0),
            self.container_size[0],
            self.__title.shape.height + self.__content.shape.height + padding
        )


class HelpWindow(UncheckedContainer):

    def __init__(self):
        super().__init__()

        self.__title = TextArea(["Help"], font_size=30, bold=True)

        self.__sections = [
            HelpSection("New game", _new_game_help),
            HelpSection("In game", _game_loaded_help),
        ]
        self.__new_game = HelpSection("New game", _new_game_help)
        # self.__new_game_title = TextArea(["⊰New game⊱"], font_size=20, italic=True)
        # self.__new_game_help = TextArea(_new_game_help, font_size=12)

        self.add(self.__title)
        for s in self.__sections:
            self.add(s)
        # self.add(self.__new_game_title)
        # self.add(self.__new_game_help)

    def layout(self, context: cairo.Context):

        super().layout(context)

        padding = 20


        current_y = self.__title.shape.height + padding
        for s in self.__sections:
            s.set_translate(0, current_y)
            current_y += padding + s.shape.height

        self.shape = DrawableRectangle(Point(0, 0), self.__title.shape.width,
                                       current_y - padding)
        # self.__new_game_title.set_translate(0, current_y)
        # current_y += self.__new_game_title.shape.height + 10
        # self.__new_game_help.set_translate(10, current_y)

    @property
    def container_size(self) -> Tuple[int, int]:
        old_width, old_height = super().container_size
        return old_width - 20, old_height


class HelpScreen(UncheckedContainer):

    def __init__(self):
        super().__init__()
        self.__help_window = HelpWindow()
        self.__back_button = BetterButton("Back", origin=BetterButton.RIGHT)
        self.add(self.__help_window)
        self.add(self.__back_button, -1)

        self.__click_y = None
        self.__translation = 0

    def __get_translation(self, y: int) -> int:
        mini = min(0, self.father.container_size[1] -self.__help_window.shape.height)
        return max(min(self.__translation - self.__click_y + y, 0), mini)

    def is_point_in(self, p: "Point", category=MouseEvent.UNKNOWN):
        return True

    def on_mouse_up(self, widget: Widget, event: MouseEvent):
        super().on_mouse_up(widget, event)
        self.__translation = self.__get_translation(event.y)
        self.__click_y = None

    def on_mouse_down(self, widget: Widget, event: MouseEvent):
        super().on_mouse_down(widget, event)
        self.__click_y = event.y

    def on_mouse_move(self, widget, event):
        super().on_mouse_move(widget, event)
        if self.__click_y is not None:
            self.__help_window.set_translate(0, self.__get_translation(event.y))
            self.invalidate()

    @property
    def container_size(self) -> Tuple[int, int]:
        old_width, old_height = super().container_size
        return old_width - 20, old_height

    def layout(self, context: cairo.Context):
        super().layout(context)
        self.__back_button.set_translate(self.father.container_size[0] - 10, 10)

def main():

    win = MainWindow("Help test")
    root = Root(200, 200)

    root.set_main_window(win)
    root.set_child(HelpScreen())

    win.start_main()

if __name__ == '__main__':
    main()
