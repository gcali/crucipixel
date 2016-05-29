'''
Created on Apr 8, 2015

@author: giovanni
'''

from lightwidgets.geometry import Point, Rectangle
import math
from lightwidgets.support import rgb_to_gtk
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.stock_widgets.root import MainWindow, Root

class WidgetDebug(Widget):
    
    def __init__(self,
                 width,
                 height,
                 background_color=None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.font_size = 10
        self.clip_rectangle = Rectangle(Point(0,0),
                                        width,
                                        height)
        self._text = ""
        self._background_color=background_color
    
    @property
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self, value):
        if value is None:
            self._background_color = None
        else:
            self._background_color = rgb_to_gtk(value)
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self,value):
        self._text = value
        self.invalidate()
    
    def on_draw(self, widget, context):
        def split_every(string,nth):
            return [string[i:i+nth] for i in range(0,len(string),nth)]
        def split_in(string, times):
            nth = math.floor(len(string) / times)
            return split_every(string,nth)
        super().on_draw(widget, context)
        ext = context.text_extents("W")
        txt_height = math.ceil(ext[3])
        basic_lines = self.text.split(sep='\n')
        lines = []
        width = self.width
        for bline in basic_lines:
            ext = context.text_extents(bline)
            length = math.ceil(ext[2])
            if length > width:
                char_width = math.ceil(length/len(bline))
                max_chars = math.floor(width / char_width)
                for l in split_every(bline,max_chars):
                    lines.append(l)
            else:
                lines.append(bline)
                
        context.set_font_size(self.font_size)
        context.rectangle(.5, .5,
                          self.width - 1,
                          self.height - 1)
        if not self.background_color is None:
            context.set_source_rgb(*self.background_color)
            context.fill_preserve()
        context.set_source_rgb(0,0,0)
        context.stroke()
        context.move_to(.5,txt_height + .5)
        for i,line in enumerate(lines):
            context.move_to(.5, txt_height * (i+1) + .5)
            context.show_text(line)

if __name__ == '__main__':
    main_win = MainWindow(title="Debug test")
    root = Root(100, 100)
    main_win.add(root)
    debug = WidgetDebug(70,50)
    debug.translate(10,10)
    root.set_child(debug)
    main_win.start_main()