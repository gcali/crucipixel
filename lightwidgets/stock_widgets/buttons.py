'''
Created on May 20, 2015

@author: giovanni
'''
from typing import Tuple, Callable, Iterable

import cairo

from crucipixel.interface import global_constants
from lightwidgets.stock_widgets.containers import UncheckedContainer

from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.geometrical import DrawableRoundedRectangle
from lightwidgets.support import rgb_to_gtk
from lightwidgets.events import MouseEvent, MouseButton


def click_left_button_wrapper(action: Callable[[], None]) \
        -> Callable[[MouseButton], None]:
    return lambda x: (action() if x == MouseButton.LEFT else None)


class BetterButton(Widget):

    LEFT = 0,
    RIGHT = 1,
    CENTER = 2

    def __init__(self, label: str,
                 font_size: int = 20,
                 padding: int = 10,
                 origin: int = CENTER,
                 background_color: Tuple[int, int, int] = (.588, .588, .588),
                 label_color: Tuple[int, int, int] = (0, 0, 0),
                 **kwargs):
        super().__init__(self, **kwargs)
        self.min_height = 0
        self.label = label
        self.padding = padding
        self.origin = origin
        self.background_color = background_color
        self.label_color = label_color
        self.font_size = font_size
        self.shape = None
        self.disabled = False

        self.on_click_action = None

        self._mouse_up_interested = None

    def is_point_in(self,p: Point, category=MouseEvent.UNKNOWN):
        if not self.is_shape_set:
            return False
        # elif category == MouseEvent.MOUSE_UP and self._mouse_up_interested:
        #     return True
        else:
            return self.shape.is_point_in(p)

    def on_click(self, widget: "Widget", button: MouseButton):
        if self.on_click_action is not None and not self.disabled:
            self.on_click_action(button)

    def layout(self, context: cairo.Context):
        super().layout(context)
        self.set_shape_from_context(context)

    def set_shape_from_context(self, context: cairo.Context):
        label = self.label
        padding = self.padding
        context.set_font_size(self.font_size)
        xb, yb, w, h, xa, ya = context.text_extents(label)
        width = padding * 2 + xa
        height = padding * 2 + h
        height = max(height, self.min_height)

        if self.origin == self.LEFT:
            start = Point(0, 0)
        elif self.origin == self.CENTER:
            start = Point(-width/2, 0)
        else:
            start = Point(-width, 0)
        self.shape = DrawableRoundedRectangle(start, width, height)

    def on_draw(self, widget: Widget, context: cairo.Context):

        start_x, start_y = context.get_current_point()
        context.set_font_size(self.font_size)

        context.move_to(0, 0)

        if not self.is_shape_set:
            self.set_shape_from_context(context)
        shape = self.shape
        start = shape.start
        padding = self.padding
        h = shape.height - 2 * padding
        label = self.label

        context.set_source_rgb(*self.background_color)
        shape.draw_on_context(context)
        context.fill_preserve()

        context.set_line_width(1)
        context.set_source_rgb(*self.label_color)
        context.stroke()

        if self.disabled:
            context.set_source_rgba(1, 1, 1, .7)
            context.move_to(start.x + padding-1,
                            start.y + padding + h+1)
            context.show_text(label)
            context.set_source_rgba(*self.label_color, .9)
        else:
            context.set_source_rgb(*self.label_color)
        context.move_to(start.x + padding,
                        start.y + padding + h)
        context.show_text(label)

        if self.disabled:
            context.set_source_rgba(1, 1, 1, .7)
            context.move_to(0, 0)
            shape.draw_on_context(context)
            context.fill()



def main():
    main_window = MainWindow(title="button")
    root = Root(200, 200)
    root.set_main_window(main_window)
    button = BetterButton("Pulsante!", 20, origin=BetterButton.CENTER)
    disabled = BetterButton("Disable", 20, origin=BetterButton.CENTER)
    button.translate(100, 50)
    disabled.translate(100, 100)
    button.on_click_action = click_left_button_wrapper(lambda: print("Hi!"))
    def disabled_action():
        button.disabled = not button.disabled
        button.invalidate()
    disabled.on_click_action = click_left_button_wrapper(disabled_action)
    container = UncheckedContainer()
    container.add(button)
    container.add(disabled)
    root.set_child(container)

    main_window.start_main()




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
            
        start_x = (self.size.x - width)/2 + xb
        start_y = (self.size.y - height)/2 - yb
        c.move_to(start_x,start_y)
        c.set_source_rgb(*self.label_color)
        c.show_text(self.label)
        c.restore()
    
    def on_mouse_down(self, w, e):
        super().on_mouse_down(w, e)
        self._button_mouse_was_down = True

    def on_mouse_up(self, w, e):
        super().on_mouse_up(w,e)
        if not self.on_mouse_up_broadcast is None:
            self.broadcast_lw_signal(self.on_mouse_up_broadcast)
        self._button_mouse_was_down = False
    
    def is_point_in(self, p:"Point", category=MouseEvent.UNKNOWN):
        if category == MouseEvent.MOUSE_UP and self._button_mouse_was_down:
            return True
        return self._shape.is_point_in(p)

if __name__ == '__main__':
    main()


class OrderedButtons(UncheckedContainer):

    def __init__(self,
                 button_names: Iterable[Iterable[str]],
                 background_color: Tuple[int, int, int] =\
                     global_constants.background,
                 **kwargs):
        super().__init__(**kwargs)
        self._padding = 10
        self._buttons = [
            [BetterButton(name, 20, self._padding, origin=BetterButton.LEFT)
             for name in series]
            for series in button_names
        ]

        self._active = [
            0 for _ in self._buttons
        ]

        for series, active in zip(self._buttons, self._active):
            for b in series:
                self.add(b)
                b.visible = False
            series[active].visible = True

        self.background_color = background_color

    def _iter_over_visible(self) -> Iterable[BetterButton]:
        for series, active in zip(self._buttons, self._active):
            yield series[active]

    def set_action(self, index: int, series_position: int,
                   action: Callable[[MouseButton], None]):
        self._buttons[index][series_position].on_click_action = action

    def get_action(self, index: int, series_position: int) -> Callable[[MouseButton], None]:
        return self._buttons[index][series_position].on_click_action

    def next_visible(self, index: int):
        old = self._active[index]
        new = (old + 1) % len(self._buttons[index])
        self.set_visible(index, new)

    def set_visible(self, index: int, series_position: int):
        old = self._active[index]
        new = series_position % len(self._buttons[index])
        self._buttons[index][old].visible = False
        self._buttons[index][new].visible = True
        self._active[index] = new
        self.invalidate()

    def set_clickable(self, index: int, series_position: int, clickable: bool):
        self._buttons[index][
            series_position % len(self._buttons[index])
        ].disabled = not clickable

    def layout(self, context: cairo.Context):
        super().layout(context)

        height = 0
        width = self._padding
        for button in self._iter_over_visible():
            button.set_translate(width, self._padding)
            height = max(height, button.shape.height)
            width += button.shape.width + self._padding
        for button in self._iter_over_visible():
            button.min_height = height
            button.layout(context)

        height += 2 * self._padding

        self.shape = DrawableRoundedRectangle(
            Point(0, 0),
            width,
            height
        )

    def on_draw(self, widget: Widget, context: cairo.Context):

        context.save()
        context.set_source_rgb(*self.background_color)
        self.shape.draw_on_context(context)
        context.fill_preserve()
        context.set_source_rgb(0,0,0)
        context.set_line_width(1)
        context.stroke()

        context.restore()

        super().on_draw(widget, context)
