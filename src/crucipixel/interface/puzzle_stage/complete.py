'''
Created on May 19, 2015

@author: giovanni
'''
import copy

import cairo

from crucipixel.data.json_parser import parse_file_name
from crucipixel.interface.puzzle_stage.buttons import GridButtons
from crucipixel.interface.puzzle_stage.navigator import Navigator
from crucipixel.logic import core
from lightwidgets.events import KeyboardEvent, MouseEvent, MouseButton
from lightwidgets.geometry import Point
from gi.repository import Gdk

from lightwidgets.stock_widgets.buttons import click_left_button_wrapper
from lightwidgets.stock_widgets.overlay import TextOverlay
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget
from lightwidgets.support import Bunch
from lightwidgets.animator import AccMovement
from crucipixel.interface import global_constants
from crucipixel.interface.puzzle_stage.guides import Guides, BetterGuide, \
    Orientation, GuideStatus
from crucipixel.interface.puzzle_stage.grid import CrucipixelGrid, \
    CrucipixelGridWonWrapper
from crucipixel.interface.puzzle_stage.selector import Selector, BetterSelector
from lightwidgets.stock_widgets.containers import UncheckedContainer


def gdk_color(*args):
    if len(args) == 1:
        r, g, b = args[0]
    else:
        r, g, b = args
    return Gdk.Color.from_floats(r, g, b) 


class CompleteCrucipixel(UncheckedContainer):

    def _init_guides(self, crucipixel: core.Crucipixel):
        self.horizontal_guide = BetterGuide(
            elements=crucipixel.scheme.cols,
            cell_size=self.cell_size,
            orientation=Orientation.HORIZONTAL
        )
        self.vertical_guide = BetterGuide(
            elements=crucipixel.scheme.rows,
            cell_size=self.cell_size,
            orientation=Orientation.VERTICAL
        )
        # def on_won_change(value: bool):
        #     self.horizontal_guide.visible = not value
        #     self.vertical_guide.visible = not value
        # crucipixel.on_won_change_callbacks_list.append(on_won_change)
        # self.horizontal_guide.visible = not crucipixel.is_won
        # self.vertical_guide.visible = not crucipixel.is_won
        self.add(self.horizontal_guide)
        self.add(self.vertical_guide)

    def __init__(self,
                 crucipixel: core.Crucipixel,
                 start=Point(0,0),
                 cell_size=15,
                 *args, **kwargs):
        super().__init__(*args,**kwargs)
        print("Starting at", start)
        self.translate(start.x,start.y)
        self.cell_size = cell_size
        self.grid = CrucipixelGrid(crucipixel, cell_size, cell_size)
        self.add(self.grid)

        self._init_guides(crucipixel)

        def update_guide(orientation: Orientation, index: int,
                         status: GuideStatus):
            if orientation == Orientation.HORIZONTAL:
                guide = self.horizontal_guide
            else:
                guide = self.vertical_guide
            guide.change_status(index, status)

        self.grid.on_guide_update = update_guide
        self.grid.refresh_guides()


        self._current_scale = Point(1, 1)
        self._direction_animations = {}
        self._movement = dict(global_constants.global_movement_keys)

    def _update_scale(self):
        self.scale(self._current_scale.x,self._current_scale.y)
        self.invalidate()

    def save(self):
        self.grid.save()

    def load(self):
        self.grid.load()

    def undo(self):
        self.grid.undo()

    def handle_selector(self, index: int, button: MouseButton):
        self.grid.handle_selector(index, button)

    @property
    def is_destroyed(self) -> bool:
        return self.grid.is_destroyed

    @is_destroyed.setter
    def is_destroyed(self, value: bool):
        self.grid.is_destroyed = value

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

    # def on_mouse_enter(self):
    #     super().on_mouse_enter()
    #
    # def on_mouse_exit(self):
    #     return super().on_mouse_exit()
        
class PuzzleScreen(UncheckedContainer):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.ID = "MainArea"
        self.crucipixel = None
        self.grid = None
        self.selector = None
        self._mouse_down = False
        self._click_point = Point(0,0)
        # self.counter = 0
        self.navigator = None
        self.buttons = None

    def start_all(self, crucipixel: core.Crucipixel):
        self.start_crucipixel(crucipixel)
        self.start_selector()
        self.start_navigator()
        self.start_buttons()
        self.buttons.on_save_action = click_left_button_wrapper(lambda: self.crucipixel.save())
        self.buttons.on_load_action = click_left_button_wrapper(lambda: self.crucipixel.load())
        self.buttons.on_undo_action = click_left_button_wrapper(lambda: self.crucipixel.undo())

        def create_lambda(index):
            return lambda button: self.crucipixel.handle_selector(index, button)

        for i in range(3):
            self.selector.set_click_action(
                i,
                create_lambda(i)
            )

        overlay = TextOverlay("PUZZLE SOLVED")

        def overlay_action():
            overlay.visible = False
        overlay.on_click_action = overlay_action
        self.add(overlay, top=-10)

        def update_win_status(is_won: bool):
            if is_won:
                overlay.visible = True
                self.grid.visible = True
                self.crucipixel.visible = False
                self.crucipixel.grid.victory_screen = True
                self.buttons.set_edit()
            else:
                self.grid.visible = False
                self.crucipixel.visible = True
                self.crucipixel.grid.victory_screen = False
                overlay.visible = False
                self.buttons.set_undo()
                print("Hi!")
        update_win_status(crucipixel.is_won)
        self.buttons.on_edit_action = click_left_button_wrapper(lambda: update_win_status(False))

        crucipixel.on_won_change_callbacks_list.append(update_win_status)

    def start_buttons(self):
        self.buttons = GridButtons()
        self.buttons.ID = "GridButtons"
        self.add(self.buttons, top=-1)

    def start_navigator(self):
        self.navigator = Navigator()
        self.navigator.scale(.7,.7)
        self.navigator.ID = "Navigator"
        self.add(self.navigator, top=-1)
    
    def start_selector(self,start=Point(0,0)):
        self.selector = BetterSelector()
        # self.selector.translate(.5, .5)
        self.selector.ID = "Selector"
        self.add(self.selector, top=-1)
    
    def start_crucipixel(self,crucipixel: core.Crucipixel,
                         start=Point(120,100),cell_size=20):
        self.crucipixel = CompleteCrucipixel(crucipixel, start, cell_size)
        self.crucipixel.ID="CompleteCrucipixel"
        self.grid = CrucipixelGridWonWrapper(self.crucipixel.grid, crucipixel)
        self.add(self.crucipixel)
        self.add(self.grid)

    def on_mouse_down(self, widget, event: MouseEvent):
        if 'ctrl' in event.modifiers:
            handled = False
        else:
            handled = super().on_mouse_down(widget, event)
        if not handled:
            self._mouse_down = True
            self._click_point = Point(event.x, event.y)
            self._translate_vector = Point(self.crucipixel.fromWidgetCoords.transform_point(0,0))
    
    def on_mouse_move(self, w, e):
        if self._mouse_down:
            delta_x = int(e.x - self._click_point.x)
            delta_y = int(e.y - self._click_point.y)
            self.crucipixel.set_translate(self._translate_vector.x + delta_x,
                                          self._translate_vector.y + delta_y)
            self.invalidate()
        super().on_mouse_move(w,e)
    
    def on_mouse_up(self, widget, event):
        if self._mouse_down:
            self._mouse_down = False
        super().on_mouse_up(widget, event)

    def on_draw(self, widget: Widget, context: cairo.Context):
        selector_width = self.selector.width
        self.grid.left_padding = selector_width + 10
        buttons_width, buttons_height = self.buttons.get_width_height(context)
        self.grid.upper_padding = buttons_height + 30

        self.min_size = selector_width + buttons_width + 10, 100

        super().on_draw(widget, context)

    def set_quit_button_callback(self, value):
        if self.buttons is not None:
            def on_quit_action(button: MouseButton):
                self.is_destroyed = True
                value(button)
            self.buttons.on_quit_action = on_quit_action

    @property
    def is_destroyed(self) -> bool:
        return self.crucipixel.is_destroyed

    @is_destroyed.setter
    def is_destroyed(self, value: bool):
        self.crucipixel.is_destroyed = value


def main() -> int:
    crucipixel_model = parse_file_name("../data/monopattino.json")
    crucipixel_core = core.Crucipixel(crucipixel_model)
    # cruci_core = core.Crucipixel(
    #     len(cruci_scheme.rows),
    #     len(cruci_scheme.cols),
    #     cruci_scheme.rows,
    #     cruci_scheme.cols
    # )
    complete = PuzzleScreen()
    complete.start_crucipixel(crucipixel_core)
    complete.start_selector()
    complete.start_navigator()

    main_area = MainWindow(title="Complete")
    root = Root()
    root.set_child(complete)
    main_area.add(root)
    main_area.start_main()

if __name__ == '__main__':
    main()
