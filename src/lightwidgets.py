'''
Created on Feb 18, 2015

@author: giovanni
'''

from gi.repository import Gtk
from gi.repository.Gdk import EventMask
import cairo
from math import pi,sqrt
from geometry import Point
from _operator import pos

def _transform_event(event_type,e,w):
    x,y=w.toWidgetCoords.transform_point(e.x,e.y)
    new_e = MouseEvent(event_type,x,y)
    try:
        if e.button == 1:
            new_e.button = "left"
        elif e.button == 2:
            new_e.button = "middle"
        elif e.button == 3:
            new_e.button = "right"
    except AttributeError:
        pass 
    return new_e

class MouseEvent:
    
    def __init__(self, event_type, x, y, button=None):
        self.x = x
        self.y = y
        self.event_type = event_type
        self.button = button

class Root(Gtk.DrawingArea):
    
    def __init__(self, width=-1,height=-1,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.child = None
        events = EventMask.BUTTON_PRESS_MASK | EventMask.BUTTON_RELEASE_MASK | EventMask.POINTER_MOTION_MASK
        self.add_events(events)
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_mouse_down)
        self.connect("button-release-event", self.on_mouse_up)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.set_min_size(width,height)
        
    def set_min_size(self, sizeX:"num", sizeY:"num"):
        self.set_size_request(sizeX, sizeY)
    
    def set_child(self, child:"Widget"):
        self.child = child
        child.father = self
    
    def on_draw(self, widget:"Widget", context:"cairo.Context"):
        context.save()
        context.transform(self.child.fromWidgetCoords)
        self.child.clip_path(context)
        self.child.on_draw(self,context)
        context.restore()
    
    def _transform_event(self,event_type,e):
        return _transform_event(event_type,e,self.child)
    
    def on_mouse_down(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self.child.on_mouse_down(self,self._transform_event("mouse_down",e))
        return True
    
    def on_mouse_up(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self.child.on_mouse_up(self,self._transform_event("mouse_up", e))
        return True

    def on_mouse_move(self,w:"Gtk.Widget",e:"Gdk.EventMotion"):
        self.child.on_mouse_move(self,self._transform_event("mouse_move",e))
        return True
    
    def invalidate(self):
        self.queue_draw()

class Widget:

    def __init__(self, sizeX=0, sizeY=0):
        self.size = (sizeX,sizeY)
        self._fromTranslate = cairo.Matrix()
        self._fromRotate = cairo.Matrix()
        self._fromScale = cairo.Matrix()
        self._toTranslate = cairo.Matrix()
        self._toRotate = cairo.Matrix()
        self._toScale = cairo.Matrix()
        self.ID = "Widget"
    
    def __str__(self):
        return self.ID
    
    @property
    def fromWidgetCoords(self):
        #return self._fromScale.multiply(self._fromRotate.multiply(self._fromTranslate))
        return self._fromRotate.multiply(self._fromTranslate.multiply(self._fromScale))
    
    @property
    def toWidgetCoords(self):
        #return self._toTranslate.multiply(self._toRotate.multiply(self._toScale))
        return self._toScale.multiply(self._toTranslate.multiply(self._toRotate))
    
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

    def clip_path(self,c):
        pass
    
    def on_draw(self,w,c):
        pass
    
    def on_mouse_move(self,w,e):
        return False
    
    def on_mouse_down(self,w,e):
        return False
    
    def on_mouse_up(self,w,e):
        return False
    
    def is_point_in(self,p:"Point"):
        return False
    
    def invalidate(self):
        self.father.invalidate()


class Circle(Widget):
    
    def __init__(self, radius):
        super().__init__(2*radius,2*radius)
        self.radius = radius
        self.ID = "Circle"
    
    def on_draw(self,w,c):
        c.set_source_rgb(0.5,0,0.4)
        c.arc(self.radius,self.radius,self.radius,0,2*pi)
        c.stroke()
    
class Line(Widget):
    
    def __init__(self, startP, endP):
        super().__init__(endP.y,endP.x)
        self.startP = startP
        self.endP = endP
        self.ID = "Line"
    
    def on_draw(self,w,c):
        c.set_line_width(3)
        c.set_source_rgb(0.5,0,0.4)
        c.move_to(self.startP.x,self.startP.y)
        c.line_to(self.endP.x,self.endP.y)
        c.stroke()
    
    def clip_path(self,c):
        width=self.endP.y - self.startP.y
        height=self.endP.x - self.startP.x
        c.rectangle(self.startP.x, self.startP.y,width,height)
        c.clip()
        print(self,c.clip_extents())

class Donut(Widget):
    
    def __init__(self, centerP, inner, outer,iters=36):
        super().__init__(outer*2, outer*2)
        self._centerP = Point(0,0)
        self.centerP = centerP
        self.inner = inner
        self.outer = outer
        self.iters = iters
        self.selected = False
        self.ID = "Donut"
    
    def on_draw(self,w,c):
        for i in range(self.iters):
            c.save()
            c.rotate(i*pi/self.iters)
            c.scale(1,self.inner/self.outer)
            c.arc(0,0,self.outer,0,2*pi)
            c.stroke() 
            c.restore()
    
    @property
    def centerP(self):
        return self._centerP

    @centerP.setter
    def centerP(self,value):
        self._centerP= value + self.centerP
        self.translate(value.x,value.y)
        #self.translate(deltaX,deltaY)
    
    def is_point_in(self, p:"Point"):
        isInExtern = (sqrt(p.x*p.x + p.y*p.y) <= self.outer)
        isInIntern = (sqrt(p.x*p.x + p.y*p.y) <= self.inner)
        return isInExtern and not isInIntern
    
    def on_mouse_down(self,w,e):
        p = Point(e.x,e.y)
        if self.is_point_in(p):
            self.selected = True 
            self._deltaP = p
            return True
        else:
            return False
    
    def on_mouse_up(self,w,e):
        self.selected = False
        self._deltaP = None
        return True
    
    def on_mouse_move(self,w,e):
        if self.selected:
            self.centerP =  Point(e.x,e.y) - self._deltaP
            w.queue_draw()
        return True

class Container(Widget):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "Container"
    
    @property
    def list(self):
        raise NotImplementedError()
    
    def add(self,widget) -> "id":
        raise NotImplementedError()
    
    def remove_obj(self,widget):
        raise NotImplementedError()
    
    def remove_id(self,id_v:"id"):
        raise NotImplementedError()
    
    def on_draw(self,w,c):
        for child in self.list:
            c.save()
            c.transform(child.fromWidgetCoords)
            child.on_draw(self,c)
            c.restore()
    
    def _handle_event(self,w,e,f):
        for child in reversed(self.list):
            p = Point(child.toWidgetCoords.transform_point(e.x,e.y))
            if child.is_point_in(p):
                if f(child)(e,child):
                    return True
        return False
    
    def on_mouse_down(self, w, e):
        def take_on_mouse_down(w):
            return w.on_mouse_down
        return self._handle_event(w,e,take_on_mouse_down)
    
    def on_mouse_up(self, w, e):
        def take_on_mouse_up(w):
            return w.on_mouse_up
        return self._handle_event(w,e,take_on_mouse_up)

    def on_mouse_move(self, w, e):
        def take_on_mouse_move(w):
            return w.on_mouse_move
        return self._handle_event(w,e,take_on_mouse_move)
                        

class UncheckedContainer(Container):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._widget_list = []
    
    @property
    def list(self):
        for (i,w) in self._widget_list:
            yield w
    
    def remove_id(self, id_v:"id"):
        index = None
        for (pos,(i,w)) in enumerate(self._widget_list):
            if i == id_v:
                index = pos
                break
        if index is None:
            raise KeyError("{} not found".format(id))
        del(self._widget_list[index])
    
    def remove_obj(self, widget):
        index = None
        for (pos,(i,w)) in enumerate(self._widget_list):
            if w == widget:
                index = pos
                break
        if index is None:
            raise KeyError("{} not found".format(str(widget)))
        del(self._widget_list[index])
    
class MainWindow(Gtk.Window):
    def __init__(self,title,*args,**kwargs):
        super().__init__(*args,title=title,**kwargs)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
    
    def start_main(self):
        self.show_all()
        return Gtk.main() 