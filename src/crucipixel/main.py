'''
Created on Feb 22, 2015

@author: giovanni
'''

from crucipixel.interface.puzzle_stage.complete import MainArea
from lightwidgets.debug import WidgetDebug
from crucipixel.interface import global_constants
from lightwidgets.support import gtk_to_rgb
from gi.overrides import Gdk
from gi.overrides.Gtk import Gtk
from crucipixel import core
from crucipixel.interface.main_menu import MainMenu
from lightwidgets.stock_widgets.root import MainWindow, Root

#DRAFT-2015

class CustomDebug(WidgetDebug):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_color = gtk_to_rgb(global_constants._background)
        def handle_set_text(value):
            self.text = value
        self.register_signal("debug_text",handle_set_text)


        

if __name__ == '__main__':
    win = MainWindow(title="CompleteCrucipixel Dev")
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    root = Root()

    main_area = MainArea(min_size=(500,500))
    debug = CustomDebug(width=100,height=30)
    debug.translate(200,10)
    main_area.add(debug,top=-1)
    main_area.translate(.5,.5)
    with open("test.tmp","r") as f:
        cruci = core.Crucipixel.guides_from_file(f)
    main_area.start_crucipixel(cruci)
    main_area.start_selector()
    root.register_switch_to("new_scheme", main_area)
#     root.set_child(main_area)

    print(gtk_to_rgb(global_constants._start_default))
    entries=["New Game",
             "Options",
             "Exit"]
    root.set_child(MainMenu(button_width=100,button_height=30,
                            entries=entries,
                            broadcasts=["new_scheme"]))
    root.set_main_window(win)
    root.grab_focus()
    global_constants.global_animator.start()
    win.start_main()