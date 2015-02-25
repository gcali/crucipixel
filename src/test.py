#!/usr/bin/python3

#from gi.repository import Gtk
 
from lightwidgets import *


def main():
    win = MainWindow("Hello world!")
    root = Root()
    root.set_min_size(500,500)
    win.add(root)
    donut = Donut(Point((250,250),),100,200,iters=36)
    root.set_child(donut)
    win.start_main()

if __name__ == '__main__':
    main()