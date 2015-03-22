'''
Created on Feb 22, 2015

@author: giovanni
'''

import math
import cairo
from gi.repository import Gtk,Gdk
from general.geometry import Point, Rectangle
import general.lightwidgets as lw
from general.support import get_from_to_inclusive, DefaultDict, clamp,\
                            rgb_to_gtk
from collections import OrderedDict
from general.lightwidgets import MouseEvent
from crucipixel import core

_start_selected = (.3,.3,.3)
_start_default = (.8,.8,.8)
_start_empty = rgb_to_gtk((240,255,240))
_highlight = rgb_to_gtk((0,250,154))
_highlight = rgb_to_gtk((210,105,30))
_highlight = rgb_to_gtk((186,85,211))
_highlight = rgb_to_gtk(95,158,160)

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
        self.function_color_map = {"selected" : _start_selected,
                                   "empty" : _start_empty,
                                   "default" : _start_default}
        self.input_selection_style_map = {"1" : CrucipixelGrid.SELECTION_FREE,
                                          "2" : CrucipixelGrid.SELECTION_LINE,
                                          "3" : CrucipixelGrid.SELECTION_RECTANGLE}
        
        self.selection_style = CrucipixelGrid.SELECTION_RECTANGLE

        self.set_translate(start.x+.5,start.y+.5)
        self._selected_function_property = "selected"
        self._selection_start = Point(0,0)
        self._selection_backup = []
        self._selection_core_encode = []
        self._cell_function = DefaultDict()
        self._cell_function.default = lambda: "default"
        self._highlight_row = None
        self._highlight_col = None
        self.core_crucipixel = crucipixel
        self.clip_rectangle = Rectangle(Point(-.5,-.5),self._total_height+1,self._total_width+1)

        def handle_select_color(name,value):
            self.input_function_map[name] = value
            print(name,value)
        self.register_signal("select_color",handle_select_color)
    
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
                self._cell_function[i,j] = self._crucipixel_to_function_cell(self._core_crucipixel[i,j])
                self.invalidate()
    
    def on_draw(self,widget,context):
        
        def highlight_rectangles(row,col):
            width = self._total_width
            height = self._total_height
            
            row_rectangle = Rectangle(Point(0,row * self.cell_height),
                                      width,
                                      self.cell_height)
            col_rectangle = Rectangle(Point(col * self.cell_width,0),
                                      self.cell_width,
                                      height)
            context.save()
            r,g,b = _highlight
            context.set_source_rgba(r,g,b,.3)
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
        height= self._total_height
        
        def draw_cell(function:"cell_function",area:"Rectangle"):
            r,g,b = self._function_to_color(function)
            context.set_source_rgb(r,g,b)
            context.rectangle(area.start.x,
                              area.start.y,
                              area.width,
                              area.height)
            context.fill()
            if function == "empty":
                r,g,b = self._function_to_color("selected")
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
                

        for (k,v) in self._cell_function.items():
            rectangle = Rectangle(Point(k[0] * self.cell_width,
                                        k[1] * self.cell_height),
                                  self.cell_width,
                                  self.cell_height)
            draw_cell(v,rectangle)
                        
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
        
        if self._highlight_col is not None and\
           self._highlight_row is not None:
            highlight_rectangles(self._highlight_row,
                                 self._highlight_col)

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
            self._selected_function = self.input_function_map[e.button]
            self._select_rectangle(cell_col, cell_row)
            self.invalidate()
            return True
        else:
            return False
    
    def on_mouse_exit(self):
        super().on_mouse_exit()
        self._highlight_col = None
        self._highlight_row = None
        self.invalidate()
    
    def on_key_up(self, w, e):
        super().on_key_up(w,e)
        if e.key == "r":
            self.update_status_from_crucipixel()
            return True
        try:
            self.selection_style = self.input_selection_style_map[e.key]
        except KeyError:
            pass
        return True
        
    def _restore_selection(self):
        for row, col, color in self._selection_backup:
            self._cell_function[row, col] = color


    def _select_rectangle(self, cell_col_end, cell_row_end):
        for c in get_from_to_inclusive(self._selection_start.col, cell_col_end):
            for r in get_from_to_inclusive(self._selection_start.row, cell_row_end):
                self._selection_backup.append((c, r, self._cell_function[c, r]))
                self._cell_function[c, r] = self._selected_function
                self._selection_core_encode.append((c,r,self._selected_core_function))

    def on_mouse_move(self, w, e):
        x = clamp(e.x,0,self._total_width-1)
        y = clamp(e.y,0,self._total_height-1)
        cell_col,cell_row = self._get_cell_id(Point(x,y))
        self.highlight_hover(cell_row,cell_col)
        if self.is_mouse_down:
            self._selection_core_encode = []
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
                self.core_crucipixel.update(self._selection_core_encode)
            self._selection_core_encode = []
        return False
    
    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        if category == MouseEvent.MOUSE_MOVE and self.is_mouse_down:
            return True
        else:
            return super().is_point_in(p,category)
    
    def highlight_hover(self, row,col):
        self._highlight_row = row
        self._highlight_col = col

class Selector(lw.Widget):
    
    def __init__(self,start=Point(0,0),options=None,*args,**kwargs):
        super().__init__(*args,**kwargs) 
        self.ID = "SelectorWindow"
        self.start = start
        self.padding = 5
        self.font_size = 20
        if options is None:
            self.options = OrderedDict(
                                [("Left",(.4,.4,.4)),
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
                 cell:"Rectangle", text:"str",wide_cell=None):
        self.cell = cell
        self.coordinates = coordinates
        self.text = text
        self.wide_cell=wide_cell

class GuideElement:
    
    def __init__(self, coordinates:"(line,pos)",
                 value:"num", 
                 done:"bool"=False,
                 wrong:"bool"=False,
                 cancelled:"bool"=False,
                 cell:"Rectangle"=None,
                 wide_cell:"Rectangle"=None):
        self.coordinates = coordinates
        self.value = value
        self.done = done
        self.wrong = wrong
        self.cancelled = cancelled 
        self.cell = cell
        self.wide_cell = wide_cell
    
    @property
    def text(self):
        return str(self.value)
        

class Guides(lw.Widget): 
    VERTICAL = 0
    HORIZONTAL = 1
    
    @staticmethod
    def _elements_from_list(elements):
        new_elements = []
        for line_index,line in enumerate(elements):
            new_line = []
            for position,e in enumerate(line):
                new_e = GuideElement(coordinates=(line_index,position),
                                     value=e)
                if line_index == 1:
                    new_e.wrong = True
                elif line_index == 4:
                    new_e.done = True
                new_line.append(new_e)
            new_elements.append(new_line)
        return new_elements

    def __init__(self, elements:"num iterable", 
                 start:"Point", size:"num", orientation=HORIZONTAL): 
        super().__init__()
        self.translate(start.x +.5, start.y+.5)
        self.orientation = orientation
        self.elements = Guides._elements_from_list([ list(e) for e in elements ])
        self.cell_size = size
        self.height = 50
        self.width=self.height
        self.font_size = 13
        self._number_height = None
        self._number_width = None
        self._cell_list_to_update = True
        self._cell_list = []
        if self.orientation == Guides.HORIZONTAL:
            self.clip_rectangle = Rectangle(Point(0,0),self.cell_size * len(self.elements)+.5,-self.height)
        else:
            self.clip_rectangle = Rectangle(Point(0,0),-self.width,self.cell_size * len(self.elements)+.5)
        self.color_map = {
            "done" : rgb_to_gtk(46,139,87),
            "wrong" : rgb_to_gtk(178,34,34),
            "cancelled" : rgb_to_gtk(139,134,130)
            }

        
    def _update_cell_list(self):
        """Should be called only after on_draw has been called at least once"""
        self._cell_list = []
        for (line_index,element_list) in enumerate(self.elements): 
            line = self._line_coordinates(line_index)
            if self.orientation == Guides.HORIZONTAL:
                next_x = line[0].x - self.font_size//2
                next_y = line[0].y - (2*self.font_size)//3
            elif self.orientation == Guides.VERTICAL:
                next_x = line[0].x - self.font_size//3
                next_y = line[0].y - self.font_size//2
            for element in element_list:
                text = str(element.value)
                if self.orientation == Guides.HORIZONTAL:
                    width = self._number_width * len(text)
                    height = self._number_height
                    rectangle = Rectangle(Point(next_x-width,next_y),
                                          width,
                                          -height)
                    wide_rectangle = Rectangle(Point(line[0].x,next_y),
                                               -self.cell_size,
                                               -height)
                    next_y = next_y - height - self.font_size//2
                elif self.orientation == Guides.VERTICAL:
                    width = self._number_width * len(text)
                    height = self._number_height
                    rectangle = Rectangle(Point(next_x - width,next_y),
                                          width,
                                          -height)
                    wide_rectangle = Rectangle(Point(next_x - width,line[0].y),
                                               width,
                                               -self.cell_size)
                    next_x -= width + self.font_size//2
                element.cell = rectangle
                element.wide_cell = wide_rectangle
        
    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        value= super().is_point_in(p,category)
        return value
    
    def on_mouse_down(self, w, e):
        p = Point(e.x,e.y)
        print("Point:",p)
        for line in self.elements:
            for e in line:
                if e.wide_cell.is_point_in(p):
                    print("I was in!")
                    print("Old value: {}".format(e.cancelled))
                    e.cancelled = not e.cancelled
                    self.invalidate()
                    return True
                elif e.coordinates == (0,0):
                    print("I wasn't in, why?")
                    print(e.wide_cell)

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
    

    def _draw_element(self, context, e):
        context.save()
        if e.done:
            context.set_source_rgb(*self.color_map["done"])
        elif e.wrong:
            context.set_source_rgb(*self.color_map["wrong"])
        elif e.cancelled:
            context.set_source_rgb(*self.color_map["cancelled"])
        context.move_to(e.cell.start.x, e.cell.start.y)
        context.show_text(e.text)
        if e.cancelled:
            context.move_to(e.cell.start.x-1,e.cell.start.y)
            context.line_to(e.cell.start.x + e.cell.width + 1,
                            e.cell.start.y + e.cell.height+1)
            context.stroke()
        context.restore()

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
            self._cell_list_to_update = False
        
        for (i,e) in enumerate(self.elements):
            line = self._line_coordinates(i)
            if (i+1) % 5 == 0:
                context.set_line_width(2)
            else:
                context.set_line_width(1)
            draw_line(line)
        context.set_line_width(2)
        draw_line(self._line_coordinates(i+1))

        context.set_line_width(1)
        context.set_font_size(self.font_size)
        for line in self.elements:
            for e in line:
                self._draw_element(context, e)

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
        self._current_scale = Point(1,1)
    
    def _update_scale(self):
        self.scale(self._current_scale.x,self._current_scale.y)
        self.invalidate()
    
    def on_key_down(self, w, e):
        if e.key == "=" or e.key == "+":
            self.zoom_in()
            return True
        elif e.key == "-":
            self.zoom_out()
            return True
        else:
            super().on_key_down(w,e)

    def zoom_in(self):
        self.scale(1.5,1.5)
        self.invalidate()
    
    def zoom_out(self):
        self.scale((1/1.5),(1/1.5))
        self.invalidate()
    
    def on_mouse_enter(self):
        super().on_mouse_enter()
        
    def on_mouse_exit(self):
        return super().on_mouse_exit()
        
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
    hor_elements = "1,2;2,2;3;4;5"
    ver_elements = "1,2;2,12;3;4;5"
    cruci = core.Crucipixel.guides_from_strings(5, 5, hor_elements, ver_elements)
    for i in range(5):
        for j in range(5):
            if i >= (4-j):
                cruci[i,j] = core.Crucipixel.MAIN_SELECTED
    main_area.start_crucipixel(cruci)
    main_area.start_selector()

    win.add(root)
    root.grab_focus()
    win.start_main()