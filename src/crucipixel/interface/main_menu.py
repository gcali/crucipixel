'''
Created on May 19, 2015

@author: giovanni
'''
from time import sleep
from typing import Callable, List

import cairo

from lightwidgets.events import MouseButton
from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.buttons import Button, BetterButton
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget


class BetterMainMenu(UncheckedContainer):

    def __init__(self,
                 title: str,
                 labels: List[str],
                 callbacks: List[Callable[[MouseButton], None]],
                 font_size: int=20,
                 distance: int=20,
                 **kwargs):
        self.done = False
        super().__init__(**kwargs)
        self.title = title
        self.distance = distance
        self._buttons = [
            BetterButton(
                label,
                font_size,
                origin=BetterButton.CENTER
            ) for label in labels
        ]

        for b in self._buttons:
            self.add(b)

        for b, c in zip(self._buttons, callbacks):
            b.on_click_action = c

    def set_callback(self, index: int, callback: Callable[[MouseButton], None]):
        self._buttons[index].on_click_action = callback
        print("Set for", index)

    def on_resize(self,new_father_dim):
        self.invalidate()

    def on_draw(self, widget: Widget, context: cairo.Context):


        for b in self._buttons:
            b.set_shape_from_context(context)

        shapes = [b.shape for b in self._buttons]

        context.save()
        context.select_font_face("", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        xb, yb, w, h, xa, ya = context.text_extents(self.title)

        width = max(shape.width for shape in shapes)
        width = max(width, xa)
        container_width = self.container_size[0]
        translation = Point(0, self.distance)
        if container_width > width:
            translation += Point((container_width)/2, 0)
        else:
            translation += Point(width/2, 0)

        context.move_to(translation.x - xa/2, h + self.distance)
        context.show_text(self.title)
        context.restore()

        height = h + self.distance * 3
        for b in self._buttons:
            height += b.shape.height + self.distance

        self.min_size = width + 2 * self.distance, height + self.distance

        start_point = context.get_current_point()
        translation += Point(0, h + self.distance * 2)
        context.translate(translation.x, translation.y)

        distance_offset = Point(0, self.distance)


        for b in self._buttons:
            context.move_to(*start_point)
            b.set_translate(translation.x, translation.y)
            context.save()
            b.on_draw(widget, context)
            context.restore()

            to_translate = Point(distance_offset.x,
                                 distance_offset.y + b.shape.height)
            context.translate(to_translate.x, to_translate.y)
            translation += to_translate


def main() -> int:
    main_window = MainWindow(title="menu_test")
    root = Root()
    root.set_main_window(main_window)

    def create_callback(x: int):
        return lambda: print("Hi from", x)
    menu = BetterMainMenu(["ciao", "come", "stai"], [create_callback(x) for x in range(3)])
    root.set_child(menu)

    main_window.start_main()
    return 0


class MainMenu(UncheckedContainer):
    
    def __init__(self, button_width,
                       button_height, 
                       entries:"[str]"=[], 
                       distance=20,
                       broadcasts:"[str]"=[],
                       *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._button_width = button_width
        self._button_height = button_height
        self.distance = distance
        self._buttons = [Button(label=text,size_x=button_width,size_y=button_height) for text in entries]
        
        for i,b in enumerate(self._buttons):
            b.ID = "Button{}".format(i)
            b.force_clip_not_set = True
            self.add(b)
        if broadcasts:
            for button,name in zip(self._buttons,broadcasts):
                if name != None and name != "":
                    button.on_mouse_up_broadcast = name
        self.refresh_min_size()

    @property
    def min_size(self):
        return (self._button_width + 2 * self.distance,
                (self._button_height + 2*self.distance) * len(self._buttons))
        
    
    def on_draw(self, widget, context):
        if not self._buttons:
            return
        total_width, total_height = self.container_size
        total_button_width = self._button_width
        total_button_height = (self.distance + self._button_height) * len(self._buttons) 
        def padding(container,widget):
            if container < widget:
                return 0
            else:
                return (container-widget)//2
        upper_padding = max(padding(total_height,total_button_height),self.distance)
        left_padding = padding(total_width,total_button_width)
        translate_x = left_padding
        translate_y = upper_padding
        for b in self._buttons:
            b.set_translate(translate_x,translate_y)
            translate_y += self._button_height + self.distance
        super().on_draw(widget, context)
    


if __name__ == '__main__':
    main()
