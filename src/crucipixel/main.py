'''
Created on Feb 22, 2015

@author: giovanni
'''
from typing import List

from gi.overrides.Gtk import Gtk
from gi.repository import Gdk

from crucipixel.data import json_parser, storage
from crucipixel.data.complete_model import CrucipixelCompleteModel
from crucipixel.interface import global_constants
from crucipixel.interface.main_menu import MainMenu, BetterMainMenu
from crucipixel.interface.puzzle_chooser.chooser_table import ChooserTable, \
    scheme_to_entry
from crucipixel.interface.puzzle_stage.complete import PuzzleScreen
from crucipixel.logic import core
from lightwidgets.debug import WidgetDebug
from lightwidgets.stock_widgets.buttons import click_left_button_wrapper
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.support import gtk_to_rgb


class CustomDebug(WidgetDebug):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_color = gtk_to_rgb(global_constants.background)
        def handle_set_text(value):
            self.text = value
        self.register_signal("debug_text", handle_set_text)


def create_new_game(root: Root) -> None:
    def new_game() -> None:
        models = storage.get_models()
        chooser = ChooserTable([scheme_to_entry(model.scheme)
                                for model in models])
        chooser.set_contents_callback(create_load_model(root, models))
        chooser.set_back_callback(click_left_button_wrapper(create_main_menu(root)))

        chooser.translate(50, 50)
        root.set_min_size(400, 200)
        root.set_child(chooser)
    return new_game


def create_load_model(root: Root, models: List[CrucipixelCompleteModel]) \
        -> None:

    def load_model(index: int) -> None:
        model = models[index]
        core_crucipixel = core.Crucipixel(model)
        puzzle_screen = PuzzleScreen(min_size=(500, 500))
        puzzle_screen.translate(.5, .5)
        puzzle_screen.start_all(core_crucipixel)
        puzzle_screen.set_quit_button_callback(click_left_button_wrapper(create_new_game(root)))
        root.set_child(puzzle_screen)
    return load_model

def create_main_menu(root: Root) -> None:
    def main_menu() -> None:
        main_menu = BetterMainMenu(
            "Crucipixel GTK",
            [
                "New game",
                "Create level",
                "Options",
                "Exit"
            ], [
                click_left_button_wrapper(lambda: print("New game!")),
                click_left_button_wrapper(lambda: print("Create level!")),
                click_left_button_wrapper(lambda: None),
                click_left_button_wrapper(lambda: Gtk.main_quit())
            ])
        main_menu.set_callback(0, click_left_button_wrapper(create_new_game(root)))

        root.set_child(main_menu)
    return main_menu


def main() -> int:

    win = MainWindow(title="CrucipixelGTK")
    win.connect("delete-event", lambda *args: Gtk.main_quit)
    print(Gdk.RGBA)
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.9,.9,.9,1))
    root = Root()

    from lightwidgets.events import MouseButton
    create_main_menu(root)()

    root.set_main_window(win)
    win.start_main()

    return 0
        

if __name__ == '__main__':
    from sys import exit
    exit(main())
