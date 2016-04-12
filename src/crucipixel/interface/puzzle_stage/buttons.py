from typing import Callable, Tuple, List, Iterable

import cairo

from crucipixel.interface import global_constants
from lightwidgets.geometry import Rectangle, Point
from lightwidgets.stock_widgets.buttons import Button, BetterButton, \
    click_left_button_wrapper
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRoundedRectangle
from lightwidgets.stock_widgets.layout import SetAlignment, Alignment
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget


class OrderedButtons(UncheckedContainer):

    def __init__(self,
                 button_names: Iterable[Iterable[str]],
                 background_color: Tuple[int, int, int] =\
                     global_constants.background,
                 **kwargs):
        super().__init__(**kwargs)
        self._padding = 10
        self._buttons = [
            [BetterButton(name, 20, self._padding, origin=BetterButton.LEFT)
             for name in series]
            for series in button_names
        ]

        self._active = [
            0 for _ in self._buttons
        ]

        for series, active in zip(self._buttons, self._active):
            for b in series:
                self.add(b)
                b.visible = False
            series[active].visible = True

        self.background_color = background_color

    def _iter_over_visible(self) -> Iterable[BetterButton]:
        for series, active in zip(self._buttons, self._active):
            yield series[active]

    def set_action(self, index: int, series_position: int,
                   action: Callable[[], None]):
        self._buttons[index][series_position].on_click_action = action

    def next_visible(self, index: int):
        old = self._active[index]
        new = (old + 1) % len(self._buttons[index])
        self._buttons[index][old].visible = False
        self._buttons[index][new].visible = True
        self._active[index] = new
        self.invalidate()

    def layout(self, context: cairo.Context):
        super().layout(context)

        height = 0
        width = self._padding
        for button in self._iter_over_visible():
            button.set_translate(width, self._padding)
            height = max(height, button.shape.height)
            width += button.shape.width + self._padding
        for button in self._iter_over_visible():
            button.min_height = height
            button.layout(context)

        height += 2 * self._padding

        self.shape = DrawableRoundedRectangle(
            Point(0, 0),
            width,
            height
        )

    def on_draw(self, widget: Widget, context: cairo.Context):

        context.save()
        context.set_source_rgb(*self.background_color)
        self.shape.draw_on_context(context)
        context.fill_preserve()
        context.set_source_rgb(0,0,0)
        context.set_line_width(1)
        context.stroke()

        context.restore()

        super().on_draw(widget, context)


class GridButtons(UncheckedContainer):

    def __init__(self, background_color=global_constants.background,
                 **kwargs):
        super().__init__(**kwargs)
        self._padding = 10
        self._save_button = BetterButton("Save", 20, self._padding,
                                         origin=BetterButton.RIGHT)
        self._quit_button = BetterButton("Quit", 20, self._padding,
                                         origin=BetterButton.RIGHT)
        self._load_button = BetterButton("Load", 20, self._padding,
                                         origin=BetterButton.RIGHT)
        self._undo_edit_button = BetterButton("Undo", 20, self._padding,
                                              origin=BetterButton.RIGHT)

        self._undo_action = None
        self._edit_action = None

        self.is_undo = True

        self._buttons = [
            self._quit_button,
            self._save_button,
            self._load_button,
            self._undo_edit_button
        ]

        self.background_color = background_color

        for b in self._buttons:
            self.add(b)

        self.shape = None

    def set_undo(self):
        self.is_undo = True
        self._undo_edit_button.label = "Undo"
        self._undo_edit_button.on_click_action = self._undo_action

    def set_edit(self):
        self.is_undo = False
        self._undo_edit_button.label = "Edit"
        self._undo_edit_button.on_click_action = self._edit_action

    @property
    def on_save_action(self) -> Callable[[], None]:
        return self._save_button.on_click_action

    @on_save_action.setter
    def on_save_action(self, value) -> None:
        self._save_button.on_click_action = value

    @property
    def on_undo_action(self) -> Callable[[], None]:
        return self._undo_action

    @on_undo_action.setter
    def on_undo_action(self, value) -> None:
        self._undo_action = value
        if self.is_undo:
            self._undo_edit_button.on_click_action = value

    @property
    def on_edit_action(self) -> Callable[[], None]:
        return self._edit_action

    @on_edit_action.setter
    def on_edit_action(self, value) -> None:
        self._edit_action = value
        if not self.is_undo:
            self._undo_edit_button.on_click_action = value

    @property
    def on_load_action(self) -> Callable[[], None]:
        return self._load_button.on_click_action

    @on_load_action.setter
    def on_load_action(self, value) -> None:
        self._load_button.on_click_action = value

    @property
    def on_quit_action(self) -> Callable[[], None]:
        return self._quit_button.on_click_action

    @on_quit_action.setter
    def on_quit_action(self, value) -> None:
        self._quit_button.on_click_action = value

    def _button_translation(self, button: BetterButton) -> int:
        return button.shape.width + self._padding

    def on_mouse_down(self, widget, event):
        self._mouse_down = True
        super().on_mouse_down(widget, event)
        return True

    def on_mouse_up(self, widget, event):
        self._mouse_down = False
        return super().on_mouse_up(widget, event)

    def on_mouse_move(self, w, e):
        super().on_mouse_move(w, e)
        return False

    def get_width_height(self, context: cairo.Context) -> Tuple[int, int]:
        height = 0
        width = 0

        for button in self._buttons:
            button.set_shape_from_context(context)
            height = max(height, button.shape.height)
            width += self._button_translation(button)
        return width, height

    def on_draw(self, widget: Widget, context: cairo.Context):

        x_offset = self.father.container_size[0] - self._padding
        y_offset = self._padding

        width, height = self.get_width_height(context)

        self.shape = DrawableRoundedRectangle(
            Point(x_offset - width, 0),
            width + self._padding,
            height + 2 * self._padding
        )

        context.save()

        context.set_source_rgb(*self.background_color)
        self.shape.draw_on_context(context)
        context.fill_preserve()
        context.set_source_rgb(0,0,0)
        context.set_line_width(1)
        context.stroke()

        context.restore()

        context.translate(x_offset, y_offset)

        for button in self._buttons:
            button.shape.height = height
            button.set_translate(x_offset, y_offset)
            translate_of = -self._button_translation(button)
            x_offset += translate_of
            button.on_draw(self, context)
            context.translate(translate_of, 0)

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

    # grid_buttons.on_save_action = click_left_button_wrapper(lambda: print("I'm saving!"))
    # grid_buttons.on_load_action = click_left_button_wrapper(lambda: print("I'm loading!"))
    # grid_buttons.on_quit_action = click_left_button_wrapper(lambda: print("I'm quitting!"))

    root.set_child(SetAlignment(SetAlignment(grid_buttons, Alignment.RIGHT), Alignment.VERTICAL_CENTER))

    main_window.start_main()

if __name__ == '__main__':
    main()
