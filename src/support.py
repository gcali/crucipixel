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

class DefaultDict(dict): 
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