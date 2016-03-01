'''
Created on Feb 22, 2015

@author: giovanni
'''

from gi.overrides.Gtk import Gtk
from gi.repository import Gdk

from crucipixel.data import json_parser
from crucipixel.interface import global_constants
from crucipixel.interface.main_menu import MainMenu
from crucipixel.interface.puzzle_stage.complete import MainArea
from crucipixel.logic import core
from lightwidgets.debug import WidgetDebug
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.support import gtk_to_rgb


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
    # with open("test.tmp","r") as f:
    #     cruci = core.Crucipixel.guides_from_file(f)
    #     print(cruci.row_guides)
    cruci_scheme = json_parser.parse_file_name("../data/uccellino.json")
    cruci = core.Crucipixel(
        len(cruci_scheme.rows),
        len(cruci_scheme.cols),
        cruci_scheme.rows,
        cruci_scheme.cols
    )
    main_area.start_crucipixel(cruci)
    main_area.start_selector()
    main_area.start_navigator()
    root.register_switch_to("new_scheme", main_area)

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