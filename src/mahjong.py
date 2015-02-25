'''
Created on Feb 22, 2015

@author: giovanni
'''

import lightwidgets as lw
from geometry import Point
import cairo

def set_blue(c):
    c.set_source_rgb(.1,.1,.8)
def set_black(c):
    c.set_source_rgb(0,0,0)

class Tile(lw.Widget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.bottom_left = Point(250.5,250.5)
        self.height = 20
        self.width = 80
        self.depth = 80
    
    def on_draw(self,w,c):
        c.set_line_join(cairo.LINE_JOIN_MITER)
        s = self.bottom_left
        h = self.height
        w = self.width
        d=self.depth
        co=1.4
        c.set_line_width(.3)
        set_blue(c)
        c.move_to(s.x,s.y)
        c.line_to(s.x,s.y-h)
        c.line_to(s.x+w,s.y-h)
        c.line_to(s.x+w,s.y)
        c.close_path()
        c.fill_preserve()
        set_black(c)
        c.stroke()
        c.move_to(s.x,s.y-h)
        c.line_to(s.x+w*.45,s.y-h-d)
        c.line_to(s.x+w*co,s.y-h-d)
        c.line_to(s.x+w,s.y-h)
        c.stroke()
        c.move_to(s.x+w,s.y)
        c.line_to(s.x+w*co,s.y-d)
        c.line_to(s.x+w*co,s.y-h-d)
        c.stroke()



if __name__ == '__main__':
    win = lw.MainWindow(title="Mahjong Test")
    root = lw.Root(500,500)
    win.add(root)
    tile = Tile()
    root.set_child(tile)
    win.start_main()