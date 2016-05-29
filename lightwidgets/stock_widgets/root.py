'''
Created on May 20, 2015

@author: giovanni
'''
# from gi.repository import Gtk
from gi.repository import Gtk
from gi.repository import Gdk
# from gi.repository import Gdk
# from gi.repository import Gdk
from gi.repository.Gdk import EventMask

from lightwidgets.events import _transform_mouse_event,\
    _transform_keyboard_event, ScrollEvent, _transform_scroll_event
# from gi.overrides.Gdk import Gdk
from lightwidgets.geometry import Rectangle, Point
from lightwidgets.stock_widgets.widget import Widget
from numbers import Number

class Root(Gtk.DrawingArea):
    
    def __init__(self, width=-1,height=-1,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self._child = None
        events = Gdk.EventMask.BUTTON_PRESS_MASK\
               | Gdk.EventMask.BUTTON_RELEASE_MASK\
               | Gdk.EventMask.POINTER_MOTION_MASK\
               | Gdk.EventMask.SCROLL_MASK\
               | Gdk.EventMask.KEY_PRESS_MASK\
               | Gdk.EventMask.KEY_RELEASE_MASK\
               | Gdk.EventMask.STRUCTURE_MASK
        self.add_events(events)
        self.set_can_focus(True)
        self.connect("draw", self.on_draw)
        self.connect("scroll-event", self.on_scroll)
        self.connect("button-press-event", self.on_mouse_down)
        self.connect("button-release-event", self.on_mouse_up)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("key-press-event", self.on_key_down)
        self.connect("key-release-event", self.on_key_up)
        self.connect("configure-event", self.on_new_configuration)
        self.set_min_size(width, height)
        self.current_size = width, height
        self._switcher = _RootChildSwitcher()
        self._switcher.father = self
        self._lw_signals = {}
        self._main_window = None
        self.mouse_is_down = False
        
    @property
    def child(self):
        return self._child
    
    @child.setter
    def child(self, value):
        self._child = value
        value.father = self
        try:
            size_x, size_y = value.min_size
            self.set_min_size(size_x, size_y)
        except AttributeError:
            pass

    @property
    def window_size(self):
        return self.current_size
    
    @property
    def container_size(self):
        return self.window_size

    @property
    def shape(self):
        w, h = self.container_size
        return Rectangle(Point(0, 0), w, h)
    
    def set_main_window(self, window):
        window.add(self)
        self._main_window = window

    def update_min_size(self, value):
        self.set_min_size(value[0], value[1])

    def set_min_size(self, sizeX:"num", sizeY:"num"):
        self.set_size_request(sizeX, sizeY)
    
    def set_child(self, child:"Widget"):
        self.child = child
        self.invalidate()
    
    def on_draw(self, widget:"Widget", context:"cairo.Context"):
        if self._child is not None:
            context.save()
            self._child.layout(context)
            context.restore()
            context.save()
            context.transform(self._child.fromWidgetCoords)
            if self._child.is_clip_set():
                rectangle = self._child.clip_rectangle
                context.rectangle(rectangle.start.x,rectangle.start.y,
                                  rectangle.width,rectangle.height)
                context.clip()
            self._child.on_draw(self,context)
            context.restore()
    
    def _transform_mouse_event(self,event_type,e):
        if self._child is not None:
            return _transform_mouse_event(event_type,e,self._child)

    def _transform_scroll_event(self, event: Gdk.EventScroll) -> ScrollEvent:
        if self._child is not None:
            return _transform_scroll_event(event, self._child)
    
    def on_mouse_down(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self.mouse_is_down = True
        self.grab_focus()
        if self._child is not None:
            if e.type == Gdk.EventType.BUTTON_PRESS:
                self._child.on_mouse_down(self,self._transform_mouse_event("mouse_down",e))
        return True
    
    def on_mouse_up(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self.mouse_is_down = False
        if self._child is not None:
            self._child.on_mouse_up(self,self._transform_mouse_event("mouse_up", e))
        return True

    def on_scroll(self, widget: Gtk.Widget, event: Gdk.EventScroll):
        if self._child is not None:
            self._child.on_scroll(self._transform_scroll_event(event))

    def on_mouse_move(self,w:"Gtk.Widget",e:"Gdk.EventMotion"):
        if self._child is not None:
            self._child.on_mouse_move(self,self._transform_mouse_event("mouse_move",e))
        return True
    
    def on_key_down(self,w:"Gtk.Widget",e:"Gdk.EventKey"):
        if self._child is not None:
            self._child.on_key_down(self,_transform_keyboard_event("key_down",e))
        return True

    def on_key_up(self,w:"Gtk.Widget",e:"Gdk.EventKey"):
        if self._child is not None:
            self._child.on_key_up(self,_transform_keyboard_event("key_up",e))
        return True
    
    def on_new_configuration(self,widget:"Gtk.Widget",event:"Gdk.EventConfigure"):
        new_size = (event.width, event.height)
        if self._child is not None and self.current_size != new_size:
            self.current_size = new_size
            self._child.on_resize(new_size)
        self.invalidate()
    
    def invalidate(self):
        self.queue_draw()

    def register_signal_for_child(self,signal_name,widget):
        try:
            self._lw_signals[signal_name].append(widget)
        except KeyError:
            self._lw_signals[signal_name] = []
            return self.register_signal_for_child(signal_name, widget)

    def broadcast_lw_signal(self,signal_name,*args): 
        try:
            for w in self._lw_signals[signal_name]:
                w.handle_signal(signal_name,*args)
        except KeyError as e:
            print("Signal not found: {}".format(signal_name))

    def register_switch_to(self, signal_name:"str", widget:"Widget"):
        return self._switcher.register_switch_to(signal_name, widget)

    def quit(self):
        if self._main_window is not None:
            self._main_window.destroy()


class _RootChildSwitcher(Widget):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
    
    def register_switch_to(self, signal_name:"str", widget:"Widget"):
        def switch():
            self.father.child = widget
            widget.invalidate()
        self.register_signal(signal_name, switch)


class MainWindow(Gtk.Window):
    def __init__(self,title,*args,**kwargs):
        super().__init__(*args,title=title,**kwargs)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
    
    def start_main(self):
        self.show_all()
        return Gtk.main()

    def set_background_rgba(self, r: Number, g: Number, b: Number, a: Number):
        self.override_background_color(Gtk.StateFlags.NORMAL,
                                       Gdk.RGBA(r, g, b, a))
