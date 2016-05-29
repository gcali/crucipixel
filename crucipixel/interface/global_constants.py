"""
Created on May 19, 2015

@author: giovanni
"""

from lightwidgets.support import rgb_to_gtk
from lightwidgets.animator import Animator
from lightwidgets.geometry import Point

background = (.9, .9, .9)
start_selected = (.3, .3, .3)
start_default = rgb_to_gtk(25, 25, 112)
start_default = (.8, .8, .8)
start_empty = rgb_to_gtk((240, 255, 240))
highlight = rgb_to_gtk(255, 255, 0)
highlight = rgb_to_gtk(70, 130, 180)

_keys_r = {
    "up": ["w", "k", "up"],
    "down": ["s", "j", "down"],
    "left": ["a", "h", "left"],
    "right": ["d", "l", "right"],
    "up_left": ["y", "q"],
    "down_left": ["b", "z"],
    "up_right": ["u", "e"],
    "down_right": ["n", "c"]
}

global_movement_keys = {}
for (k, v) in _keys_r.items():
    for e in v:
        global_movement_keys[e] = k
del _keys_r 

menu_button_dim = Point(100, 30)
