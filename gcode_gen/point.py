'''
A basic base class for point and point lists
'''
import numpy as np


class PointException(Exception):
    pass


class Point(object):

    def __init__(self, x=0, y=0, z=0):
        self.arr = np.array((x, y, z), dtype=np.float64)


class PointList(object):
    '''An array of 3-d points, suitable for doing matrix transforms on.
    Use self.arr to access the points array
    self.array is a 4-d numpy array of float64
    self.arr index 0 is the point index
    self.arr indices 1-3 correspond to the x, y, and z values
    add points using .append()
    extend
    '''
    def __init__(self, arg=None):
        self.arr = np.empty((0, 3), dtype=np.float64)
        if arg is not None:
            if isinstance(arg, PointList):
                self.extend(arg)
            elif isinstance(arg, Point):
                self.append(arg)
            else:
                raise PointException('PointList append given non Point/PointList initializer')

    def append(self, p):
        if not isinstance(p, Point):
            raise PointException('PointList append given non Point argument')
        self.arr = np.append(self.arr, p.arr.reshape(1, 3), axis=0)

    def extend(self, point_list):
        assert isinstance(point_list, PointList)
        self.arr = np.concatenate((self.arr, point_list.arr), axis=0)

    def __len__(self):
        return self.arr.shape[0]


def PointList_from_list(arg_list):
    '''helpful alternate constructor for pointlist from a standard python list of lists'''
    result = PointList()
    for raw_point in arg_list:
        point = Point(*raw_point)
        result.append(point)
    return result



