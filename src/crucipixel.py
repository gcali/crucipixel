'''
Created on Feb 22, 2015

@author: giovanni
'''

import math
from gi.repository import Gtk,Gdk
from geometry import Point, Rectangle
import lightwidgets as lw
from support import get_from_to_inclusive, DefaultDict
from collections import OrderedDict

class Grid(lw.Widget):
    
    SELECTION_FREE = 0
    SELECTION_LINE = 1
    SELECTION_RECTANGLE = 2
    def __init__(self,cols=10,rows=10,
                 start=Point(0,0),
                 width=10,height=10,
                 *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "CrucipixelWindow"

        self.cols=cols
        self.rows=rows
        self.cell_width=width
        self.cell_height=height
        self.is_mouse_down = False
        
        self.color_associations = {"left" : (0,0,0),
                                   "right" : (1,1,1),
                                   "middle" : (.8,.8,.8)}
        
        self.selection_style = Grid.SELECTION_RECTANGLE

        self.set_translate(start.x+.5,start.y+.5)
        self._selected_color = (0,0,0)
        self._selection_start = Point(0,0)
        self._selection_backup = []
        self._cell_color = DefaultDict()
        self._cell_color.default = self.color_associations["middle"]
        self.clip_rectangle = Rectangle(Point(0,0),self._total_height,self._total_width)
        #print(self.clip_rectangle)

        def handle_hi():
            print("Hi! I've been called by a signal!")
        def handle_select_color(name,value):
            print(name,value)
        self.register_signal("hi", handle_hi)
        self.register_signal("select_color",handle_select_color)
    
    @property
    def _total_height(self):
        return self.rows * self.cell_height
    
    @property
    def _total_width(self):
        return self.cols * self.cell_width
    
    def on_draw(self,w,c):
        c.save()
        c.set_line_width(1)
        c.set_source_rgb(0,0,0)
        width = self._total_width
        height= self._total_height
        for x in range(0,width+self.cell_width,self.cell_width):
            c.move_to(x,0)
            c.line_to(x,height)
            c.stroke() 

        for y in range(0,height+self.cell_height,self.cell_height):
            c.move_to(0,y)
            c.line_to(width,y)
            c.stroke()
        
        c.move_to(0,0)
        c.line_to(-10,-10)
        c.stroke()
            
        for (k,v) in self._cell_color.items():
            c.set_source_rgb(*v)
            c.rectangle(k[0] * self.cell_width + 2,
                        k[1] * self.cell_height + 2,
                        self.cell_width - 4,
                        self.cell_height - 4)
            c.fill()
                        

        c.restore()
    
    def _get_cell_id(self,pos:"Point") -> "(col,row)":
            cell_col = int(pos.x // self.cell_width)
            cell_row = int(pos.y // self.cell_height)
            return cell_col,cell_row
        
#     
    def on_mouse_down(self, w, e):
        self.broadcast_lw_signal("hi")
        if self.is_point_in(Point(e.x,e.y)):
            self.is_mouse_down = True
            cell_col,cell_row = self._get_cell_id(e)
            self._selection_start = Point(cell_col,cell_row)
            try:
                self._selected_color = self.color_associations[e.button]
            except KeyError:
                pass
            self._cell_color[(cell_col,cell_row)] = self._selected_color
            self.invalidate()
            return True
        else:
            return False
        
    def _restore_selection(self):
        for row, col, color in self._selection_backup:
            self._cell_color[row, col] = color


    def _select_rectangle(self, cell_col_end, cell_row_end):
        for c in get_from_to_inclusive(self._selection_start.col, cell_col_end):
            for r in get_from_to_inclusive(self._selection_start.row, cell_row_end):
#                 self._selection_backup.append((c, r, self._cell_color.get((c, r), (.8, .8, .8))))
                self._selection_backup.append((c, r, self._cell_color[c, r]))
                self._cell_color[c, r] = self._selected_color

    def on_mouse_move(self, w, e):
        if self.is_mouse_down and self.is_point_in(Point(e.x,e.y)):
            #TODO Clamp e.x,e.y in width and height
            cell_col,cell_row = self._get_cell_id(e)
            if self.selection_style == Grid.SELECTION_FREE:
                self._cell_color[cell_col,cell_row] = self._selected_color
            elif self.selection_style == Grid.SELECTION_LINE:
                self._restore_selection()
                self._selection_backup = []
                if cell_col == self._selection_start.col or\
                   cell_row == self._selection_start.row:
                    self._select_rectangle(cell_col, cell_row)
            elif self.selection_style == Grid.SELECTION_RECTANGLE:
                self._restore_selection()
                self._selection_backup = []
                self._select_rectangle(cell_col, cell_row)
                    
            self.invalidate()
            return True
        else:
            return False
    
    def on_mouse_up(self, w, e):
        if self.is_mouse_down:
            self.is_mouse_down = False
            self._selection_backup = []
        return False
    
    def is_point_in(self, p:"Point"):
        return (p.x >= 0 and p.x <= self.cols * self.cell_width) and\
               (p.y >= 0 and p.y <= self.rows * self.cell_height)

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
            raise AttributeError("Can't get size until first drawn")
        return math.floor(self.maxH * .6) 

    def _get_text_max_size(self, context, lines):
        sizes = []
        for l in lines:
            xb, yb, width, height, _, _ = context.text_extents(l)
            sizes.append(Rectangle(Point(xb, yb), width, height))
        
        maxW, maxH = 0, 0
        for s in sizes:
#             print(s)
            maxW = max(maxW, s.width - s.start.x)
            maxH = max(maxH, s.height - s.start.y)
        
        return maxH, maxW
    
    def on_mouse_down(self, w, e):
        rectangle_list = self._get_rectangle_list(self.options.keys())
        r = 0
        found = False
        for i,rectangle in enumerate(rectangle_list):
            if rectangle.is_point_in(Point(e.x,e.y),delta=2):
                r=i
                found = True
        if found:
            selected = list(self.options.keys())[r]
            self.broadcast_lw_signal("select_color",selected,None)
        return True
    
    def is_point_in(self, p:"Point"):
#         print(p,self.total_width,self.total_height)
        return p.x >= 0 and p.x <= self.total_width and\
               p.y >= 0 and p.y <= self.total_height

    def on_draw(self,w,c):
        c.save()
        c.select_font_face("sans-serif")
        c.set_font_size(self.font_size)
        c.set_line_width(1)
        lines = self.options.keys()
        maxH, maxW = self._get_text_max_size(c, lines)
        self.maxH = maxH
        self.maxW = maxW
        rectangle_size = self._get_rectangle_size()
        self._total_height = maxH
        self._total_width = self.padding * 2 + rectangle_size + maxW
        line_color_rectangle = zip(self.options.items(),self._get_rectangle_list(self.options.keys()))
        for (line,color),rectangle in line_color_rectangle:
            c.rectangle(rectangle.start.x,
                        rectangle.start.y,
                        rectangle.width,
                        rectangle.height)
            c.set_source_rgb(*color)
            c.fill_preserve()
            c.set_source_rgb(0,0,0)
            c.stroke()
            c.move_to(rectangle.start.x + rectangle.width + self.padding, 
                      math.floor(rectangle.start.y + rectangle.height * .9))
            c.show_text(line)
        c.restore()
    

if __name__ == '__main__':
    win = lw.MainWindow(title="Crucipixel Dev")
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.8,.8,.8,1))
    root = lw.Root(500,500)
    simple_container = lw.UncheckedContainer()
    simple_container.ID = "SimpleContainer"
    cruci = Grid(start=Point(80,80),cols=30,rows=30,width=20,height=20)
    selector = Selector()
    simple_container.add(selector)
    simple_container.add(cruci)
    root.set_child(simple_container)

    win.add(root)
    win.start_main()