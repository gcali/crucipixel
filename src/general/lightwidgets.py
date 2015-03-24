'''
Created on Feb 18, 2015

@author: giovanni
'''

from gi.repository import Gtk
from gi.repository.Gdk import EventMask
import cairo
from math import pi,sqrt
from general.geometry import Point, Rectangle
from _operator import pos 
from gi.overrides.Gdk import Gdk
from general.animator import Animator, Slide

def _transform_mouse_event(event_type,e,w):
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
    UNKNOWN =      0
    MOUSE_DOWN =   1
    MOUSE_UP =     2
    MOUSE_MOVE =   3
    
    def __init__(self, event_type, x, y, button=None):
        self.x = x
        self.y = y
        self.event_type = event_type
        self.button = button
    
    def __copy__(self):
        return MouseEvent(self.event_type,self.x,self.y,self.button)

def _transform_keyboard_event(event_type,e):
    event_type = event_type
    modifiers = { Gdk.KEY_Shift_L : "shift_l",
                  Gdk.KEY_Shift_R : "shift_r",
                  Gdk.KEY_Control_L : "ctrl_l",
                  Gdk.KEY_Control_R : "ctrl_r",
                  Gdk.KEY_Alt_L : "alt_l",
                  Gdk.KEY_Alt_R : "alt_r"}
    if e.keyval in modifiers:
        key = modifiers[e.keyval]
    else:
        key = chr(Gdk.keyval_to_unicode(e.keyval))
    return KeyboardEvent(event_type,key)
    

class KeyboardEvent:
    UNKNOWN  = 0
    KEY_DOWN = 1
    KEY_UP   = 2
    
    def __init__(self, event_type, key, modifiers=[]):
        self.event_type = event_type
        self.key = key
        self.modifiers = modifiers

class Root(Gtk.DrawingArea):
    
    def __init__(self, width=-1,height=-1,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.child = None
        events = EventMask.BUTTON_PRESS_MASK\
                 | EventMask.BUTTON_RELEASE_MASK\
                 | EventMask.POINTER_MOTION_MASK\
                 | EventMask.KEY_PRESS_MASK\
                 | EventMask.KEY_RELEASE_MASK
        self.add_events(events)
        self.set_can_focus(True)
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_mouse_down)
        self.connect("button-release-event", self.on_mouse_up)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("key-press-event", self.on_key_down)
        self.connect("key-release-event", self.on_key_up)
        self.set_min_size(width,height)
        self._lw_signals = {}
        
    def set_min_size(self, sizeX:"num", sizeY:"num"):
        self.set_size_request(sizeX, sizeY)
    
    def set_child(self, child:"Widget"):
        self.child = child
        child.father = self
    
    def on_draw(self, widget:"Widget", context:"cairo.Context"):
        context.save()
        context.transform(self.child.fromWidgetCoords)
        if self.child.is_clip_set():
            rectangle = self.child.clip_rectangle
            context.rectangle(rectangle.start.x,rectangle.start.y,
                              rectangle.width,rectangle.height)
            context.clip()
        self.child.on_draw(self,context)
        context.restore()
    
    def _transform_mouse_event(self,event_type,e):
        return _transform_mouse_event(event_type,e,self.child)
    
    def on_mouse_down(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self.grab_focus()
        if e.type == Gdk.EventType.BUTTON_PRESS:
            self.child.on_mouse_down(self,self._transform_mouse_event("mouse_down",e))
        return True
    
    def on_mouse_up(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self.child.on_mouse_up(self,self._transform_mouse_event("mouse_up", e))
        return True

    def on_mouse_move(self,w:"Gtk.Widget",e:"Gdk.EventMotion"):
        self.child.on_mouse_move(self,self._transform_mouse_event("mouse_move",e))
        return True
    
    def on_key_down(self,w:"Gtk.Widget",e:"Gdk.EventKey"):
        self.child.on_key_down(self,_transform_keyboard_event("key_down",e))
        return True

    def on_key_up(self,w:"Gtk.Widget",e:"Gdk.EventKey"):
        self.child.on_key_up(self,_transform_keyboard_event("key_up",e))
        return True
    
    def invalidate(self):
        self.queue_draw()
    
    def register_signal_for_child(self,signal_name,widget):
#         print("I've been called!")
        try:
            self._lw_signals[signal_name].append(widget)
#             print("I existed!")
        except KeyError:
            self._lw_signals[signal_name] = []
            return self.register_signal_for_child(signal_name, widget)

    def broadcast_lw_signal(self,signal_name,*args): 
#         print(self._lw_signals)
        for w in self._lw_signals[signal_name]:
            w.handle_signal(signal_name,*args)
    

class Widget:
    
    NO_CLIP=None

    def __init__(self, sizeX=0, sizeY=0):
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
    
    def __str__(self):
        return str(self.ID)

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
    def fromWidgetCoords(self):
        return self._fromScale.multiply(self._fromRotate.multiply(self._fromTranslate))
#         return self._fromRotate.multiply(self._fromTranslate.multiply(self._fromScale))
    
    @property
    def toWidgetCoords(self):
        return self._toTranslate.multiply(self._toRotate.multiply(self._toScale))
#         return self._toScale.multiply(self._toTranslate.multiply(self._toRotate))
    
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
#         print(self,c.clip_extents())

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
    
    def is_point_in(self, p:"Point",*args,**kwargs):
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
            w.invalidate()
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
    
    def on_draw(self,widget,context):
        for child in self.list:
            context.save()
            context.transform(child.fromWidgetCoords)
            if child.is_clip_set():
                rectangle = child.clip_rectangle
                context.rectangle(rectangle.start.x,rectangle.start.y,
                                  rectangle.width,rectangle.height)
                context.clip() 
            child.on_draw(self,context)
            context.restore()
    
    def _handle_mouse_event(self,widget,event,callback,category):
        for child in reversed(list(self.list)):
            p = Point(child.toWidgetCoords.transform_point(event.x,event.y))
            try:
                if child.is_point_in(p,category):
                    child.mouse_is_in = True
                    local_event = event.__copy__()
                    local_event.x = p.x
                    local_event.y = p.y
                    if (callback(child))(self,local_event):
                        return True
                else:
                    child.mouse_is_in = False
            except TypeError:
                return True
        return False
    
    def _handle_keyboard_event(self,widget,event,callback):
        for child in reversed(list(self.list)):
            if (callback(child)(self,event)):
                return True
        return False
    
    def on_mouse_down(self, w, e):
        def take_on_mouse_down(w):
            return w.on_mouse_down
        return self._handle_mouse_event(w,e,take_on_mouse_down,MouseEvent.MOUSE_DOWN)
    
    def on_mouse_up(self, w, e):
        def take_on_mouse_up(w):
            return w.on_mouse_up
        return self._handle_mouse_event(w,e,take_on_mouse_up,MouseEvent.MOUSE_UP)

    def on_mouse_move(self, w, e):
        super().on_mouse_move(w,e)
        def take_on_mouse_move(w):
            return w.on_mouse_move
        return self._handle_mouse_event(w,e,take_on_mouse_move,MouseEvent.MOUSE_MOVE)
    
    def on_mouse_exit(self):
        for child in reversed(list(self.list)):
            child.mouse_is_in = False
    
    def on_key_down(self, w, e):
        def take_on_key_down(w):
            return w.on_key_down
        return self._handle_keyboard_event(self, e, take_on_key_down)

    def on_key_up(self, w, e):
        def take_on_key_up(w):
            return w.on_key_up
        return self._handle_keyboard_event(self, e, take_on_key_up)
    
    def register_signal_for_child(self, signal_name:"str", widget:"Widget"):
        def handle_child(*args):
            return widget.handle_signal(signal_name,*args)
        self.register_signal(signal_name, handle_child)
    
    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        for child in self.list:
            if child.is_point_in(p,category):
                return True
        return False
    
    def is_clip_set(self):
        if super().is_clip_set():
            return True
        if not self.list:
            return False
        for child in self.list:
            if not child.is_clip_set():
                return False
        return True
    
    @property
    def clip_rectangle(self):
        if super().is_clip_set():
            return super().clip_rectangle
        else:
            vertexes = []
            for child in self.list:
                if child.is_clip_set():
                    child_vertexes = [Point(child.fromWidgetCoords.transform_point(p.x,p.y))\
                                        for p in child.clip_rectangle.get_vertexes()]
                    vertexes.extend(child_vertexes)
            if not vertexes:
                return super().clip_rectangle
            else:
                return Rectangle.from_points(vertexes)

                        

class UncheckedContainer(Container):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._widget_list = []
    
    @property
    def list(self):
        for (_,w) in self._widget_list:
            yield w
    
    def add(self,widget):
        self._widget_list.append((widget,widget))
        widget.father = self
        return widget
    
    def remove_id(self, id_v:"id"):
        index = None
        for (pos,(i,_)) in enumerate(self._widget_list):
            if i == id_v:
                index = pos
                break
        if index is None:
            raise KeyError("{} not found".format(id))
        del(self._widget_list[index])
    
    def remove_obj(self, widget):
        index = None
        for (pos,(_,w)) in enumerate(self._widget_list):
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

if __name__ == '__main__':
    main = MainWindow("Animated donut")
    root = Root(600,600)
    donut = Donut(Point(200,200), 50, 150)
    donut_b = Donut(Point(300,300), 50, 150)
    main.add(root)
    cont = UncheckedContainer()
    cont.add(donut)
#     cont.add(donut_b)
    root.set_child(cont)
    animator = Animator(interval=.01,widget=root)
    start_point = Point(50,50)
    end_point = Point(350,350)
    speed = Point(200,200)
    duration = 2
    pos = start_point
    def assign(p):
        global pos
        delta_point = p - pos
        print(p)
        donut.centerP = delta_point
        pos = p
    animation = Slide(duration,
                      start_point,
                      end_point,
                      speed,
                      assign)
    animator.add_animation(animation)
    animator.start() 
    main.start_main()