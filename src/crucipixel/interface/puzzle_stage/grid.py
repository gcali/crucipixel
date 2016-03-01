"""
Created on May 19, 2015

@author: giovanni
"""
from typing import Tuple

import cairo

from crucipixel.data.json_parser import parse_file_name
from crucipixel.interface import global_constants
from crucipixel.logic import core
from lightwidgets.events import MouseEvent
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.stock_widgets.root import Root, MainWindow
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.support import DefaultDict, clamp, get_from_to_inclusive


class CrucipixelGrid(Widget):
    
    SELECTION_FREE = 0
    SELECTION_LINE = 1
    SELECTION_RECTANGLE = 2

    @classmethod
    def from_crucipixel(cls,
                        crucipixel,
                        cell_size,
                        start=Point(0,0)):
        return cls(cols=crucipixel.cols,
                   rows=crucipixel.rows,
                   start=start,
                   width=cell_size,
                   height=cell_size,
                   crucipixel=crucipixel)

    def __init__(self,
                 core_crucipixel: core.Crucipixel,
                 start=Point(0,0),
                 cell_width=10,
                 cell_height=10,
                 *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "CrucipixelWindow"

        self.cell_width = cell_width
        self.cell_height=cell_height

        self.is_mouse_selection_on = False
        self.is_keyboard_selection_on = False
        
        self.input_function_map = {"left": "selected",
                                   "right": "empty",
                                   "middle": "default"}

        self.function_color_map = {"selected": global_constants._start_selected,
                                   "empty": global_constants._start_empty,
                                   "default": global_constants._start_default}
        self.input_selection_style_map = {"1": CrucipixelGrid.SELECTION_FREE,
                                          "2": CrucipixelGrid.SELECTION_LINE,
                                          "3": CrucipixelGrid.SELECTION_RECTANGLE}
        
        self.selection_style = CrucipixelGrid.SELECTION_RECTANGLE

        self.set_translate(start.x, start.y)
        self._selected_function_property = "selected"

        self._selection_start_point = Point(0,0)
        self._selection_backup = []
        self._selection_core_encode = []

        self._cell_function = DefaultDict()
        self._cell_function.default = lambda: "default"

        self._highlight_row = None
        self._highlight_col = None

        self.number_of_cols = core_crucipixel.cols
        self.number_of_rows = core_crucipixel.rows
        self._core_crucipixel = core_crucipixel
        self.update_status_from_crucipixel()

        self.clip_rectangle = Rectangle(Point(-.5,-.5),self._total_height+2,self._total_width+2)

        self.should_drag = False
        self.is_dragging = False

        self._movement_keys = global_constants._global_movement_keys
        reversed_selection_keys = {
            "selected": ["space", "i"],
            "default": ["p", "backspace"],
            "empty": ["x", "o"]
        }
        self._selection_keys = {}
        for (f,l) in reversed_selection_keys.items():
            for k in l:
                self._selection_keys[k] = f

        def handle_select_color(name, value):
            self.input_function_map[name] = value
            print(name, value)

        self.register_signal("select_color", handle_select_color)
    
    @property
    def _selected_function(self):
        return self._selected_function_property

    @_selected_function.setter
    def _selected_function(self,value):
        self._selected_function_property = value
        self._selected_core_function_property = self._function_to_crucipixel_cell(value)
        
    @property
    def _selected_core_function(self):
        return self._selected_core_function_property

    @_selected_core_function.setter
    def _selected_core_function(self,value):
        self._selected_core_function_property = value
        self._selected_function_property = self._crucipixel_to_function_cell(value)

    @property
    def _total_height(self):
        return self.number_of_rows * self.cell_height
    
    @property
    def _total_width(self):
        return self.number_of_cols * self.cell_width
    
    @property
    def core_crucipixel(self):
        return self._core_crucipixel
    
    @core_crucipixel.setter
    def core_crucipixel(self, value: core.Crucipixel):
        self._core_crucipixel = value
        self.number_of_rows = value.rows
        self.number_of_cols = value.cols
        self.update_status_from_crucipixel()

    def _function_to_color(self,function):
        return self.function_color_map[function]

    def _crucipixel_to_function_cell(self,cell):
        if cell == core.Crucipixel.EMPTY:
            return "empty"
        elif cell == core.Crucipixel.MAIN_SELECTED:
            return "selected"
        elif cell == core.Crucipixel.DEFAULT:
            return "default"
        else:
            raise NameError("No known cell value {}".format(cell))
    
    def _function_to_crucipixel_cell(self,function):
        if function == "selected":
            return core.Crucipixel.MAIN_SELECTED
        elif function == "empty":
            return core.Crucipixel.EMPTY
        elif function == "default":
            return core.Crucipixel.DEFAULT
    
    def update_status_from_crucipixel(self):
        for i in range(self.core_crucipixel.rows):
            for j in range(self.core_crucipixel.cols):
                self._cell_function[i, j] = \
                    self._crucipixel_to_function_cell(
                        self._core_crucipixel[i,j]
                    )
                self.invalidate()
    
    def on_draw(self, widget, context):

        def highlight_rectangles(row, col):
            width = self._total_width
            height = self._total_height
            
            line_width = 3
            
            row_rectangles = [
                Rectangle(
                    Point(1, row * self.cell_height - line_width/2),
                    width-2,
                    line_width
                ),
                Rectangle(
                    Point(1, (row + 1) * self.cell_height - line_width/2),
                    width-2,
                    line_width
                )
            ]

            col_rectangles = [
                Rectangle(
                    Point(col * self.cell_width - line_width/2, 1),
                    line_width,
                    height-2
                ),
                Rectangle(
                    Point((col+1) * self.cell_width - line_width/2, 1),
                    line_width,
                    height-2
                )
            ]
            context.save()
            r, g, b = global_constants._highlight
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
            row_rectangle = Rectangle(Point(col * self.cell_width,0),
                                      self.cell_width,
                                      height)
            col_rectangle = Rectangle(Point(0,row * self.cell_height),
                                      width,
                                      self.cell_height)
            context.set_source_rgba(r,g,b,.1)
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
            
        context.save()
        context.set_line_width(1)
        width = self._total_width
        height = self._total_height
        
        def draw_cell(function:"cell_function",area:"Rectangle"):
            r, g, b = self._function_to_color(function)
            context.set_source_rgb(r, g, b)
            context.rectangle(area.start.x,
                              area.start.y,
                              area.width,
                              area.height)
            context.fill()
            if True and function == "empty":
                r, g, b = self._function_to_color("selected")
                context.set_source_rgb(r,g,b)
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
                

#         for (k,v) in self._cell_function.items():
        for row in range(self.number_of_rows):
            for col in range(self.number_of_cols):
                k = row, col
                v = self._cell_function[k]
                rectangle = Rectangle(Point(col * self.cell_width,
                                            row * self.cell_height),
                                      self.cell_width,
                                      self.cell_height)
                if row < 5 and col < 5:
                    pass
                draw_cell(v, rectangle)
                        
        context.set_source_rgb(0,0,0)
        context.set_line_cap(cairo.LINE_CAP_SQUARE)
        i=0
        for x in range(0,width+self.cell_width,self.cell_width):
            if i % 5 == 0:
                context.set_line_width(2.5)
            else:
                context.set_line_width(1)
            context.move_to(x,0)
            context.line_to(x,height)
            context.stroke() 
            i+=1

        i=0
        for y in range(0,height+self.cell_height,self.cell_height):
            if i % 5 == 0:
                context.set_line_width(2.5)
            else:
                context.set_line_width(1)
            context.move_to(0,y)
            context.line_to(width,y)
            context.stroke()
            i+=1
        
        context.move_to(0,0)
        context.line_to(-10,-10)
        context.stroke() 
        
        if self._highlight_col is not None and\
           self._highlight_row is not None:
            highlight_rectangles(self._highlight_row,
                                 self._highlight_col)

        context.restore()
    
    def _get_cell_id(self, pos:Point) -> Tuple[int, int]:
            cell_col = int(pos.x // self.cell_width)
            cell_row = int(pos.y // self.cell_height)
            return cell_row, cell_col

    def on_key_up(self, w, e):
        super().on_key_up(w,e)
        if e.key == "ctrl_l":
            self.should_drag = False
        elif e.key == "r":
            self.update_status_from_crucipixel()
        elif e.key in self._selection_keys and self.is_keyboard_selection_on:
            self._handle_key_selection_end()
            self.is_keyboard_selection_on = False
        else:
            try:
                self.selection_style = self.input_selection_style_map[e.key]
            except KeyError:
                pass
        return False
    
    def on_key_down(self, w, e):
        super().on_key_down(w,e)
        if e.key == "ctrl_l":
            self.should_drag = True
            print("Should drag?")
            return True
        elif e.key in self._movement_keys:
            self._handle_hover_movement(self._movement_keys[e.key])
            if self.is_keyboard_selection_on:
                self._handle_key_selection_move(self._movement_keys[e.key])
            self.invalidate()
            return True
        elif e.key in self._selection_keys and not self.is_keyboard_selection_on:
            if self.is_mouse_selection_on:
                self.is_mouse_selection_on = False
                self._selection_end()
            self.is_keyboard_selection_on = True
            self._handle_key_selection_start(self._selection_keys[e.key])
            self.invalidate()
        return False
    
    def _handle_key_selection_start(self, function):
        if self.is_mouse_selection_on:
            self._selection_end()
        if self._highlight_col is None:
            col = 0
        else:
            col = self._highlight_col
        if self._highlight_row is None:
            row = 0
        else:
            row = self._highlight_row
        start_point = Point(col, row)
        self._selection_start(start_point, function)
    
    def _handle_key_selection_move(self, direction):
        col = self._highlight_col if self._highlight_col is not None else 0
        row = self._highlight_row if self._highlight_row is not None else 0
        self._selection_move(Point(col, row))

    def _handle_key_selection_end(self):
        self._selection_end()

    
    def _handle_hover_movement(self,direction:"str"):
        self.broadcast_lw_signal("debug_text",direction)
        def get_movement(direction):
            if direction == "down":
                movement = Point(0, 1)
            elif direction == "up":
                movement = Point(0, -1)
            elif direction == "left":
                movement = Point(-1, 0)
            elif direction == "right":
                movement = Point(1, 0)
            else:
                raise NameError("Couldn't find direction {}".format(direction))
            return movement
        movement = Point(0, 0)
        for d in direction.split("_"):
            movement += get_movement(d) 
        curr_row, curr_col = self._highlight_row, self._highlight_col
        if curr_row is None:
            self._highlight_row = 0
        else:
            self._highlight_row = clamp(self._highlight_row + movement.row, 
                                        0, 
                                        self.number_of_rows-1)
        if curr_col is None:
            self._highlight_col = 0
        else:
            self._highlight_col = clamp(self._highlight_col + movement.col,
                                        0,
                                        self.number_of_cols-1)
        
    def _restore_selection(self):
        for row, col, color in self._selection_backup:
            self._cell_function[row, col] = color


    def _select_rectangle(self, cell_row_end, cell_col_end):
        for c in get_from_to_inclusive(self._selection_start_point.col, cell_col_end):
            for r in get_from_to_inclusive(self._selection_start_point.row, cell_row_end):
                self._selection_backup.append((r, c, self._cell_function[r, c]))
                self._cell_function[r, c] = self._selected_function
                self._selection_core_encode.append((r, c, self._selected_core_function))

    def _selection_start(self, start_point, selected_function):
        self.is_mouse_selection_on = True
        self._selection_start_point = start_point
        self._selected_function = selected_function
        print("Selection start!", start_point.row, start_point.col)
        self._select_rectangle(start_point.row, start_point.col)

    def on_mouse_down(self, w, e):
        point_in = self.is_point_in(Point(e.x, e.y))
        if (not self.should_drag) and\
           (not self.is_keyboard_selection_on) and\
           point_in:
            cell_id = self._get_cell_id(e)
            start_point = Point(cell_id[1], cell_id[0])
            selected_function = self.input_function_map[e.button]
            self.is_mouse_selection_on = True
            self._selection_start(start_point, selected_function)
            self.invalidate()
            return True
        else:
            if self.should_drag or\
               not point_in:
                self.is_dragging = True
                return False
            else:
                return False
    
    def on_mouse_exit(self):
        super().on_mouse_exit()
        self._highlight_col = None
        self._highlight_row = None
        self.invalidate() 

    def _selection_move(self, selection_pos):
        if self.selection_style == CrucipixelGrid.SELECTION_FREE:
            self._selection_backup = []
            self._selection_start_point = selection_pos
            self._select_rectangle(selection_pos.row, selection_pos.col)
        elif self.selection_style == CrucipixelGrid.SELECTION_LINE:
            self._selection_core_encode = []
            self._restore_selection()
            self._selection_backup = []
            if selection_pos.col == self._selection_start_point.col or\
               selection_pos.row == self._selection_start_point.row:
                self._select_rectangle(selection_pos.row, selection_pos.col)
        elif self.selection_style == CrucipixelGrid.SELECTION_RECTANGLE:
            self._selection_core_encode = []
            self._restore_selection()
            self._selection_backup = []
            self._select_rectangle(selection_pos.row, selection_pos.col)

    def on_mouse_move(self, w, e):
        if self.is_dragging:
            print("I'm dragging!")
            return False
        x = clamp(e.x, 0, self._total_width-1)
        y = clamp(e.y, 0, self._total_height-1)
        cell_row, cell_col = self._get_cell_id(Point(x,y))
        self.highlight_hover(cell_row, cell_col)
        selection_pos = Point(cell_col, cell_row)
        if self.is_mouse_selection_on:
            self._selection_move(selection_pos) 
        self.invalidate()
        return False

    def _selection_end(self):
        self._selection_backup = []
        if self.core_crucipixel:
            self.is_mouse_selection_on = False
#             print("Encode:")
#             for t in self._selection_core_encode:
#                 print("*",t)
            rows, cols = self.core_crucipixel.update(self._selection_core_encode)
#             print("Activate status:")
#             print(rows,cols)
            self.broadcast_lw_signal("activate-ver-status", rows)
            self.broadcast_lw_signal("activate-hor-status", cols)
        self._selection_core_encode = []

    def on_mouse_up(self, w, e):
        if self.is_mouse_selection_on:
            self.is_mouse_selection_on = False
            self._selection_end()
        self.is_dragging = False
        return False
    
    def is_point_in(self, p: Point, category=MouseEvent.UNKNOWN):
        print("Asking if I was in", category)
        if category == MouseEvent.MOUSE_MOVE and self.is_mouse_selection_on:
            return True
        else:
            return super().is_point_in(p,category)
    
    def highlight_hover(self, row,col):
        self._highlight_row = row
        self._highlight_col = col


def main() -> int:
    root = Root()
    main_window = MainWindow(title="Prova")
    main_window.add(root)

    crucipixel_scheme = parse_file_name("../data/monopattino.json")
    crucipixel_core = core.Crucipixel(
        len(crucipixel_scheme.rows),
        len(crucipixel_scheme.cols),
        crucipixel_scheme.rows,
        crucipixel_scheme.cols
    )

    grid = CrucipixelGrid(crucipixel_core, cell_width=15, cell_height=15)

    root.set_child(grid)

    main_window.start_main()

if __name__ == '__main__':
    main()
