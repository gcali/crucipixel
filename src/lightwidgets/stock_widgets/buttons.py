'''
Created on May 20, 2015

@author: giovanni
'''
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.geometrical import DrawableRoundedRectangle
from lightwidgets.support import rgb_to_gtk
from lightwidgets.events import MouseEvent

class Button(Widget):
    
    def __init__(self, label:"str", 
                 size_x:"int", size_y:"int", 
                 background_color=(150,150,150), 
                 label_color = (0,0,0),
                 **kwargs):
        super().__init__(**kwargs)
        self.size = Point(size_x, size_y)
        self.label = label
        self.background_color = background_color
        self.label_color = label_color
        self.force_clip_not_set = False
        self._button_mouse_was_down = False
        self._on_mouse_up_broadcast = None
    
    @property
    def _shape(self):
        return DrawableRoundedRectangle(Point(0,0),self.size.x,self.size.y)
    @property
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self, value):
        self._background_color = rgb_to_gtk(value)
    
    @property
    def label_color(self):
        return self._label_color
    
    @label_color.setter
    def label_color(self,value):
        self._label_color = rgb_to_gtk(value)
    
    @property
    def on_mouse_up_broadcast(self):
        return self._on_mouse_up_broadcast
    
    @on_mouse_up_broadcast.setter
    def on_mouse_up_broadcast(self,value):
        self._on_mouse_up_broadcast = value
    
    @on_mouse_up_broadcast.deleter
    def on_mouse_up_broadcast(self):
        self._on_mouse_up_broadcast = None

    def on_draw(self, w, c):
        super().on_draw(w, c)
        c.save()
        c.set_source_rgb(*self.background_color)
        self._shape.draw_on_context(c)
        c.fill()
        
        xb, yb, width, height, _, _ = c.text_extents(self.label)
        if (not self.force_clip_not_set) and not self.is_clip_set():
            self.clip_rectangle = self._shape
            
#         print(xb,yb,width,height)
        start_x = (self.size.x - width)/2 + xb
        start_y = (self.size.y - height)/2 - yb
#         print(start_x, start_y)
        c.move_to(start_x,start_y)
        c.set_source_rgb(*self.label_color)
        c.show_text(self.label)
        c.restore()
    
    def on_mouse_down(self, w, e):
        print("I've been called!")
        super().on_mouse_down(w, e)
        self._button_mouse_was_down = True
        print(self)
    
    def on_mouse_up(self, w, e):
        super().on_mouse_up(w,e)
        if not self.on_mouse_up_broadcast is None:
            self.broadcast_lw_signal(self.on_mouse_up_broadcast)
        self._button_mouse_was_down = False
    
    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        if category == MouseEvent.MOUSE_UP and self._button_mouse_was_down:
            return True
        return self._shape.is_point_in(p) 
