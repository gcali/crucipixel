'''
Created on May 20, 2015

@author: giovanni
'''
from typing import Callable

import cairo

from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.geometry import Point, Rectangle
from lightwidgets.events import MouseEvent, KeyboardEvent, MouseEventCategory


def _transform_point(widget: Widget, point: Point):
    return Point(widget.toWidgetCoords.transform_point(point.x, point.y))

class Container(Widget):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "Container"
        self._sizes = {}

    @property
    def list(self):
        raise NotImplementedError()
    
    @property
    def sizes(self):
        return self._sizes
    
    def add(self,widget) -> "id":
        raise NotImplementedError()
    
    def remove_obj(self,widget):
        raise NotImplementedError()
    
    def layout(self, context: cairo.Context):
        for child in self.list:
            if child.visible:
                context.save()
                child.layout(context)
                context.restore()

    def on_draw(self, widget: Widget, context: cairo.Context):
        for child in self.list:
            if child.visible:
                context.save()
                context.transform(child.fromWidgetCoords)
                if child.is_clip_set():
                    rectangle = child.clip_rectangle
                    context.rectangle(rectangle.start.x,rectangle.start.y,
                                      rectangle.width,rectangle.height)
                    context.clip()
                child.on_draw(self,context)
                context.restore()
    
    def update_min_size(self, value):
        self.min_size = value
        # self.sizes[widget] = value
    
    def get_allocated_size(self, widget):
        try:
            self.sizes[widget]
        except KeyError:
            raise AttributeError()


    def _handle_mouse_event(
            self,
            widget: Widget,
            event: MouseEvent,
            callback: Callable[[Widget],
            Callable[[Widget, MouseEvent], bool]],
            category: MouseEventCategory
    ):
        for child in reversed(list(self.list)):
            if child.visible:
                # p = Point(child.toWidgetCoords.transform_point(event.x,event.y))
                p = _transform_point(child, event)
                was_in = child.is_point_in(p, category)
                if category == MouseEventCategory.MOUSE_UP or \
                        was_in:
                    child.mouse_is_in = was_in
                    local_event = event.__copy__()
                    local_event.x = p.x
                    local_event.y = p.y
                    if (callback(child))(self, local_event):
                        return True
                else:
                    child.mouse_is_in = False
        return False
    
    def _handle_keyboard_event(self,widget,event,callback):
        for child in reversed(list(self.list)):
            if (callback(child)(self,event)):
                return True
        return False
    
    def on_mouse_down(self, widget: Widget, event: MouseEvent):
        super().on_mouse_down(widget, event)
        def take_on_mouse_down(w):
            return w.on_mouse_down
        return self._handle_mouse_event(widget,
                                        event,
                                        take_on_mouse_down,
                                        MouseEvent.MOUSE_DOWN)
    
    def on_mouse_up(self, widget: Widget, event: MouseEvent):
        super().on_mouse_up(widget, event)
        def take_on_mouse_up(w):
            return w.on_mouse_up
        return self._handle_mouse_event(widget,
                                        event,
                                        take_on_mouse_up,
                                        MouseEvent.MOUSE_UP)

    def on_mouse_move(self, widget: Widget, event: MouseEvent):
        super().on_mouse_move(widget, event)
        def take_on_mouse_move(w):
            return w.on_mouse_move
        return self._handle_mouse_event(widget, event, take_on_mouse_move, MouseEvent.MOUSE_MOVE)
    
    def on_mouse_exit(self):
        for child in reversed(list(self.list)):
            child.mouse_is_in = False
    
    def on_key_down(self, widget: Widget, event: KeyboardEvent) -> bool:
        def take_on_key_down(w):
            return w.on_key_down
        return self._handle_keyboard_event(self, event, take_on_key_down)

    def on_key_up(self, widget: Widget, event: KeyboardEvent) -> bool:
        def take_on_key_up(w):
            return w.on_key_up
        return self._handle_keyboard_event(self, event, take_on_key_up)
    
    def register_signal_for_child(self, signal_name:"str", widget:"Widget"):
        def handle_child(*args):
            return widget.handle_signal(signal_name,*args)
        self.register_signal(signal_name, handle_child)
    
    def is_point_in(self, p: "Point", category=MouseEvent.UNKNOWN):
        for child in self.list:
            if child.is_point_in(_transform_point(child, p),category):
                return True
        return False
    
    def is_clip_set(self):
        if super().is_clip_set():
            return True
        found_one = False
        for child in self.list:
            found_one = True
            if not child.is_clip_set():
                return False
        return found_one
    
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
                else:
                    return super().clip_rectangle
            if not vertexes:
                return super().clip_rectangle
            else:
                return Rectangle.from_points(vertexes)

    def set_max_size(self, width: int, height: int):
        self.father.set_max_size(width, height)


class UncheckedContainer(Container):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._widget_list = []
    
    @property
    def list(self):
        for (_,w) in self._widget_list:
            yield w
    
    def add(self,widget,top=0):
        self._widget_list.append((top,widget))
        self._widget_list = sorted(self._widget_list,key=lambda x:-x[0])
        widget.father = self
        try:
            self.min_size = widget.min_size
        except AttributeError:
            pass
        return widget
    
    def remove_obj(self, widget):
        self._widget_list = [(top, list_widget)
                             for (top, list_widget) in self._widget_list
                             if list_widget != widget]
