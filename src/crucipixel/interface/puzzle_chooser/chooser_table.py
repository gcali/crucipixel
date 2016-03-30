'''
Created on May 20, 2015

@author: giovanni
'''
from typing import List, Tuple, Iterable, Callable

import cairo
import itertools

from crucipixel.data.crucipixel_scheme import CrucipixelScheme
from crucipixel.data.json_parser import parse_file_name
from crucipixel.interface import global_constants
from lightwidgets.events import MouseEvent, MouseButton
from lightwidgets.geometry import Rectangle, Point
from lightwidgets.stock_widgets.arrow import Arrow
from lightwidgets.stock_widgets.buttons import Button, BetterButton
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget

from gi.overrides.Gtk import Gtk
from gi.repository import Gdk

class _CellDataSize:

    def __init__(self, width: int, height: int, padding: int=0):
        self.width = width
        self.height = height
        self.padding = padding

    def calculate_padding(self, new_width: int):
        self.padding = max(0, (new_width - self.width) / 2)

    @property
    def total_width(self) -> int:
        return self.width + 2 * self.padding

    def __str__(self):
        return "w{}h{}p{}".format(self.width, self.height, self.padding)


class _LineExtents:

    def __init__(self, cells_extents: List[_CellDataSize],
                 margin: int):
        self.cells_extents = cells_extents
        self._total_width = None
        self._total_height = None
        self.margin = margin

    def get_cell_data_left(self, index: int):
        left = 0
        for c in self.cells_extents[:index]:
            left += 2 * self.margin + c.width + 2 * c.padding
        left += self.cells_extents[index].padding + self.margin
        return left

    @property
    def total_width(self):
        if self._total_width is None:
            self._calc_size()
        return self._total_width

    @property
    def total_height(self):
        if self._total_height is None:
            self._calc_size()
        return self._total_height

    def refresh_size(self):
        self._total_height = None
        self._total_width = None

    def _calc_size(self):
        total_height = 0
        total_width = 0

        margin = self.margin

        for cell in self.cells_extents:
            total_height = max(total_height, cell.height)
            total_width += cell.width + 2 * margin + 2 * cell.padding

        total_height += 2 * margin

        self._total_width = total_width
        self._total_height = total_height

    def __getitem__(self, item):
        return self.cells_extents.__getitem__(item)

    def __iter__(self) -> Iterable[_CellDataSize]:
        return self.cells_extents.__iter__()

    def __len__(self):
        return self.cells_extents.__len__()

class _TableExtents:

    def __init__(self, title_extents: _LineExtents,
                 line_extents: List[_LineExtents]):
        self.title_extents = title_extents
        self.line_extents = line_extents
        self._base_vertical_positions = None
        self.entries_width = 0
        self._heights = 0
        self._calc_size()

    def get_height_up_to(self, skip: int, how_many: int) -> int:
        # print("Skip!", skip, how_many, len(self._heights))
        return sum(self._heights[skip: skip + how_many])

    def get_height_of(self, skip: int, how_many: int, index: int) -> int:
        if index >= how_many:
            raise IndexError(index)
        return self._heights[skip + index]

    def get_vertical_position(self, index: int, skip: int=0):
        return sum(self._heights[skip:skip + index - 1])

    def _calc_size(self):

        line_extents = self.line_extents
        title_extents = self.title_extents

        line_extents = list(itertools.chain([title_extents], line_extents))

        if not line_extents:
            return

        max_width = [0 for _ in title_extents]

        margin = line_extents[0].margin

        heights = []

        for line in line_extents:
            h = line.total_height
            heights.append(h)
            for index, cell in enumerate(line):
                max_width[index] = max(max_width[index], cell.total_width)

        for i, line in enumerate(line_extents):
            # print("Line", i)
            for new_width, cell in zip(max_width, line):
                # print("-> Cell", cell, new_width)
                cell.calculate_padding(new_width)
                # print("-> New Cell", cell)

        total_width = 0
        for value in max_width:
            total_width += value + 2 * margin
        # print("Total width:", total_width)

        self.entries_width = total_width
        self._heights = heights[1:]

    def iter_over(self, to_skip: int, how_many: int):
        for l in self.line_extents:
            if to_skip > 0:
                to_skip -= 1
            elif how_many > 0:
                how_many -= 1
                yield l
            else:
                break

    # def __iter__(self) -> Iterable[_LineExtents]:
    #     return self.iter_over(self.skip, self.how_many)

    def __getitem__(self, item):
        return self.line_extents.__getitem__(item)


class TableEntry:

    def __init__(self, title: object, hardness: object,
                 rows: object, cols: object):
        self.title = str(title)
        self.hardness = str(hardness)
        self.rows = str(rows)
        self.cols = str(cols)

    def __iter__(self):
        yield self.title
        yield self.hardness
        yield self.rows + "x" + self.cols

    def __getitem__(self, item):
        for i in self:
            if item == 0:
                return i
            else:
                item -= 1
        raise IndexError(item)

    @property
    def attributes(self) -> int:
        return len(list(self))


class TableNavigator(UncheckedContainer):

    def __init__(self, up_pos: int = 0, down_pos: int = 0):
        super().__init__()

        base = 15
        height = 15

        self.width = base
        self.height = height

        self._up_arrow = Arrow(base_size=base, height=height, direction=Arrow.UP)
        self._down_arrow = Arrow(base_size=base, height=height, direction=Arrow.DOWN)

        self._left_offset = base / 2
        self._up_offset = height / 2

        self._up_pos = 0
        self._down_pos = 0

        self.up_pos = up_pos
        self.down_pos = down_pos

        self.add(self._up_arrow)
        self.add(self._down_arrow)


    @property
    def on_down_arrow_action(self):
        return self._down_arrow.action

    @property
    def on_up_arrow_action(self):
        return self._up_arrow.action

    @on_down_arrow_action.setter
    def on_down_arrow_action(self, value):
        self._down_arrow.action = value

    @on_up_arrow_action.setter
    def on_up_arrow_action(self, value):
        self._up_arrow.action = value

    @property
    def up_pos(self) -> int:
        return self._up_pos

    @up_pos.setter
    def up_pos(self, value):
        self._up_pos = value
        self._up_arrow.set_translate(
            self._left_offset,
            self._up_offset + value
        )

    @property
    def down_pos(self) -> int:
        return self._down_pos

    @down_pos.setter
    def down_pos(self, value):
        self._down_pos = max(value, self._up_pos + 2 * self._up_offset)
        self._down_arrow.set_translate(
            self._left_offset,
            - self._up_offset + value
        )

    def on_draw(self,widget,context):
        if self._down_pos - self.height  <= self._up_pos:
            pass
        else:
            super().on_draw(widget, context)


class TableContents(Widget):
    
    def __init__(self, entries: List[TableEntry]=[], **kwargs):
        super().__init__(**kwargs)

        self.ID = "TableContents"

        self._entries = entries
        self._font_size = 20
        self.margin = 4
        self._skip = 0
        self._how_many = len(entries)
        self._shown = self._how_many
        self._table_extents = None
        self._max_width = None
        self._max_height = None
        self._to_highlight = None
        self.table_height = 0
        self.table_width = 0
        self.title_height = 0
        self._selected_callback = lambda x: None

    def set_selected_callback(self, callback: Callable[[int], None]):
        self._selected_callback = callback

    def on_mouse_up(self,w,e):
        if self._to_highlight is not None:
            self._selected_callback(self._to_highlight + self.skip)

    @property
    def title(self) -> Iterable[str]:
        yield "NAME"
        yield "H"
        yield "SIZE"

    @property
    def skip(self):
        return min(self._skip, len(self._entries) - self._shown)

    @skip.setter
    def skip(self, value):
        self._skip = max(value, 0)

    @property
    def how_many(self):
        v = self._how_many
        return min(v, len(self._entries))

    @how_many.setter
    def how_many(self, value):
        self._how_many = max(value, 1)

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value
        self._reset_calculations()

    @property
    def entries(self) -> List[TableEntry]:
        return self._entries

    @entries.setter
    def entries(self, entries):
        self._how_many = len(entries)
        self._entries = entries
        self._reset_calculations()

    def _reset_calculations(self):
        self._table_extents = None

    def add_entry(self, entry: TableEntry):
        self._entries.append(entry)
        self._reset_calculations()

    def set_max_size(self, width: int, height: int):
        self._max_width = width
        self._max_height = height

        self._reset_calculations()

    def _get_line_extents(self,
                          entry: str,
                          context: cairo.Context,
                          min_first_width: int=1) -> _LineExtents:

        def _get_cell_data_size(data: str) -> _CellDataSize:
            xb, yb, w, h, xa, ya = context.text_extents(data)
            return _CellDataSize(xa, -yb)


        # entry = self.entries[index]
        extents = _LineExtents(
            [_get_cell_data_size(data) for data in entry],
            self.margin
        )

        width = extents.total_width
        # print("Width: {} Max: {}".format(width, self._max_width))
        # if width > self._max_width:
        left_start = extents.get_cell_data_left(1)
        first_width = self._max_width - width + left_start - self.margin * 4
        first_width = max(first_width, min_first_width)
        if first_width < extents[0].width:
            extents[0].width = first_width
        else:
            extents[0].calculate_padding(first_width)

        return extents

    def _update_table_extents(self, context: cairo.Context,
                              max_width:int = None):
        # print("Updating!")

        title_extents = self._get_line_extents([e for e in self.title], context)
        self._table_extents = _TableExtents(
            title_extents,
            [self._get_line_extents(e, context, title_extents[0].width)
             for e in self.entries]
        )

    def _get_line_index_from_point(self, p: Point):

        y = p.y
        limit = self.margin + self._table_extents.title_extents.total_height
        if y < limit:
            return None
        for i in range(self._shown):
            limit += self._table_extents.get_height_of(self.skip, self._shown, i)
            if y < limit:
                return i
        else:
            return None

    def is_point_in(self,p: Point, category=MouseEvent.UNKNOWN):
        if self._table_extents is None:
            return False
        else:
            y = p.y
            h = self._table_extents.get_height_up_to(self.skip, self._shown) + \
                self._table_extents.title_extents.total_height + self.margin
            if y < 0 or y > h:
                return False
            x = p.x
            w = self._table_extents.entries_width
            if x < 0 or x > w:
                return False
            return True

    def _highlight(self, index: int):
        self._to_highlight = index
        self.invalidate()

    def on_mouse_move(self,widget, event):
        super().on_mouse_move(widget, event)
        self._highlight(self._get_line_index_from_point(event))

    def on_mouse_exit(self):
        super().on_mouse_exit()
        self._highlight(None)

    def on_draw(self, widget: Widget, context: cairo.Context):
        super().on_draw(widget, context)

        context.save()
        context.set_font_size(self.font_size)

        if self._table_extents is None:
            self._update_table_extents(context)

        skip = max(self.skip, 0)
        how_many = self.how_many

        table_extents = self._table_extents
        title_extents = self._table_extents.title_extents

        expected_height = title_extents.total_height + self.margin

        entries = self.entries

        base = skip
        up_to = skip
        over = False
        while up_to < len(entries) and not over:
            expected_height += table_extents[up_to].total_height
            over = expected_height >= self._max_height
            if not over:
                up_to += 1

        while base > 0 and not over:
            expected_height += table_extents[base-1].total_height
            over = expected_height >= self._max_height
            if not over:
                base -= 1

        how_many = up_to - base
        skip = base

        entries = self.entries[skip:skip + how_many]

        def table_extents_iterator():
            return table_extents.iter_over(
                skip, how_many
            )

        start_x, start_y = context.get_current_point()

        start_y += title_extents.total_height
        h = title_extents.total_height
        self.title_height = h
        for (index, cell), data in zip(enumerate(title_extents), self.title):
            context.save()
            offset = title_extents.get_cell_data_left(index)
            context.rectangle(start_x + offset, start_y - h, cell.width, 2*h)
            context.clip()
            context.move_to(
                start_x + offset,
                start_y
            )
            context.show_text(data)
            context.restore()
        # start_y += self.margin

        curr_x, curr_y = start_x, start_y# + title_extents.total_height

        for line_index, (line_extent, entry) in enumerate(zip(table_extents_iterator(), entries)):
            # print("Handling", entry[0])
            h = line_extent.total_height
            curr_y += h
            # how_many = line_index
            # print("Line index:", how_many)
            if curr_y + self.margin >= self._max_height:
                # print("I'm breaking at", how_many)
                # print("Max height:", self._max_height)
                break
            for (cell_index, cell), data in zip(enumerate(line_extent), entry):
                # print("->", data, cell)
                context.save()
                offset = line_extent.get_cell_data_left(cell_index)
                context.rectangle(curr_x + offset, curr_y - h, cell.width, 2*h)
                context.clip()
                context.move_to(
                    curr_x + offset,
                    curr_y
                )
                context.show_text(data)
                context.restore()
        # else:
        #     how_many += 1
        # print("How many?", how_many)

        curr_x = start_x
        end_x = table_extents.entries_width
        curr_y = start_y + self.margin
        end_y = table_extents.get_height_up_to(skip, how_many) + start_y + self.margin + 1

        self.table_height = end_y
        self.table_width = end_x

        for line in table_extents_iterator():
            context.move_to(curr_x, curr_y)
            context.line_to(end_x, curr_y)
            context.stroke()
            curr_y += line.total_height
        context.move_to(curr_x, curr_y)
        context.line_to(end_x, curr_y)
        context.stroke()

        curr_x = start_x
        curr_y = start_y - 1 + self.margin
        line = table_extents[0]
        for cell in line:
            context.move_to(curr_x, curr_y)
            context.line_to(curr_x, end_y)
            context.stroke()
            curr_x += cell.total_width + 2 * self.margin
        context.move_to(curr_x, curr_y)
        context.line_to(curr_x, end_y)
        context.stroke()

        if self._to_highlight is not None:
            r, g, b = global_constants.highlight
            context.set_source_rgba(r, g, b, .6)
            index = self._to_highlight
            base = start_y + table_extents.get_height_up_to(skip, index) + self.margin
            h = table_extents.get_height_of(skip, how_many, index)
            context.rectangle(start_x, base, table_extents.entries_width, h)
            context.fill()


        context.restore()

        self._shown = how_many


class ChooserTable(UncheckedContainer):

    def __init__(self, entries: List[TableEntry]=[], **kwargs):
        super().__init__()
        self.contents = TableContents(entries)
        self.contents.set_max_size(400, 70)
        self.navigator = TableNavigator()
        self.navigator.up_pos += 15
        self.back_button = BetterButton("Back", origin = BetterButton.RIGHT)
        self.back_button.font_size = 20

        self.add(self.contents)
        self.add(self.navigator)
        self.add(self.back_button)
        def adjust_skip(value):
            print("Old:", self.skip)
            skip = self.skip
            self.skip = skip + value
            print("New:", self.skip)
            self.invalidate()

        self.navigator.on_up_arrow_action = lambda: adjust_skip(-1)
        self.navigator.on_down_arrow_action = lambda: adjust_skip(1)

    def set_contents_callback(self, callback: Callable[[int], None]) -> None:
        self.contents.set_selected_callback(callback)

    def set_back_callback(self, callback: Callable[[MouseButton], None]) -> None:
        self.back_button.on_click_action = callback

    @property
    def font_size(self):
        return self.contents.font_size

    @font_size.setter
    def font_size(self, value):
        self.contents.font_size = value

    @property
    def skip(self):
        return self.contents.skip

    @skip.setter
    def skip(self, value):
        print("New value!", value)
        self.contents.skip = value

    @property
    def how_many(self):
        return self.contents.how_many

    @how_many.setter
    def how_many(self, value):
        self.contents.how_many = value

    def on_draw(self, widget: "Widget", context: cairo.Context):
        translation = 10, 10
        context.translate(*translation)
        self.contents.set_translate(*translation)
        self.navigator.set_translate(*translation)
        self.back_button.set_translate(*translation)
        up_margin = 4
        down_margin = 6
        left_margin = 4
        right_margin = self.navigator.width
        navigator_margin = 4
        base_x, base_y = self.fromWidgetCoords.transform_point(0, 0)
        base_x += translation[0]
        base_y += translation[1]
        width = self.container_size[0] - 2 * base_x - right_margin - 2 * navigator_margin
        height = self.container_size[1] - 2 * base_y - down_margin
        self.contents.set_max_size(width, height)
        self.contents.on_draw(widget, context)
        offset = self.contents.table_width + navigator_margin
        self.navigator.translate(offset, 0)
        context.translate(offset, 0)
        self.navigator.down_pos = self.contents.table_height
        self.navigator.on_draw(widget, context)
        context.translate(-offset, 0)
        rectangle_width = left_margin + offset + navigator_margin + right_margin
        rectangle_height = self.contents.table_height + up_margin + down_margin
        context.rectangle(
            -left_margin,
            -up_margin,
            rectangle_width,
            rectangle_height
        )
        context.stroke()

        button_left = (rectangle_width - left_margin) / 2
        button_left = 0
        button_left = rectangle_width - left_margin
        button_up = rectangle_height + up_margin

        self.back_button.translate(button_left, button_up)
        context.translate(button_left, button_up)
        self.back_button.on_draw(self, context)


def scheme_to_entry(scheme: CrucipixelScheme) -> TableEntry:
    return TableEntry(
        scheme.title,
        scheme.hard,
        len(scheme.rows),
        len(scheme.cols)
    )


def main() -> int:
    main_window = MainWindow(title="table")

    root = Root(width=-1, height=-1)
    main_window.add(root)

    file_names=["al_parco.json", "brachiosauri.json", "monopattino.json", "mostro.json"]
    schemes = [parse_file_name("../data/" + name) for name in file_names]

    table_entries = [
        TableEntry(scheme.title, scheme.hard, len(scheme.rows), len(scheme.cols))
        for scheme in schemes
    ]

    for scheme in schemes:
        print(scheme.title)

    table = ChooserTable(table_entries)

    table.translate(50, 50)

    table.skip = 1
    table.how_many = 10

    table.set_back_callback(lambda: root.set_min_size(200, 200))
    table.set_contents_callback(lambda x: print("{} selected".format(x)))
    table.font_size = 20
    root.set_child(table)

    main_window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))

    main_window.start_main()

if __name__ == '__main__':
    main()
