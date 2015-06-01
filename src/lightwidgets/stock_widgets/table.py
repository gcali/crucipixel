'''
Created on May 20, 2015

@author: giovanni
'''
from lightwidgets.stock_widgets.widget import Widget
from crucipixel.interface.global_constants import char_size

class Table(Widget):
    
    def __init__(self, cols, entries:"tuple(cols) list"=[], **kwargs):
        super().__init__(**kwargs)
        
        self._entries = list(entries)
        self.font_size = 20
        self.cols = cols
    
    def add_entry(self, entry):
        self._entries.append(entry)
    
    @property
    def entries(self):
        return list(self._entries)
    
    @entries.setter
    def entries(self, value):
        self._entries = list(value)
    
    @property
    def cell_height(self):
        height = char_size(self.font_size).y
        return height * 2
    
    @property
    def cell_widths(self):
        char_width = char_size(self.font_size).x
        comparison_list = zip(*self._entries)
        return [max([char_width * (len(e) + 2) for e in column]) for column in comparison_list]
        
        
    def on_draw(self, w, c):
        super().on_draw(w,c)
        widths = self.cell_widths
        height = self.cell_height
        total_width = sum(widths)
        total_height = height * len(self._entries)
        def draw_external():
            c.move_to(0,0)
            #TODO
        for i,e in enumerate(self._entries): 
            draw_external(i)