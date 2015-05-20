'''
Created on May 19, 2015

@author: giovanni
'''

from general import lightwidgets as lw
from general.lightwidgets import Button
from crucipixel.interface import global_constants
from gi.overrides.Gtk import Gtk
from gi.overrides import Gdk
from general.geometry import Point

class MainArea(lw.UncheckedContainer):

    def __init__(self, puzzle_list:"[(name,dim,path)]",*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.puzzle_list = list(puzzle_list)
        self.buttons = []
        self.paths = {}
        upper_padding = global_constants.menu_button_dim.y
        left_padding = upper_padding
        button_width = global_constants.menu_button_dim.x
        button_height = global_constants.menu_button_dim.y
        for (i,(name, dim, path)) in enumerate(self.puzzle_list):
            new_button = Button(label=name + " ({}x{})".format(dim.x,dim.y),
                                size_x=button_width,
                                size_y=button_height)
            new_button.set_translate(left_padding, upper_padding * (i+1))
            self.buttons.append(new_button)
            self.add(new_button)
            self.paths[name] = path
    
    def on_resize(self, new_father_dim):
        super().on_resize(new_father_dim)
        print(new_father_dim)

            

if __name__ == '__main__':
    win = lw.MainWindow(title="PuzzleChooser Dev")
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    root = lw.Root()

    main_area = MainArea(puzzle_list=[("Forbici", Point(20,20), "tmp.data")],min_size=(100,100))
    main_area.translate(.5,.5)
    root.set_child(main_area)

    root.set_main_window(win)
    root.grab_focus()
    global_constants.global_animator.start()
    win.start_main()
