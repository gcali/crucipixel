"""
Created on May 19, 2015

@author: giovanni
"""

from typing import Tuple, Iterable, Callable

import cairo
from gi.repository import GLib

from crucipixel.data.crucipixel_instance import CrucipixelCellValue, MoveAtom
from crucipixel.data.json_parser import parse_file_name
from crucipixel.interface import global_constants
from crucipixel.interface.puzzle_stage.guides import Orientation, GuideStatus
from crucipixel.interface.puzzle_stage.navigator import Direction
from crucipixel.logic import core
from lightwidgets.events import MouseEvent, MouseButton, KeyboardEvent
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
from lightwidgets.stock_widgets.root import Root, MainWindow
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.support import DefaultDict, clamp, get_from_to_inclusive

class CrucipixelGrid(Widget):

    def __init__(self, crucipixel: core.Crucipixel,
                 cell_width: int=10, cell_height: int=10, **kwargs):
        super().__init__(**kwargs)

        self.crucipixel = crucipixel
        self.cell_width = cell_width
        self.cell_height = cell_height

        self.clip_rectangle = Rectangle(Point(-1, -1), self._total_width + 2, self._total_height + 2)

        self.highlight_color = global_constants.highlight

        self._cell_value_order = [
            CrucipixelCellValue.SELECTED,
            CrucipixelCellValue.EMPTY,
            CrucipixelCellValue.DEFAULT
        ]

        self.crucipixel_cell_value_to_color = {
            CrucipixelCellValue.EMPTY: global_constants.start_empty,
            CrucipixelCellValue.DEFAULT: global_constants.start_default,
            CrucipixelCellValue.SELECTED: global_constants.start_selected
        }

        self._mouse_button_to_crucipixel_cell_value = {
            MouseButton.LEFT: CrucipixelCellValue.SELECTED,
            MouseButton.RIGHT: CrucipixelCellValue.EMPTY,
            MouseButton.MIDDLE: CrucipixelCellValue.DEFAULT
        }

        self._keyboard_value_to_crucipixel_cell_value = {
            'space': CrucipixelCellValue.SELECTED,
            'enter': CrucipixelCellValue.EMPTY,
            'backspace': CrucipixelCellValue.DEFAULT,

            'z': CrucipixelCellValue.SELECTED,
            'x': CrucipixelCellValue.EMPTY,
            'c': CrucipixelCellValue.DEFAULT,

            'i': CrucipixelCellValue.SELECTED,
            'o': CrucipixelCellValue.EMPTY,
            'p': CrucipixelCellValue.DEFAULT,
        }

        self._keyboard_value_to_movement_directions = {
            'w': (Direction.UP,),
            'a': (Direction.LEFT,),
            's': (Direction.DOWN,),
            'd': (Direction.RIGHT,),

            'k': (Direction.UP,),
            'h': (Direction.LEFT,),
            'j': (Direction.DOWN,),
            'l': (Direction.RIGHT,),

            'y': (Direction.UP, Direction.LEFT),
            'u': (Direction.UP, Direction.RIGHT),
            'b': (Direction.DOWN, Direction.LEFT),
            'n': (Direction.DOWN, Direction.RIGHT)
        }

        self._key_pressed = set()

        self._should_highlight = False
        self._highlight_row = None
        self._highlight_col = None

        self.victory_screen = False

        self._selection_value = None
        self._selection_start_point = None
        self._selection_end_point = None
        self._selection_rectangle = None
        self.is_destroyed = False

        def default_guide_update(orientation: Orientation, line: int,
                                 status: GuideStatus):
            pass

        self.on_guide_update = default_guide_update

        def timeout_function() -> bool:
            self.invalidate()
            return not self.is_destroyed
        GLib.timeout_add(33, timeout_function)

    def save(self):
        self.crucipixel.save()

    def load(self):
        self.crucipixel.load()
        self.refresh_guides()

    def undo(self):
        rows, cols = set(), set()
        for atom in self.crucipixel.undo_move():
            rows.add(atom.row)
            cols.add(atom.col)
        for row in rows:
            self._handle_guide_line_check(Orientation.HORIZONTAL, row)
        for col in cols:
            self._handle_guide_line_check(Orientation.VERTICAL, col)


    def handle_selector(self, index: int, button: MouseButton):
        self._mouse_button_to_crucipixel_cell_value[button] = self._cell_value_order[index]

    def refresh_guides(self):
        for row in range(self.number_of_rows):
            self._handle_guide_line_check(Orientation.HORIZONTAL, row)
        for col in range(self.number_of_cols):
            self._handle_guide_line_check(Orientation.VERTICAL, col)

    @property
    def _total_height(self) -> int:
        return self.number_of_rows * self.cell_height

    @property
    def _total_width(self) -> int:
        return self.number_of_cols * self.cell_width

    @property
    def number_of_rows(self) -> int:
        return self.crucipixel.number_of_rows

    @property
    def number_of_cols(self) -> int:
        return self.crucipixel.number_of_cols

    def set_mouse_value(self, button: MouseButton,
                        cell_value: CrucipixelCellValue):
        self._mouse_button_to_crucipixel_cell_value[button] = cell_value

    def get_cell_value(self, row: int, col: int) -> CrucipixelCellValue:
        selection = self._selection_rectangle
        if selection is not None and selection.is_point_in(Point(col, row)):
            return self._selection_value
        else:
            return self.crucipixel.get_row_col_value(row, col)

    def _update_selection_rectangle(self):
        if self._selection_start_point is not None and \
           self._selection_end_point is not None:
            s = self._selection_start_point
            e = self._selection_end_point
            upper = Point(min(s.col, e.col), min(s.row, e.row))
            lower = Point(max(s.col, e.col), max(s.row, e.row))
            height = lower.row - upper.row
            width = lower.col - upper.col
            self._selection_rectangle = Rectangle(upper, width, height)

    def _highlight_rectangles(self, context, row: int, col: int):

        self._highlight_border(context, row, col)

        width = self._total_width
        height = self._total_height

        row_rectangle = Rectangle(Point(col * self.cell_width,0),
                                  self.cell_width,
                                  height)
        col_rectangle = Rectangle(Point(0,row * self.cell_height),
                                  width,
                                  self.cell_height)
        r, g, b = self.highlight_color
        context.save()
        context.set_source_rgba(r, g, b, .1)
        context.rectangle(row_rectangle.start.x,
                          row_rectangle.start.y,
                          row_rectangle.width,
                          row_rectangle.height)
        context.fill()
        context.rectangle(col_rectangle.start.x,
                          col_rectangle.start.y,
                          col_rectangle.width,
                          col_rectangle.height)
        context.fill()
        context.restore()

    def _highlight_border(self, context: cairo.Context, row: int, col: int):
        width = self._total_width
        height = self._total_height

        line_width = 3
        row_rectangles = [
            Rectangle(
                Point(1, row * self.cell_height - line_width / 2),
                width - 2,
                line_width
            ),
            Rectangle(
                Point(1, (row + 1) * self.cell_height - line_width / 2),
                width - 2,
                line_width
            )
        ]
        col_rectangles = [
            Rectangle(
                Point(col * self.cell_width - line_width / 2, 1),
                line_width,
                height - 2
            ),
            Rectangle(
                Point((col + 1) * self.cell_width - line_width / 2, 1),
                line_width,
                height - 2
            )
        ]
        context.save()
        r, g, b = self.highlight_color
        context.set_source_rgba(r, g, b, .6)
        for row_rectangle in row_rectangles:
            context.rectangle(row_rectangle.start.x,
                              row_rectangle.start.y,
                              row_rectangle.width,
                              row_rectangle.height)
            context.fill()
        for col_rectangle in col_rectangles:
            context.rectangle(col_rectangle.start.x,
                              col_rectangle.start.y,
                              col_rectangle.width,
                              col_rectangle.height)
            context.fill()
        context.restore()

    def _draw_cell(self, context: cairo.Context,
                   cell_value: CrucipixelCellValue, area: Rectangle):

        r, g, b = self.crucipixel_cell_value_to_color[cell_value]
        context.set_source_rgb(r, g, b)
        context.rectangle(area.start.x,
                          area.start.y,
                          area.width,
                          area.height)
        context.fill()
        if not self.victory_screen and cell_value == CrucipixelCellValue.EMPTY:
            # draw the X
            r, g, b = self.crucipixel_cell_value_to_color[
                CrucipixelCellValue.SELECTED
            ]
            context.set_source_rgb(r, g, b)
            context.set_line_cap(cairo.LINE_CAP_ROUND)
            delta_x = self.cell_width // 2.8
            delta_y = self.cell_height // 2.8
            context.move_to(area.start.x + area.width - delta_x,
                            area.start.y + delta_y)
            context.line_to(area.start.x + delta_x,
                            area.start.y + area.height - delta_y)
            context.move_to(area.start.x + area.width - delta_x,
                            area.start.y + area.width - delta_y)
            context.line_to(area.start.x + delta_x,
                            area.start.y + delta_y)
            context.stroke()

    def on_draw(self, widget, context):

        context.save()
        context.set_line_width(1)
        width = self._total_width
        height = self._total_height

        for row in range(self.number_of_rows):
            for col in range(self.number_of_cols):
                value = self.get_cell_value(row, col)
                rectangle = Rectangle(Point(col * self.cell_width - 1,
                                            row * self.cell_height - 1),
                                      self.cell_width + 2,
                                      self.cell_height + 2)
                self._draw_cell(context, value, rectangle)

        context.set_source_rgb(0, 0, 0)
        context.set_line_cap(cairo.LINE_CAP_SQUARE)

        context.set_line_width(2.5)
        DrawableRectangle(Point(0, 0), width, height).draw_on_context(context)
        context.stroke()

        if not self.victory_screen:
            for i, x in enumerate(range(
                    0,
                    width + self.cell_width,
                    self.cell_width
            )):
                if i % 5 == 0:
                    context.set_line_width(2.5)
                else:
                    context.set_line_width(1)
                context.move_to(x,0)
                context.line_to(x,height)
                context.stroke()

            for i, y in enumerate(range(
                    0,
                    height + self.cell_height,
                    self.cell_height
            )):
                if i % 5 == 0:
                    context.set_line_width(2.5)
                else:
                    context.set_line_width(1)
                context.move_to(0,y)
                context.line_to(width,y)
                context.stroke()

        if self._highlight_col is not None and self._highlight_row is not None\
                and self._should_highlight and not self.victory_screen:
            self._highlight_rectangles(
                context,
                self._highlight_row,
                self._highlight_col
            )

        context.restore()

    def _point_to_row_col(self, point: Point) -> Tuple[int, int]:
        row = int(point.y // self.cell_height)
        col = int(point.x // self.cell_width)
        return clamp(row, 0, self.number_of_rows - 1), \
               clamp(col, 0, self.number_of_cols - 1)

    def _move_cursor(self, row: int, col: int):
        self.highlight_row_col(row, col)
        if self._selection_start_point is not None:
            self._move_selection(row, col)

    def on_mouse_move(self, widget: Widget, event: MouseEvent) -> bool:
        row, col = self._point_to_row_col(event)
        self._move_cursor(row, col)
        return False

    def on_mouse_down(self, widget: Widget, event: MouseEvent) -> bool:
        row, col = self._point_to_row_col(event)
        value = self._mouse_button_to_crucipixel_cell_value[event.button]
        self._start_selection(value, row, col)
        return True

    def on_mouse_up(self, widget: "Widget", event: MouseEvent) -> bool:
        print(self._highlight_row, self._highlight_col)
        self._end_selection()
        print(self._highlight_row, self._highlight_col)
        return False

    def on_key_down(self, widget: "Widget", event: KeyboardEvent) -> bool:
        super().on_key_down(widget, event)

        if event.key in self._keyboard_value_to_crucipixel_cell_value:
            is_there_one = False
            for k in self._keyboard_value_to_crucipixel_cell_value.keys():
                if k in self._key_pressed:
                    is_there_one = True
            if is_there_one:
                return False
            else:
                self._key_pressed.add(event.key)
            if self._highlight_col is None:
                self._highlight_col = 0
                self._highlight_row = 0
            self._should_highlight = True
            self._start_selection(
                self._keyboard_value_to_crucipixel_cell_value[event.key],
                self._highlight_row,
                self._highlight_col
            )
            return True
        elif event.key in self._keyboard_value_to_movement_directions:
            directions = self._keyboard_value_to_movement_directions[event.key]
            if self._highlight_col is None:
                row, col = 0, 0
            else:
                row, col = self._highlight_row, self._highlight_col

            for direction in directions:
                if direction == Direction.UP:
                    row -= 1
                elif direction == Direction.DOWN:
                    row += 1
                elif direction == Direction.RIGHT:
                    col += 1
                elif direction == Direction.LEFT:
                    col -= 1
            row = clamp(row, 0, self.number_of_rows - 1)
            col = clamp(col, 0, self.number_of_cols - 1)
            self._move_cursor(row, col)
            return True


    def on_key_up(self, widget: "Widget", event: KeyboardEvent) -> bool:
        super().on_key_up(widget, event)
        if event.key in self._key_pressed:
            self._key_pressed.remove(event.key)
            if event.key in self._keyboard_value_to_crucipixel_cell_value:
                self._end_selection()
        return False


    def _get_moves(self) -> Iterable[MoveAtom]:
        selection_rectangle = self._selection_rectangle
        moves = (
            MoveAtom(selection_rectangle.start.y + row_offset,
                     selection_rectangle.start.x + col_offset,
                     self._selection_value)
            for col_offset in range(selection_rectangle.width + 1)
            for row_offset in range(selection_rectangle.height + 1)
        )
        return moves

    def _start_selection(self, value: CrucipixelCellValue, row: int, col: int):
        if self._selection_start_point is None:
            self._selection_value = value
            self._selection_start_point = Point(col, row)
            self._selection_end_point = Point(col, row)
            self._update_selection_rectangle()
            self.crucipixel.make_move(self._get_moves())

    def _move_selection(self, row: int, col: int):
        new_point = Point(col, row)
        if new_point != self._selection_end_point:
            self._selection_end_point = new_point
            self._update_selection_rectangle()
            self.crucipixel.undo_move()
            self.crucipixel.make_move(self._get_moves())

    def _handle_guide_line_check(self, orientation: Orientation, index: int):
        if self.crucipixel.is_line_full(orientation, index):
            if self.crucipixel.is_line_wrong(orientation, index):
                status = GuideStatus.WRONG
            else:
                status = GuideStatus.DONE
        else:
            status = GuideStatus.DEFAULT
        if orientation == Orientation.HORIZONTAL:
            orientation = Orientation.VERTICAL
        else:
            orientation = Orientation.HORIZONTAL
        self.on_guide_update(orientation, index, status)

    def _end_selection(self):
        selection_rectangle = self._selection_rectangle
        if selection_rectangle is not None:
            for col_offset in range(selection_rectangle.width + 1):
                col = selection_rectangle.start.x + col_offset
                self._handle_guide_line_check(Orientation.VERTICAL, col)
            for row_offset in range(selection_rectangle.height + 1):
                row = selection_rectangle.start.y + row_offset
                self._handle_guide_line_check(Orientation.HORIZONTAL, row)
        self._selection_end_point = None
        self._selection_start_point = None
        self._selection_rectangle = None
        self._selection_value = None

    def _reset_selection(self):
        self._selection_start_point = None
        self._selection_end_point = None
        self._selection_rectangle = None
        self._selection_value = None

        self.crucipixel.undo_move()

    def highlight_row_col(self, row: int, col: int):
        self._highlight_row = row
        self._highlight_col = col

    def on_mouse_exit(self) -> bool:
        self._should_highlight = False
        return False

    def is_point_in(self,p: Point ,category=MouseEvent.UNKNOWN) -> bool:
        # if category == MouseEvent.MOUSE_UP \
        #         or category == MouseEvent.MOUSE_MOVE:
        #     if self._selection_start_point is not None:
        #         return True
        if category == MouseEvent.MOUSE_MOVE:
            if self._selection_start_point is not None:
                return True
        return super().is_point_in(p, category)

    def on_mouse_enter(self) -> bool:
        self._should_highlight = True
        return False


class CrucipixelGridWonWrapper(UncheckedContainer):

    def __init__(self, grid: CrucipixelGrid, crucipixel: core.Crucipixel):
        super().__init__()
        self.grid = grid
        self.upper_padding = 30
        self.left_padding = 30
        self._container = UncheckedContainer()
        self._container.add(grid)
        self.add(self._container)
        self.grid.victory_screen = crucipixel.is_won

        # def on_won_change(is_won: bool) -> bool:
        #     if not is_won:
        #         self.grid.victory_screen = False
        #     else:
        #         self.grid.victory_screen = True
        # crucipixel.on_won_change_callbacks_list.append(on_won_change)

    def on_draw(self, widget: "Widget", context: cairo.Context):
        width, height = self.container_size
        grid_width = self.grid._total_width
        grid_height = self.grid._total_height
        width_factor = (width - 2 * self.left_padding)/grid_width
        height_factor = (height - 2 * self.upper_padding)/grid_height
        factor = max(0.001, min(width_factor, height_factor, 1))
        self._container.set_scale(factor, factor)
        grid_width *= factor
        grid_height *= factor
        self._container.set_translate((width - grid_width) / 2,
                                      (height - grid_height) / 2)
        return super().on_draw(widget, context)

    def is_point_in(self,p: Point, category=MouseEvent.UNKNOWN) -> bool:
        return False

def main() -> int:
    root = Root()
    main_window = MainWindow(title="Prova")
    main_window.add(root)

    crucipixel_model = parse_file_name("/home/giovanni/.crucipixel/monopattino.json")
    crucipixel_core = core.Crucipixel(crucipixel_model)
    crucipixel_core.make_move((MoveAtom(i, i, CrucipixelCellValue.SELECTED) for i in range(5)))
    grid = CrucipixelGrid(crucipixel_core)

    root.set_child(grid)

    main_window.start_main()

if __name__ == '__main__':
    main()
