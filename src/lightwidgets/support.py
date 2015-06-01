'''
Created on Feb 25, 2015

@author: giovanni
'''
import types
from lightwidgets.geometry import Point

def add_method(obj, name, method):
    setattr(obj,name,types.MethodType(method,obj))

def get_step(a,b):
    if b >= a:
        return 1
    else:
        return -1

def get_from_to_inclusive(a,b):
    for i in range(a,b,get_step(a,b)):
        yield i
    yield b
    
def rgb_to_gtk(*args):
    """Takes either a tuple of the form (r,g,b) or
       three arguments, r,g,b
    """
    if len(args) == 1:
        r,g,b = args[0]
    elif len(args) == 3:
        r,g,b = args
    def to_perc(n):
        return n/255
    return (to_perc(r),
            to_perc(g),
            to_perc(b))

def gtk_to_rgb(*args):
    """Takes either a tuple of the form (r,g,b) or
       three arguments, r,g,b
    """
    if len(args) == 1:
        r,g,b = args[0]
    elif len(args) == 3:
        r,g,b = args
    def from_perc(n):
        return (n*255)
    return (from_perc(r),
            from_perc(g),
            from_perc(b))

class DefaultDict(dict): 
    
    @property
    def default(self):
        return self._default_calculator()
    @default.setter
    def default(self,value):
        self._default_calculator = value

    def __missing__(self,key):
        try:
            return self.default
        except AttributeError:
            raise KeyError(str(key))
    
    def __setitem__(self,key,value):
        if not hasattr(self, "default"):
            print("I shouldn't happen! {} {}".format(key,value))
            super().__setitem__(key, value)
        elif value == self.default:
            if key in self:
                del self[key]
        else:
            super().__setitem__(key,value)

def clamp(value:"num",min_v:"num",max_v:"num") -> "num":
    if value < min_v:
        return min_v
    elif value > max_v:
        return max_v
    else:
        return value


x_factor = .505
y_factor = .9

_char_size_data = {
  ' ' : [0.55,0.7407531110970528,0],
  '!' : [0.27678538523739765,0.7457636343704455,0],
  "'" : [0.21324157825318818,0.7457636343704455,0],
  ',' : [0.25765516904835795,0.16045534702655445,0],
  '-' : [0.34866252555494043,0.34005913333312715,0],
  '.' : [0.24524915401076391,0.16045534702655445,0],
  ';' : [0.25765516904835795,0.5714230059586096,0],
  '<' : [0.7685785971854084,0.6442687609947672,0],
  '>' : [0.7685785971854084,0.6442687609947672,0],
  '?' : [0.49179321194801073,0.7457636343704455,0],
  '@' : [0.9703822669418646,0.7452529827413729,0],
  '_' : [0.5545794431746444,-0.15667094730175224,0], 
  '0' : [0.591591906806251,0.7407531110970528,0],
  '1' : [0.5675007380987719,0.7381203163589948,0],
  '2' : [0.5595577126557464,0.7407531110970528,0],
  '3' : [0.5818371930870232,0.7407531110970528,0],
  '4' : [0.6026267491568827,0.7381203163589948,0],
  '5' : [0.5741315624715316,0.7381203163589948,0],
  '6' : [0.597703017917362,0.7407531110970528,0],
  '7' : [0.5757982291381982,0.7381203163589948,0],
  '8' : [0.5915919068062508,0.7407531110970528,0],
  '9' : [0.5895798947942389,0.7407531110970528,0],
  'A' : [0.6977351411175712,0.7381203163589948,0],
  'B' : [0.6374313399226605,0.7381203163589948,0],
  'C' : [0.6694346865978651,0.7407531110970528,0],
  'D' : [0.7352043132901904,0.7381203163589948,0],
  'E' : [0.5915919068062508,0.7381203163589948,0],
  'F' : [0.5407396516498431,0.7381203163589948,0],
  'G' : [0.714725801355358,0.7407531110970528,0],
  'H' : [0.6774679748155439,0.7381203163589948,0],
  'I' : [0.21892480571742706,0.7381203163589948,0],
  'J' : [0.21892480571742706,0.7381203163589948,0],
  'K' : [0.6996164341753348,0.7381203163589948,0],
  'L' : [0.5757982291381982,0.7381203163589948,0],
  'M' : [0.7876357170930957,0.7381203163589948,0],
  'N' : [0.6743520327865584,0.7381203163589948,0],
  'O' : [0.754928784777593,0.7407531110970528,0],
  'P' : [0.5915919068062508,0.7381203163589948,0],
  'Q' : [0.754928784777593,0.7407531110970528,0],
  'R' : [0.6827706919864553,0.7381203163589948,0],
  'S' : [0.5999951702095143,0.7407531110970528,0],
  'T' : [0.6374313399226608,0.7381203163589948,0],
  'U' : [0.6694346865978651,0.7381203163589948,0],
  'V' : [0.6977351411175712,0.7381203163589948,0],
  'W' : [0.9812423403760299,0.7381203163589948,0],
  'X' : [0.6774679748155441,0.7381203163589948,0],
  'Y' : [0.6363560711054564,0.7381203163589948,0],
  'Z' : [0.6636752238384025,0.7381203163589948,0],
  'a' : [0.5444569781717672,0.5677248304281274,0],
  'b' : [0.6026267491568827,0.770218779220569,0],
  'c' : [0.5115395270510491,0.5677248304281274,0],
  'd' : [0.5675007380987719,0.770218779220569,0],
  'e' : [0.5841509185772191,0.5677248304281274,0],
  'f' : [0.3952693417683975,0.770218779220569,0],
  'g' : [0.5675007380987719,0.5677248304281274,0],
  'h' : [0.5741315624715315,0.770218779220569,0],
  'i' : [0.2079165963203523,0.770218779220569,0],
  'j' : [0.20791659632035234,0.770218779220569,0],
  'k' : [0.598713118927463,0.770218779220569,0],
  'l' : [0.2079165963203523,0.770218779220569,0],
  'm' : [0.9094442511291063,0.5677248304281274,0],
  'n' : [0.5741315624715315,0.5677248304281274,0],
  'o' : [0.581837193087023,0.5677248304281274,0],
  'p' : [0.6026267491568827,0.5677248304281274,0],
  'q' : [0.5675007380987719,0.5677248304281274,0],
  'r' : [0.43460061384097987,0.5899294912357292,0],
  's' : [0.4964347661709221,0.5677248304281274,0],
  't' : [0.39140319491979453,0.7254378416954519,0],
  'u' : [0.5665483571463907,0.6125778618556733,0],
  'v' : [0.5841509185772192,0.5650920356900695,0],
  'w' : [0.7989512685035239,0.5650920356900695,0],
  'x' : [0.582817585243886,0.5650920356900695,0],
  'y' : [0.5841509185772192,0.5650920356900695,0],
  'z' : [0.5055967492284047,0.5650920356900695,0]}

def char_size(font_size):
    return Point(font_size * x_factor, font_size * y_factor)

class StringSize:
    
    def __init__(self, width, 
                       height, 
                       lower):
        self.width = width
        self.height = height
        self.lower = lower
    
    @property
    def x(self):
        return self.width
    @property
    def y(self):
        return self.height

def string_size(font_size, string):
    max_height = 0.0
    max_lower = 0.0
    width = 0.0
    for c in string:
        try:
            size = _char_size_data[c]
        except KeyError:
            size = _char_size_data[' ']
        max_height = max(max_height, size[1])
        max_lower = max(max_lower,size[2])
        width += size[0]
    return StringSize(width*font_size,max_height*font_size,max_lower*font_size)

#Code from
#http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/
class Bunch:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

   
if __name__ == '__main__':
    d = DefaultDict()
    d.default = lambda: "Ciao!"
    print("Items at start:")
    print(d)
    print(d[12])
    d[12] = "Cane!"
    print(d[12])
    print("Items after cane:")
    print(d)
    d[12] = "Ciao!"
    print(d[12])
    print("Items after ciao:")
    print(d)