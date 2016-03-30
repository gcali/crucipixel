'''
Created on May 20, 2015

@author: giovanni
'''
from enum import Enum, unique

from gi.repository import Gdk

def _transform_mouse_event(event_type,e,w):
    x,y=w.toWidgetCoords.transform_point(e.x,e.y)
    new_e = MouseEvent(event_type,x,y)
    if e.state & Gdk.ModifierType.CONTROL_MASK:
        new_e.modifiers.append('ctrl')
    try:
        if e.button == 1:
            new_e.button = MouseButton.LEFT
        elif e.button == 2:
            new_e.button = MouseButton.MIDDLE
        elif e.button == 3:
            new_e.button = MouseButton.RIGHT
    except AttributeError:
        pass
    return new_e

class MouseButton(Enum):

    LEFT = 0
    RIGHT = 1
    MIDDLE = 2
    UNKNOWN = 3


class MouseEventCategory(Enum):
    UNKNOWN = 0
    MOUSE_DOWN = 1
    MOUSE_UP = 2
    MOUSE_MOVE = 3


class MouseEvent:
    UNKNOWN =    MouseEventCategory.UNKNOWN
    MOUSE_DOWN = MouseEventCategory.MOUSE_DOWN
    MOUSE_UP =   MouseEventCategory.MOUSE_UP
    MOUSE_MOVE = MouseEventCategory.MOUSE_MOVE

    def __init__(self, event_type, x, y, button=None):
        self.x = x
        self.y = y
        self.event_type = event_type
        self.button = button
        self.modifiers = []
    
    def __copy__(self):
        return MouseEvent(self.event_type,self.x,self.y,self.button)
    
def _get_modifiers(event):
    state = event.state
    modifiers = []
    if state & Gdk.ModifierType.SHIFT_MASK:
        modifiers.append("shift")
    elif state & Gdk.ModifierType.CONTROL_MASK:
        modifiers.append("ctrl")
    elif state & Gdk.ModifierType.MOD1_MASK:
        modifiers.append("alt")
    return modifiers

def _transform_keyboard_event(event_type,e):
    event_type = event_type
    control_keys = { Gdk.KEY_Shift_L : "shift_l",
                  Gdk.KEY_Shift_R : "shift_r",
                  Gdk.KEY_Control_L : "ctrl_l",
                  Gdk.KEY_Control_R : "ctrl_r",
                  Gdk.KEY_Alt_L : "alt_l",
                  Gdk.KEY_Alt_R : "alt_r",
                  Gdk.KEY_Down : "down",
                  Gdk.KEY_Up : "up",
                  Gdk.KEY_Left : "left",
                  Gdk.KEY_Right : "right",
                  Gdk.KEY_space : "space",
                  Gdk.KEY_BackSpace : "backspace"
                }
    # control_keys = { Gdk.KEY_Shift_L : KeyboardValue.SHIFT_L,
    #               Gdk.KEY_Shift_R : KeyboardValue.SHIFT_R,
    #               Gdk.KEY_Control_L : KeyboardValue.CTRL_L,
    #               Gdk.KEY_Control_R : KeyboardValue.CTRL_R,
    #               Gdk.KEY_Alt_L : KeyboardValue.ALT_L,
    #               Gdk.KEY_Alt_R : KeyboardValue.ALT_R,
    #               Gdk.KEY_Down : KeyboardValue.DOWN,
    #               Gdk.KEY_Up : KeyboardValue.UP,
    #               Gdk.KEY_Left : KeyboardValue.LEFT,
    #               Gdk.KEY_Right : KeyboardValue.RIGHT,
    #               Gdk.KEY_space : KeyboardValue.SPACE,
    #               Gdk.KEY_BackSpace : KeyboardValue.BACKSPACE
    #             }
    if e.keyval in control_keys:
        key = control_keys[e.keyval]
    else:
        key = chr(Gdk.keyval_to_unicode(e.keyval)).lower()

    modifiers = _get_modifiers(e)
    return KeyboardEvent(event_type=event_type,
                         key=key,
                         modifiers=modifiers)


@unique
class KeyboardValue(Enum):
    SHIFT_L = 0
    SHIFT_R = 1
    CTRL_L = 2
    CTRL_R = 3
    ALT_L = 4
    ALT_R = 5
    DOWN = 6
    UP = 7
    LEFT = 8
    RIGHT = 9
    SPACE = 10
    BACKSPACE = 11
    A = 12
    B = 13
    C = 14
    D = 15
    E = 16
    F = 17
    G = 18
    H = 19
    I = 20
    J = 21
    K = 22
    L = 23
    M = 24
    N = 25
    O = 26
    P = 27
    Q = 28
    R = 29
    S = 30
    T = 31
    U = 32
    V = 33
    W = 34
    X = 35
    Y = 36
    Z = 37
    ZERO = 38
    ONE = 39
    TWO = 40
    THREE = 41
    FOUR = 42
    FIVE = 43
    SIX = 44
    SEVEN = 45
    EIGHT = 46
    NINE = 47
    UNKNOWN = 48


class KeyboardEvent:
    UNKNOWN  = 0
    KEY_DOWN = 1
    KEY_UP   = 2
    
    def __init__(self, event_type, key: str, modifiers=[]):
        self.event_type = event_type
        self.key = key
        self.modifiers = modifiers
