'''
Created on Mar 27, 2015

@author: giovanni
'''

from general.geometry import Point

def get_speed_from_uniform_acceleration(start_speed:"Point",
                                        acc:"Point",
                                        time:"Point"):
    return Point(start_speed.x + time*(acc.x),
                 start_speed.y + time*(acc.y))

def get_position_from_uniform_acceleration(start_position:"Point",
                                           start_speed:"Point",
                                           acc:"Point",
                                           time:"sec"):
    def single_coord(pos,
                     speed,
                     acc,
                     time):
        return pos + time*(speed + (time*acc)/2)
    return Point(single_coord(start_position.x,
                              start_speed.x,
                              acc.x,
                              time),
                 single_coord(start_position.y,
                              start_speed.y,
                              acc.y,
                              time))

def get_position_from_uniform_speed(start_position:"Point",
                                    speed:"Point",
                                    time:"sec"):
    def single_coord(pos,
                     speed,
                     time):
        return pos + time*speed
    return Point(single_coord(start_position.x,
                              speed.x,
                              time),
                 single_coord(start_position.y,
                              speed.y,
                              time))
    

if __name__ == '__main__':
    pass