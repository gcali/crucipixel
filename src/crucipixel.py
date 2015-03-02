'''
Created on Feb 22, 2015

@author: giovanni
'''

from gi.repository import Gtk,Gdk
from geometry import Point, Rectangle
import lightwidgets as lw
from support import get_from_to_inclusive
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
        self._cell_color = {}
        self.clip_rectangle = Rectangle(Point(0,0),self._total_height,self._total_width)
        print(self.clip_rectangle)

        def handle_hi():
            print("Hi! I've been called by a signal!")
        self.register_signal("hi", handle_hi)
    
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
                self._selection_backup.append((c, r, self._cell_color.get((c, r), (.8, .8, .8))))
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
        if options is None:
            self.options = OrderedDict(
                                [("Left",(0,0,0)),
                                 ("Right",(1,1,1)),
                                 ("Middle",(.8,.8,.8))])
        else:
            self.options = options
    
    
    def on_mouse_down(self, w, e):
        super().on_mouse_down(w,e)

    
    
    def on_draw(self,w,c):
        c.save()
        c.rectangle(0,0,100,80)
        c.stroke()
        padding = 5
        size = 20
        start = size + padding
        c.select_font_face("sans-serif")
        c.set_font_size(size)
        c.set_line_width(1)
        for line,color in self.options.items():
            c.rectangle(padding,start,size,-size)
            c.set_source_rgb(*color)
            c.fill_preserve()
            c.set_source_rgb(0,0,0)
            c.stroke()
            c.move_to(padding + size + padding,start)
            print(c.text_extents(line))
            c.show_text(line)
            start += size + padding
        c.restore()
        print("Hi! I'm a nice selector!")
    

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