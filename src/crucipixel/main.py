'''
Created on Feb 22, 2015

@author: giovanni
'''
from typing import List

from gi.overrides.Gtk import Gtk
from gi.repository import Gdk

from crucipixel.data import json_parser, storage
from crucipixel.data.crucipixel_scheme import CrucipixelScheme
from crucipixel.interface import global_constants
from crucipixel.interface.main_menu import MainMenu, BetterMainMenu
from crucipixel.interface.puzzle_chooser.chooser_table import ChooserTable, \
    scheme_to_entry
from crucipixel.interface.puzzle_stage.complete import PuzzleScreen
from crucipixel.logic import core
from crucipixel.logic.core import scheme_to_core
from lightwidgets.debug import WidgetDebug
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.support import gtk_to_rgb


class CustomDebug(WidgetDebug):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_color = gtk_to_rgb(global_constants._background)
        def handle_set_text(value):
            self.text = value
        self.register_signal("debug_text", handle_set_text)


def create_new_game(root: Root) -> None:
    def new_game() -> None:
        schemes = storage.get_schemes()
        chooser = ChooserTable([scheme_to_entry(scheme) for scheme in schemes])
        chooser.set_contents_callback(create_load_scheme(root, schemes))
        chooser.set_back_callback(create_main_menu(root))

        chooser.translate(50, 50)
        root.set_min_size(400, 200)
        root.set_child(chooser)
    return new_game


def create_load_scheme(root: Root, schemes: List[CrucipixelScheme]) -> None:

    def load_scheme(index: int) -> None:
        scheme = schemes[index]
        core_crucipixel = scheme_to_core(scheme)
        puzzle_screen = PuzzleScreen(min_size=(500, 500))
        puzzle_screen.translate(.5, .5)
        puzzle_screen.start_all(core_crucipixel)
        # puzzle_screen.start_crucipixel(core_crucipixel)
        # puzzle_screen.start_navigator()
        # puzzle_screen.start_selector()
        root.set_child(puzzle_screen)
    return load_scheme

def create_main_menu(root: Root) -> None:
    def main_menu() -> None:
        main_menu = BetterMainMenu(
            [
                "New game",
                "Create level",
                "Options",
                "Exit"
            ], [
                lambda: print("New game!"),
                lambda: print("Create level!"),
                lambda: win.destroy()
            ])
        main_menu.set_callback(0, create_new_game(root))

        root.set_child(main_menu)
    return main_menu


def main() -> int:

    win = MainWindow(title="CrucipixelGTK")
    win.connect("delete-event", lambda *args: Gtk.main_quit)
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    root = Root()

    create_main_menu(root)()

    root.set_main_window(win)
    win.start_main()

    return 0
        

if __name__ == '__main__':
    from sys import exit
    exit(main())

    win = MainWindow(title="CompleteCrucipixel Dev")
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    root = Root()

    main_area = PuzzleScreen(min_size=(500, 500))
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