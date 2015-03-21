'''
Created on Feb 25, 2015

@author: giovanni
'''
from operator import __setitem__

def get_step(a,b):
    if b >= a:
        return 1
    else:
        return -1

def get_from_to_inclusive(a,b):
    for i in range(a,b,get_step(a,b)):
        yield i
    yield b
    
def rgb_to_gtk(rgb:"tuple"):
    def to_perc(n):
        return n/255
    r,g,b = rgb
    return (to_perc(r),
            to_perc(g),
            to_perc(b))

def gtk_to_rgb(rgb:"tuple"):
    def from_perc(n):
        return (n*255)
    r,g,b = rgb
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
   
if __name__ == '__main__':
    d = DefaultDict()
    d.default = "Ciao!"
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