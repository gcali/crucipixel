'''
Created on May 19, 2015

@author: giovanni
'''

from lightwidgets.geometry import Point
from gi.overrides import Gdk
from lightwidgets.support import Bunch
from lightwidgets.animator import AccMovement
from crucipixel.interface import global_constants
from crucipixel.interface.puzzle_stage.guides import Guides
from crucipixel.interface.puzzle_stage.grid import CrucipixelGrid
from crucipixel.interface.puzzle_stage.selector import Selector
from lightwidgets.stock_widgets.containers import UncheckedContainer

def gdk_color(*args):
    if len(args) == 1:
        r,g,b = args[0]
    else:
        r,g,b = args
    return Gdk.Color.from_floats(r, g, b) 

class CompleteCrucipixel(UncheckedContainer): 

    def _init_guides(self, crucipixel):
        self.horizontal_guide = Guides(start=Point(0, 0), elements=crucipixel.row_guides, 
            size=self.cell_size, 
            orientation=Guides.HORIZONTAL)
        self.horizontal_guide.ID = "Horizontal Guide"
        self.vertical_guide = Guides(start=Point(0, 0), 
            elements=crucipixel.col_guides, 
            size=self.cell_size, 
            orientation=Guides.VERTICAL)
        self.vertical_guide.ID = "Vertical Guide"
        self.add(self.horizontal_guide)
        self.add(self.vertical_guide)

    def __init__(self,
                 crucipixel,
                 start=Point(0,0),
                 cell_size=15, 
                 *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.translate(start.x,start.y)
        self.cell_size = cell_size
        self.rows = crucipixel.rows
        self.cols = crucipixel.cols
        self.grid = CrucipixelGrid.from_crucipixel(crucipixel=crucipixel, 
                                                   start=Point(0,0),
                                                   cell_size=cell_size)
        self.grid.selection_style = CrucipixelGrid.SELECTION_RECTANGLE
        self.add(self.grid)

        self._init_guides(crucipixel)
        self._current_scale = Point(1,1)
        self._direction_animations = {}
        self._movement = dict(global_constants._global_movement_keys)

    def _update_scale(self):
        self.scale(self._current_scale.x,self._current_scale.y)
        self.invalidate()
    
    def on_key_down(self, w, e):
        if e.key == "=" or e.key == "+":
            self.zoom_in()
            return True
        elif e.key == "-":
            self.zoom_out()
            return True
        elif e.key in self._movement and "shift" in e.modifiers:
            self._handle_movement(self._movement[e.key])
        else:
            super().on_key_down(w,e)
    
    def on_key_up(self, w, e):
        if e.key in self._movement and "shift" in e.modifiers:
            self._stop_movement(self._movement[e.key])
        elif e.key.startswith("shift"):
            for m in self._movement.values():
                self._stop_movement(m)
        else:
            return super().on_key_up(w,e)

    def zoom_in(self):
        self.scale(1.5,1.5)
        self.invalidate()
    
    def zoom_out(self):
        self.scale((1/1.5),(1/1.5))
        self.invalidate()
    
    def _handle_movement(self,direction:"str"):
        def get_direction(direction):
            if direction == "left":
                coeff = Point(1,0)
            elif direction == "right":
                coeff = Point(-1,0)
            elif direction == "up":
                coeff = Point(0,1)
            elif direction == "down":
                coeff = Point(0,-1)
            else:
                raise NameError("Can't find direction", direction)
            return coeff
        if direction not in self._direction_animations:
            coeff = Point(0,0)
            for d in direction.split("_"):
                coeff += get_direction(d)
#             acc = Point(500 * coeff.x,
#                         500 * coeff.y)
            acc = Point(0,0)
            start_speed = Point(500 * coeff.x,
                                500 * coeff.y)
            store_pos = Bunch(v=Point(0,0))
            def assign(d):
                store_pos.v += d
                delta = Point(int(store_pos.v.x),
                              int(store_pos.v.y))
                store_pos.v -= delta
                self.translate(delta.x, delta.y)
            animation = AccMovement(assign=assign, 
                                    acc=acc, 
                                    start_position=Point(0,0), 
                                    duration=0, 
                                    start_speed=start_speed)
            animation.widget = self
            self._direction_animations[direction] = animation
            global_constants.global_animator.add_animation(animation)
    
    def _stop_movement(self,direction:"str"):
        try:
            self._direction_animations[direction].stop = True
            del self._direction_animations[direction]
        except KeyError:
            pass

    def move(self,offset_x=0,offset_y=0):
        self.translate(offset_x,offset_y)
        self.invalidate()
    
    def move_down(self,offset=10):
        return self.move(offset_y=offset)
    
    def move_up(self,offset=10):
        return self.move(offset_y=-offset)
    
    def move_left(self,offset=10):
        return self.move(offset_x=-offset)

    def move_right(self,offset=10):
        return self.move(offset_x=offset)
    
    def on_mouse_enter(self):
        super().on_mouse_enter()
        
    def on_mouse_exit(self):
        return super().on_mouse_exit()
        
class MainArea(UncheckedContainer):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "MainArea"
        self.core_crucipixel = None
        self.selector = None
        self._mouse_down = False
        self._click_point = Point(0,0)
        self.counter=0
    
    def start_selector(self,start=Point(0,0)):
        self.selector = Selector(start=start)
        self.selector.ID = "Selector"
        self.add(self.selector,top=-1)
    
    def start_crucipixel(self,crucipixel:"core.CompleteCrucipixel",
                         start=Point(120,100),cell_size=20):
        self.core_crucipixel = CompleteCrucipixel(crucipixel, start, cell_size)
        self.core_crucipixel.ID="CompleteCrucipixel"
        self.add(self.core_crucipixel)
    
    def on_mouse_down(self, w, e):
        handled = super().on_mouse_down(w, e)
        if not handled:
            self._mouse_down = True
            self._click_point = Point(e.x,e.y)
            self._translate_vector = Point(self.core_crucipixel.fromWidgetCoords.transform_point(0,0))
    
    def on_mouse_move(self, w, e):
        if self._mouse_down:
            delta_x = int(e.x - self._click_point.x)
            delta_y = int(e.y - self._click_point.y)
            self.core_crucipixel.set_translate(self._translate_vector.x + delta_x,
                                          self._translate_vector.y + delta_y)
            self.invalidate()
        super().on_mouse_move(w,e)
    
    def on_mouse_up(self,w,e):
        if self._mouse_down:
            self._mouse_down = False
        super().on_mouse_up(w,e) 

if __name__ == '__main__':
    pass