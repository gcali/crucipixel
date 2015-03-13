'''
Created on Feb 22, 2015

@author: giovanni
'''

import math
from gi.repository import Gtk,Gdk
from general.geometry import Point, Rectangle
import general.lightwidgets as lw
from general.support import get_from_to_inclusive, DefaultDict, clamp
from collections import OrderedDict
from general.lightwidgets import MouseEvent
from crucipixel import core

class CrucipixelGrid(lw.Widget):
    
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

    def __init__(self,cols=10,rows=10,
                 start=Point(0,0),
                 width=10,height=10,
                 crucipixel=None,
                 *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "CrucipixelWindow"

        self.cols=cols
        self.rows=rows
        self.cell_width=width
        self.cell_height=height
        self.is_mouse_down = False
        
        self.input_function_map = {"left" : "selected",
                                   "right" : "empty",
                                   "middle" : "default"}
        self.function_color_map = {"selected" : (0.3,0.3,0.3),
                                   "empty" : (1,1,1),
                                   "default" : (.8,.8,.8)}
        self.input_selection_style_map = {"1" : CrucipixelGrid.SELECTION_FREE,
                                          "2" : CrucipixelGrid.SELECTION_LINE,
                                          "3" : CrucipixelGrid.SELECTION_RECTANGLE}
        
        self.selection_style = CrucipixelGrid.SELECTION_RECTANGLE

        self.set_translate(start.x+.5,start.y+.5)
        self._selected_color_property = (0,0,0)
        self._selection_start = Point(0,0)
        self._selection_backup = []
        self._selection_memo = []
        self._cell_color = DefaultDict()
        self._cell_color.default = lambda: self.function_color_map["default"]
        self.core_crucipixel = crucipixel
        self.clip_rectangle = Rectangle(Point(-.5,-.5),self._total_height+1,self._total_width+1)

        def handle_select_color(name,value):
            self.input_function_map[name] = value
            print(name,value)
        self.register_signal("select_color",handle_select_color)
    
    def _color_from_function(self,function):
        return self.function_color_map[function]

    def _function_from_color(self,color):
        for (f,c) in self.function_color_map.items():
            if c == color:
                return f
        raise KeyError("No function has {} associated".format(color))

    @property
    def _selected_color(self):
        return self._selected_color_property 
    @_selected_color.setter
    def _selected_color(self,value):
        self._selected_color_property = value
        self._selected_function_property = \
            self._function_to_crucipixel_cell(self._function_from_color(value))
        
    @property
    def _selected_function(self):
        return self._selected_function_property 
    @_selected_function.setter
    def _selected_function(self,value):
        self._selected_function_property = value
        self._selected_color_property = self._crucipixel_to_color_cell(value)

    @property
    def _total_height(self):
        return self.rows * self.cell_height
    
    @property
    def _total_width(self):
        return self.cols * self.cell_width
    
    @property
    def core_crucipixel(self):
        return self._core_crucipixel
    
    @core_crucipixel.setter
    def core_crucipixel(self,value):
        self._core_crucipixel = value
        self.rows = value.rows
        self.cols = value.cols
        self.update_status_from_crucipixel()

    def _crucipixel_to_color_cell(self,cell):
        if cell == core.Crucipixel.EMPTY:
            return self.function_color_map["empty"]
        elif cell == core.Crucipixel.MAIN_SELECTED:
            return self.function_color_map["selected"]
        elif cell == core.Crucipixel.DEFAULT:
            return self.function_color_map["default"]
    
    def _function_to_crucipixel_cell(self,function):
        if function == "selected":
            return core.Crucipixel.MAIN_SELECTED
        elif function == "empty":
            return core.Crucipixel.EMPTY
        elif function == "default":
            return core.Crucipixel.DEFAULT
    
    def _color_to_crucipixel_cell(self,color):
        return self._function_to_crucipixel_cell(self._function_from_color(color))

    
    def update_status_from_crucipixel(self):
        for i in range(self.core_crucipixel.rows):
            for j in range(self.core_crucipixel.cols):
                self._cell_color[i,j] = self._crucipixel_to_color_cell(self._core_crucipixel[i,j])
                self.invalidate()
    
    def _force_update_crucipixel_from_status(self):
        """ Should never be called, the update should be allowed to 
            update the core data structure on its own
        """
        for i in range(self.rows):
            update_line = [(i,
                            j,
                            self._color_to_crucipixel_cell(self._cell_color[i,j]))\
                                for j in range(self.cols)]
            self.core_crucipixel.update(update_line)
                
    
    def on_draw(self,widget,context):
        context.save()
        context.set_line_width(1)
        width = self._total_width
        height= self._total_height

        for (k,v) in self._cell_color.items():
            context.set_source_rgb(*v)
            context.rectangle(k[0] * self.cell_width,
                        k[1] * self.cell_height,
                        self.cell_width,
                        self.cell_height)
            context.fill()
                        
        context.set_source_rgb(0,0,0)
        i=0
        for x in range(0,width+self.cell_width,self.cell_width):
            if i % 5 == 0:
                context.set_line_width(2)
            else:
                context.set_line_width(1)
            context.move_to(x,0)
            context.line_to(x,height)
            context.stroke() 
            i+=1

        i=0
        for y in range(0,height+self.cell_height,self.cell_height):
            if i % 5 == 0:
                context.set_line_width(2)
            else:
                context.set_line_width(1)
            context.move_to(0,y)
            context.line_to(width,y)
            context.stroke()
            i+=1
        
        context.move_to(0,0)
        context.line_to(-10,-10)
        context.stroke()
            

        context.restore()
    
    def _get_cell_id(self,pos:"Point") -> "(col,row)":
            cell_col = int(pos.x // self.cell_width)
            cell_row = int(pos.y // self.cell_height)
            return cell_col,cell_row
        
#     
    def on_mouse_down(self, w, e):
        if self.is_point_in(Point(e.x,e.y)):
            self.is_mouse_down = True
            cell_col,cell_row = self._get_cell_id(e)
            self._selection_start = Point(cell_col,cell_row)
            self._selected_color = self.function_color_map[\
                                                           self.input_function_map[e.button]\
                                                           ]
            self._select_rectangle(cell_col, cell_row)
            self.invalidate()
            return True
        else:
            return False
    
    def on_key_up(self, w, e):
        super().on_key_up(w,e)
        if e.key == "r":
            self.update_status_from_crucipixel()
            return True
        elif e.key == "f":
            self._force_update_crucipixel_from_status()
            return True
        try:
            self.selection_style = self.input_selection_style_map[e.key]
        except KeyError:
            pass
        return True
        
    def _restore_selection(self):
        for row, col, color in self._selection_backup:
            self._cell_color[row, col] = color


    def _select_rectangle(self, cell_col_end, cell_row_end):
        for c in get_from_to_inclusive(self._selection_start.col, cell_col_end):
            for r in get_from_to_inclusive(self._selection_start.row, cell_row_end):
                self._selection_backup.append((c, r, self._cell_color[c, r]))
                self._cell_color[c, r] = self._selected_color
                self._selection_memo.append((c,r,self._selected_function))

    def on_mouse_move(self, w, e):
        if self.is_mouse_down:
            x = clamp(e.x,0,self._total_width)
            y = clamp(e.y,0,self._total_height)
            cell_col,cell_row = self._get_cell_id(Point(x,y))
            self._selection_memo = []
            if self.selection_style == CrucipixelGrid.SELECTION_FREE:
                self._selection_backup = []
                self._selection_start = Point(cell_col,cell_row)
                self._select_rectangle(cell_col, cell_row)
            elif self.selection_style == CrucipixelGrid.SELECTION_LINE:
                self._restore_selection()
                self._selection_backup = []
                if cell_col == self._selection_start.col or\
                   cell_row == self._selection_start.row:
                    self._select_rectangle(cell_col, cell_row)
            elif self.selection_style == CrucipixelGrid.SELECTION_RECTANGLE:
                self._restore_selection()
                self._selection_backup = []
                self._select_rectangle(cell_col, cell_row)
                    
            self.invalidate()
        return False
    
    def on_mouse_up(self, w, e):
        if self.is_mouse_down:
            self.is_mouse_down = False
            self._selection_backup = []
            if self.core_crucipixel:
                self.core_crucipixel.update(self._selection_memo)
                pass
            self._selection_memo = []
        return False
    
    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        if category == MouseEvent.MOUSE_MOVE and self.is_mouse_down:
            return True
        else:
            return super().is_point_in(p,category)

class Selector(lw.Widget):
    
    def __init__(self,start=Point(0,0),options=None,*args,**kwargs):
        super().__init__(*args,**kwargs) 
        self.ID = "SelectorWindow"
        self.start = start
        self.padding = 5
        self.font_size = 20
        if options is None:
            self.options = OrderedDict(
                                [("Left",(0,0,0)),
                                 ("Right",(1,1,1)),
                                 ("Middle",(.8,.8,.8))])
        else:
            self.options = options
        self._total_height = 0
        self._total_width = 0
    
    
    @property
    def total_height(self):
        last_rectangle = self._get_rectangle_list(self.options.keys())[-1]
        return last_rectangle.start.y + last_rectangle.height + 2 #add line width
    @property
    def total_width(self):
        rectangle = self._get_rectangle_list(self.options.keys())[0]
        return rectangle.start.x + rectangle.width + self.padding + self.maxW
        
    def _get_rectangle_list(self,lines) -> "None//Raises: AttributeError":
        size = self._get_rectangle_size()
        return [Rectangle(Point(self.padding, 
                                self.padding*(1+i) + size* i),
                          size, 
                          size) for i in range(len(lines))]
    
    def _get_rectangle_size(self) -> "num//Raises: AttributeError":
        if not hasattr(self, "maxW") or not hasattr(self, "maxH"):
            raise AttributeError("Can't get cell_size until first drawn")
        return math.floor(self.maxH * .6) 

    def _get_text_max_size(self, context, lines):
        sizes = []
        for l in lines:
            xb, yb, width, height, _, _ = context.text_extents(l)
            sizes.append(Rectangle(Point(xb, yb), width, height))
        
        maxW, maxH = 0, 0
        for s in sizes:
            maxW = max(maxW, s.width - s.start.x)
            maxH = max(maxH, s.height - s.start.y)
        
        return maxH, maxW
    
    def on_mouse_down(self, w, e):
        new_colors = { "left" : "empty",
                       "right" : "selected",
                       "middle" : "default"}
        rectangle_list = self._get_rectangle_list(self.options.keys())
        r = 0
        found = False
        for i,rectangle in enumerate(rectangle_list):
            if rectangle.is_point_in(Point(e.x,e.y),delta=2):
                r=i
                found = True
                break
        if found:
            selected = (list(self.options.keys())[r]).lower()
            self.broadcast_lw_signal("select_color",selected,new_colors[selected])
            return True
        else:
            return False
    
    def is_point_in(self, p:"Point",category=MouseEvent.UNKNOWN):
        return p.x >= 0 and p.x <= self.total_width and\
               p.y >= 0 and p.y <= self.total_height

    def on_draw(self,widget,context):
        context.save()
#         context.select_font_face("sans-serif")
        context.set_font_size(self.font_size)
        context.set_line_width(1)
        lines = self.options.keys()
        maxH, maxW = self._get_text_max_size(context, lines)
        self.maxH = maxH
        self.maxW = maxW
        rectangle_size = self._get_rectangle_size()
        self._total_height = maxH
        self._total_width = self.padding * 2 + rectangle_size + maxW
        line_color_rectangle = zip(self.options.items(),self._get_rectangle_list(self.options.keys()))
        for (line,color),rectangle in line_color_rectangle:
            context.rectangle(rectangle.start.x,
                        rectangle.start.y,
                        rectangle.width,
                        rectangle.height)
            context.set_source_rgb(*color)
            context.fill_preserve()
            context.set_source_rgb(0,0,0)
            context.stroke()
            context.move_to(rectangle.start.x + rectangle.width + self.padding, 
                      math.floor(rectangle.start.y + rectangle.height * .9))
            context.show_text(line)
        context.restore()

class GuideCell:
    
    def __init__(self, coordinates:"(line,pos)",
                 cell:"Rectangle", text:"str"):
        self.cell = cell
        self.coordinates = coordinates
        self.text = text

class Guides(lw.Widget): 
    VERTICAL = 0
    HORIZONTAL = 1
    def __init__(self, elements:"num iterable", 
                 start:"Point", size:"num", orientation=HORIZONTAL): 
        super().__init__()
        self.translate(start.x +.5, start.y+.5)
        self.orientation = orientation
        self.elements = [ list(e) for e in elements ]
        self.cell_size = size
        self.height = 50
        self._number_height = None
        self._number_width = None
        self._cell_list_to_update = True
        self._cell_list = []
        if self.orientation == Guides.HORIZONTAL:
            self.clip_rectangle = Rectangle(Point(0,0),self.cell_size * len(self.elements),-self.height)
        else:
            self.clip_rectangle = Rectangle(Point(0,0),-self.height,self.cell_size * len(self.elements))
    
    def _update_cell_list(self):
        """Should be called only after on_draw has been called at least once"""
        self._cell_list = []
        for (line_index,number_list) in enumerate(self.elements): 
            line = self._line_coordinates(line_index)
            if self.orientation == Guides.HORIZONTAL:
                next_x = line[0].x - 3
                next_y = line[0].y - 5
            elif self.orientation == Guides.VERTICAL:
                next_x = line[0].x
                next_y = line[0].y - 5
            for (element_index, number) in enumerate(number_list):
                text = str(number)
                coordinates = (line_index,element_index)
                if self.orientation == Guides.HORIZONTAL:
                    width = self._number_width * len(text)
                    height = self._number_height + 5
                    rectangle = Rectangle(Point(next_x-width,next_y),
                                          width,
                                          -height)
                    next_y = next_y - height
                elif self.orientation == Guides.VERTICAL:
                    width = self._number_width * len(text) + 3
                    height = self._number_height
                    rectangle = Rectangle(Point(next_x - width,next_y),
                                          width,
                                          -height)
                    next_x -= width
                self._cell_list.append(GuideCell(coordinates=coordinates,
                                                cell=rectangle,
                                                text=text)
                                      ) 
        
    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        value= super().is_point_in(p,category)
        return value
    
    def on_mouse_down(self, w, e):
        p = Point(e.x,e.y)
        print("Point:",p)
        for e in self._cell_list:
            if e.cell.start.x == 71:
                print(e.cell)
                print(p)
                print(e.cell.is_point_in(p))
            if e.cell.is_point_in(p):
                return True

    def _line_coordinates(self,line_index):
        if self.orientation == Guides.HORIZONTAL:
            delta_x = (line_index + 1) * self.cell_size
            delta_y = -self.height
            return [Point(delta_x,0),Point(delta_x,delta_y)]
        elif self.orientation == Guides.VERTICAL:
            delta_x = -self.height
            delta_y = (line_index +1) * self.cell_size
            return [Point(0,delta_y),Point(delta_x,delta_y)]
        else:
            raise ValueError("Invalid orientation: {}".format(str(self.orientation)))
    
    def on_draw(self, widget, context):
        def draw_line(line):
            context.move_to(line[0].x,line[0].y)
            context.line_to(line[1].x,line[1].y)
            context.stroke()
        context.save()
        
        ext = context.text_extents("0")
        self._number_width = int(ext[0] + ext[2])
        self._number_height = -int(ext[1]) 
        if self._cell_list_to_update:
            self._update_cell_list()
        
        for e in self._cell_list:
            context.move_to(e.cell.start.x,
                            e.cell.start.y)
            context.show_text(e.text)

        for (i,e) in enumerate(self.elements):
            line = self._line_coordinates(i)
            if (i+1) % 5 == 0:
                context.set_line_width(2)
            else:
                context.set_line_width(1)
            draw_line(line)
        context.set_line_width(2)
        draw_line(self._line_coordinates(i+1))
        context.restore()

class CompleteCrucipixel(lw.UncheckedContainer):
    
    def __init__(self,
                 crucipixel,
                 start=Point(0,0),
                 cell_size=15, 
                 *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.translate(start.x,start.y)
        self.cell_size = cell_size
        self.rows = crucipixel.rows
        self.cols = crucipixel.cols
        self.grid = CrucipixelGrid.from_crucipixel(crucipixel=crucipixel, 
                                                   start=Point(0,0),
                                                   cell_size=cell_size)
        self.grid.selection_style = CrucipixelGrid.SELECTION_RECTANGLE
        self.add(self.grid)

        self.horizontal_guide = Guides(start=Point(0,0),
                                       elements=crucipixel.col_guides,
                                       size=cell_size,
                                       orientation=Guides.HORIZONTAL)
        self.horizontal_guide.ID="Horizontal Guide"
        self.add(self.horizontal_guide)
        
        self.vertical_guide=Guides(start=Point(0,0),
                                   elements=crucipixel.row_guides,
                                   size=cell_size,
                                   orientation=Guides.VERTICAL)
        self.vertical_guide.ID="Vertical Guide"
        self.add(self.vertical_guide)
    
class MainArea(lw.UncheckedContainer):
    
    def __init__(self):
        super().__init__()
        self.ID = "MainArea"
        self.core_crucipixel = None
        self.selector = None
        self._mouse_down = False
        self._click_point = Point(0,0)
        self.counter=0
    
    def start_selector(self,start=Point(0,0)):
        self.selector = Selector(start=start)
        self.selector.ID = "Selector"
        self.add(self.selector)
    
    def start_crucipixel(self,crucipixel:"core.CompleteCrucipixel",
                         start=Point(120,100),cell_size=20):
        self.core_crucipixel = CompleteCrucipixel(crucipixel, start, cell_size)
        self.core_crucipixel.ID="CompleteCrucipixel"
        self.add(self.core_crucipixel)
    
    def on_mouse_down(self, w, e):
        handled = super().on_mouse_down(w, e)
        if not handled:
            self._mouse_down = True
            self._click_point = Point(e.x,e.y)
            self._translate_vector = Point(self.core_crucipixel.fromWidgetCoords.transform_point(0,0))
    
    def on_mouse_move(self, w, e):
        if self._mouse_down:
            delta_x = int(e.x - self._click_point.x)
            delta_y = int(e.y - self._click_point.y)
            self.core_crucipixel.set_translate(self._translate_vector.x + delta_x,
                                          self._translate_vector.y + delta_y)
            self.invalidate()
        super().on_mouse_move(w,e)
    
    def on_mouse_up(self,w,e):
        if self._mouse_down:
            self._mouse_down = False
        super().on_mouse_up(w,e) 

if __name__ == '__main__':
    win = lw.MainWindow(title="CompleteCrucipixel Dev")
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.8,.8,.8,1))
    root = lw.Root(500,500)
    main_area = MainArea()
    root.set_child(main_area)
    cruci = core.Crucipixel(5,5,[[i+1] for i in range(5)],[[i+1] for i in range(5)])
    for i in range(5):
        for j in range(5):
            if i >= (4-j):
                cruci[i,j] = core.Crucipixel.MAIN_SELECTED
    main_area.start_selector()
    main_area.start_crucipixel(cruci)

    win.add(root)
    win.start_main()