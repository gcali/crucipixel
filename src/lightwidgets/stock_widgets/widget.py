'''
Created on May 20, 2015

@author: giovanni
'''
import cairo
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.events import MouseEvent

class Widget:
    
    NO_CLIP=None

    def __init__(self, sizeX=0, sizeY=0, min_size=None):
        self.cell_size = (sizeX,sizeY)
        self.ID = "Widget"
        self.signals = {} 

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
        
        if not min_size is None:
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
            self.father.update_min_size(self,self.min_size)
        except AttributeError:
            pass

    @property
    def mouse_is_in(self):
        return self._mouse_is_in
    
    @mouse_is_in.setter
    def mouse_is_in(self,value):
        if not self._mouse_is_in and value:
            self._mouse_is_in = True
            self.on_mouse_enter()
        elif self._mouse_is_in and not value:
            self._mouse_is_in= False
            self.on_mouse_exit()
            

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
    def container_size(self):
        if self.father is None:
            raise AttributeError
        return self.father.container_size
    
    
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
            print("Setting!")
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

    def on_draw(self,w,c):
        pass
    
    def on_mouse_exit(self):
        return False
    
    def on_mouse_enter(self):
        return True
    
    def on_mouse_move(self,widget,event):
        self._mouse_was_in = True
        return False
    
    def on_mouse_down(self,w,e):
        return False
    
    def on_mouse_up(self,w,e):
        return False
    
    def on_key_down(self,w,e):
        return False
    
    def on_key_up(self,w,e):
        return False
    
    def on_resize(self,new_father_dim):
        return
    
    def is_point_in(self,p:"Point",category=MouseEvent.UNKNOWN):
        if category == MouseEvent.MOUSE_UP:
            return True
        elif not self.is_clip_set():
            return False
        else:
            return self.clip_rectangle.is_point_in(p)
    
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
