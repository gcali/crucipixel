'''
Created on May 19, 2015

@author: giovanni
'''
from lightwidgets.stock_widgets.containers import UncheckedContainer
from lightwidgets.stock_widgets.buttons import Button



class MainMenu(UncheckedContainer):
    
    def on_mouse_down(self, w, e):
        return UncheckedContainer.on_mouse_down(self, w, e)   
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
    pass