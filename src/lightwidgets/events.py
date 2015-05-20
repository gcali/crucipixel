'''
Created on May 20, 2015

@author: giovanni
'''
from gi.overrides.Gdk import Gdk

def _transform_mouse_event(event_type,e,w):
    x,y=w.toWidgetCoords.transform_point(e.x,e.y)
    new_e = MouseEvent(event_type,x,y)
    try:
        if e.button == 1:
            new_e.button = "left"
        elif e.button == 2:
            new_e.button = "middle"
        elif e.button == 3:
            new_e.button = "right"
    except AttributeError:
        pass 
    return new_e

class MouseEvent:
    UNKNOWN =      0
    MOUSE_DOWN =   1
    MOUSE_UP =     2
    MOUSE_MOVE =   3
    
    def __init__(self, event_type, x, y, button=None):
        self.x = x
        self.y = y
        self.event_type = event_type
        self.button = button
    
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
                  Gdk.KEY_space : "space"}
    if e.keyval in control_keys:
        key = control_keys[e.keyval]
    else:
        key = chr(Gdk.keyval_to_unicode(e.keyval)).lower()
    modifiers = _get_modifiers(e)
    return KeyboardEvent(event_type=event_type,
                         key=key,
                         modifiers=modifiers)
    

class KeyboardEvent:
    UNKNOWN  = 0
    KEY_DOWN = 1
    KEY_UP   = 2
    
    def __init__(self, event_type, key, modifiers=[]):
        self.event_type = event_type
        self.key = key
        self.modifiers = modifiers
