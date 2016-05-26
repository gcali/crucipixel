'''
Created on May 20, 2015

@author: giovanni
'''
from numbers import Number
from typing import Callable, Tuple

import cairo
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.events import MouseEvent, KeyboardEvent, MouseEventCategory, \
    MouseButton, ScrollEvent


class Widget:
    
    NO_CLIP=None

    @property
    def is_shape_set(self) -> bool:
        return self._shape is not None

    @property
    def shape(self) -> Rectangle:
        if self._shape is not None:
            return self._shape
        elif self.father is not None:
            return self.father.shape
        else:
            return None

    @shape.setter
    def shape(self, rect: Rectangle):
        self._shape = rect

    def __init__(self, sizeX=0, sizeY=0, min_size=None):
        self.cell_size = (sizeX,sizeY)
        self.ID = "Widget"
        self.signals = {}

        self.visible = True
        self._shape = None
        self.is_focused = False

        self._fromTranslate = cairo.Matrix()
        self._fromRotate = cairo.Matrix()
        self._fromScale = cairo.Matrix()
        self._toTranslate = cairo.Matrix()
        self._toRotate = cairo.Matrix()
        self._toScale = cairo.Matrix()
        self._father = None
        self._clip_start = Widget.NO_CLIP
        self._clip_width = Widget.NO_CLIP
        self._clip_height = Widget.NO_CLIP
        self._mouse_is_in = False

        self.__prepare_to_click = None


        if min_size is not None:
            self._min_size = min_size
    
    def __str__(self):
        return str(self.ID)

    @property
    def min_size(self):
        return self._min_size
    
    @min_size.setter
    def min_size(self,value):
        self._min_size = value
        self.refresh_min_size()
    
    def refresh_min_size(self):
        try:
            self.father.update_min_size(self.min_size)
        except AttributeError:
            pass

    @property
    def mouse_is_in(self):
        return self._mouse_is_in
    
    @mouse_is_in.setter
    def mouse_is_in(self, value):
        if not self._mouse_is_in and value:
            self._mouse_is_in = True
            self.on_mouse_enter()
        elif self._mouse_is_in and not value:
            self._mouse_is_in = False
            self.on_mouse_exit()

    @property
    def mouse_is_down(self) -> bool:
        if self.father is None:
            return False
        else:
            return self.father.mouse_is_down
            

    @property
    def start(self):
        return Point(self.fromWidgetCoords.transform_point(0,0))
    
    @start.setter
    def start(self,value):
        self.set_translate(value.x+.5, value.y+.5)
    
    @property
    def father(self):
        return self._father
    
    @father.setter
    def father(self,value):
#         print(self,"Setting father to:", str(value))
        for signal in self.signals.keys():
#             print(self,"Adding signal {} to {}".format(signal,str(value)))
            value.register_signal_for_child(signal,self)
        self._father = value
        
    @property
    def container_size(self) -> Tuple[int, int]:
        if self.father is None:
            raise AttributeError
        size = self.father.container_size
        return size

    
    
    @property
    def fromWidgetCoords(self):
#         return self._fromRotate.multiply(self._fromTranslate.multiply(self._fromScale))
        return self._fromScale.multiply(self._fromTranslate.multiply(self._fromRotate))
        return self._fromScale.multiply(self._fromRotate.multiply(self._fromTranslate))
    
    @property
    def toWidgetCoords(self):
#         return self._toScale.multiply(self._toTranslate.multiply(self._toRotate))
        return self._toRotate.multiply(self._toTranslate.multiply(self._toScale))
        return self._toTranslate.multiply(self._toRotate.multiply(self._toScale))
    
    @property
    def allocated_size(self):
        if not self.father is None:
            return self.father.get_allocated_size(self)
    
    def rotate(self,angle):
        self._fromRotate.rotate(angle)
        self._toRotate.rotate(-angle)
    
    def translate(self,x,y):
        self._fromTranslate.translate(x,y)
        self._toTranslate.translate(-x,-y)
    
    def set_translate(self,x,y):
        self._fromTranslate = cairo.Matrix()
        self._toTranslate = cairo.Matrix()
        self.translate(x,y)

    def scale(self,x,y):
        if x == 0 or y == 0:
            raise ValueError("Cannot scale by 0") 
        self._fromScale.scale(x,y)
        self._toScale.scale(1/x,1/y)

    def set_scale(self, x: Number, y: Number):
        self._fromScale = cairo.Matrix()
        self._toScale = cairo.Matrix()
        self.scale(x, y)

    def layout(self, context: cairo.Context):
        pass

    def is_clip_set(self):
        return not (self._clip_start is None)
    
    @property
    def clip_rectangle(self):
        if not self.is_clip_set():
            raise AttributeError("Clip rectangle not set")
        return Rectangle(self._clip_start,self._clip_width,self._clip_height)
    @clip_rectangle.setter
    def clip_rectangle(self,value):
        if value is None:
            self._clip_start = None
        else:
            self._clip_start = value.start
            self._clip_width = value.width
            self._clip_height = value.height

    def get_vertexes(self):
        return [self._clip_start,
                self._clip_start + Point(self._clip_width,0),
                self._clip_start + Point(0,self._clip_height)] 
    
    def get_vertexes_father_coordinates(self):
        return map(self.fromWidgetCoords.transform_point,self.get_vertexes())

    def on_draw(self, widget: "Widget", context: cairo.Context) -> None:
        pass
    
    def on_mouse_exit(self) -> bool:
        return False
    
    def on_mouse_enter(self) -> bool:
        return True
    
    def on_mouse_move(self, widget: "Widget", event: MouseEvent) -> bool:
        return False

    def on_mouse_down(self, widget: "Widget", event: MouseEvent) -> bool:
        self.__prepare_to_click = event.button
        return True
    
    def on_mouse_up(self, widget: "Widget", event: MouseEvent) -> bool:
        if self.__prepare_to_click == event.button:
            if self.is_point_in(event):
                self.is_focused = True
                self.on_click(widget, event.button)
            else:
                self.is_focused = False
            self.__prepare_to_click = None
        else:
            self.is_focused = False
        return False

    def on_scroll(self, event: ScrollEvent) -> bool:
        return False
    
    def on_key_down(self, widget: "Widget", event: KeyboardEvent) -> bool:
        return False

    def on_key_up(self, widget: "Widget", event: KeyboardEvent) -> bool:
        return False
    
    def on_resize(self, new_father_dim) -> None:
        return
    
    def is_point_in(self,p: Point, category=MouseEvent.UNKNOWN) -> bool:
        if self.shape is not None:
            return self.shape.is_point_in(p)
        elif not self.is_clip_set():
            return False
        else:
            return self.clip_rectangle.is_point_in(p)

    def on_click(self, widget: "Widget", button: MouseButton) -> None:
        pass
    
    def invalidate(self):
        if self.father:
            self.father.invalidate()
    
    def register_signal(self,signal_name:"str",callback:"function"):
        try:
            self.signals[signal_name].append(callback)
#             print(self,"I've been succesfully added")
        except KeyError:
            self.signals[signal_name] = []
            return self.register_signal(signal_name, callback)
        if self.father:
#             print(self, "Father was:",str(self.father))
            self.father.register_signal_for_child(signal_name,self)
    
    def handle_signal(self,signal_name,*args):
        try:
            for callback in self.signals[signal_name]:
                callback(*args)
        except KeyError:
            pass
#             print("No signal {} registered to {}".format(signal_name,self.ID),file=stderr)
    
    def broadcast_lw_signal(self,signal_name,*args):
        return self.father.broadcast_lw_signal(signal_name,*args)
    
    def emit_lw_signal(self,dest:"Widget",signal_name,*args):
        dest.handle_signal(signal_name,*args)
