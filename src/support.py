'''
Created on Feb 25, 2015

@author: giovanni
'''

def get_step(a,b):
    if b >= a:
        return 1
    else:
        return -1

def get_from_to_inclusive(a,b):
    for i in range(a,b,get_step(a,b)):
        yield i
    yield b

if __name__ == '__main__':
    pass