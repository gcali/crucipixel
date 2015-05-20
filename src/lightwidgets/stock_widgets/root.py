'''
Created on May 20, 2015

@author: giovanni
'''
from gi.repository import Gtk
from gi.repository.Gdk import EventMask
from lightwidgets.events import _transform_mouse_event,\
    _transform_keyboard_event
from gi.overrides.Gdk import Gdk
from lightwidgets.stock_widgets.widget import Widget

class Root(Gtk.DrawingArea):
    
    def __init__(self, width=-1,height=-1,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self._child = None
        events = EventMask.BUTTON_PRESS_MASK\
                 | EventMask.BUTTON_RELEASE_MASK\
                 | EventMask.POINTER_MOTION_MASK\
                 | EventMask.KEY_PRESS_MASK\
                 | EventMask.KEY_RELEASE_MASK\
                 | EventMask.STRUCTURE_MASK
        self.add_events(events)
        self.set_can_focus(True)
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_mouse_down)
        self.connect("button-release-event", self.on_mouse_up)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("key-press-event", self.on_key_down)
        self.connect("key-release-event", self.on_key_up)
        self.connect("configure-event", self.on_new_configuration)
        self.set_min_size(width,height)
        self.current_size = (width,height)
        self._switcher = _RootChildSwitcher()
        self._switcher.father = self
        self._lw_signals = {}
        self._main_window = None
        
    @property
    def child(self):
        return self._child
    
    @child.setter
    def child(self, value):
        self._child = value
        value.father = self
        if hasattr(value,"min_size"):
            size_x,size_y =  value.min_size
            self.set_min_size(size_x, size_y)
        
    @property
    def window_size(self):
        return self.current_size
    
    @property
    def container_size(self):
        return self.window_size
    
    def set_main_window(self, window):
        window.add(self)
        self._main_window = window
        
    def set_min_size(self, sizeX:"num", sizeY:"num"):
        self.set_size_request(sizeX, sizeY)
    
    def set_child(self, child:"Widget"):
        self.child = child
    
    def on_draw(self, widget:"Widget", context:"cairo.Context"):
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
        return _transform_mouse_event(event_type,e,self._child)
    
    def on_mouse_down(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self.grab_focus()
        if e.type == Gdk.EventType.BUTTON_PRESS:
            self._child.on_mouse_down(self,self._transform_mouse_event("mouse_down",e))
        return True
    
    def on_mouse_up(self,w:"Gtk.Widget",e:"Gdk.EventButton"):
        self._child.on_mouse_up(self,self._transform_mouse_event("mouse_up", e))
        return True

    def on_mouse_move(self,w:"Gtk.Widget",e:"Gdk.EventMotion"):
        self._child.on_mouse_move(self,self._transform_mouse_event("mouse_move",e))
        return True
    
    def on_key_down(self,w:"Gtk.Widget",e:"Gdk.EventKey"):
        self._child.on_key_down(self,_transform_keyboard_event("key_down",e))
        return True

    def on_key_up(self,w:"Gtk.Widget",e:"Gdk.EventKey"):
        self._child.on_key_up(self,_transform_keyboard_event("key_up",e))
        return True
    
    def on_new_configuration(self,widget:"Gtk.Widget",event:"Gdk.EventConfigure"):
        new_size = (event.width, event.height)
        if not self._child is None and self.current_size != new_size:
            self.current_size = new_size
            self._child.on_resize(new_size)
    
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
    
    def register_switch_to(self, signal_name:"str", widget:"Widget"):
        return self._switcher.register_switch_to(signal_name, widget)
    
class _RootChildSwitcher(Widget):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
    
    def register_switch_to(self, signal_name:"str", widget:"Widget"):
        def switch():
            self.father.child = widget
            self.father.invalidate()
            print("I'm switching!")
        self.register_signal(signal_name, switch)


class MainWindow(Gtk.Window):
    def __init__(self,title,*args,**kwargs):
        super().__init__(*args,title=title,**kwargs)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
    
    def start_main(self):
        self.show_all()
        return Gtk.main() 
