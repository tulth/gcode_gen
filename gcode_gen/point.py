'''
A basic base class for point and point lists
'''
import numpy as np
from collections.abc import MutableSequence, Iterable
from . import number


class XYZ(object):
    '''Tuple of x, y, z where the types of x/y/z could be anything
    Not intended to be mutable!
    '''
    def __init__(self, x=None, y=None, z=None):
        self.xyz = (x, y, z)

    @property
    def arr(self):
        return self.xyz

    @property
    def x(self):
        return self.xyz[0]

    @property
    def y(self):
        return self.xyz[1]

    @property
    def z(self):
        return self.xyz[2]


class Point(XYZ):
    '''Point class for representing 3-d x/y/z cartesian coordinates.
    x/y/z elements are 64 bit floats
    x/y/z not specified are assumed to be zero
    Not intended to be mutable!
    '''
    def __init__(self, x=0, y=0, z=0):
        self.xyz = np.array((x, y, z), dtype=np.float64)

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return Point(*self.xyz.copy())


class PointList(MutableSequence):
    '''A list of 3-d Points.
    Underlying representation is a 4-d numpy array of np.float64
    Access points within the array like any other list.
    While the list is mutable, the points within the list are not intended to be.
    Note: slice assignment is not supported
    '''
    def __init__(self, arg=None):
        if arg is None:
            self._arr = np.empty((0, 3), dtype=np.float64)
        else:
            cast_arg = np.asarray((self._cast_arr(arg)), dtype=np.float64)
            # print(cast_arg)
            # print(type(cast_arg))
            self._arr = cast_arg

    def _cast_arr(self, arg):  # cast arg to np array suitable for extending/inserting PointList
        err = TypeError('cannot cast type={} val={}'.format(type(arg), arg))
        if isinstance(arg, PointList):
            return arg.arr
        elif isinstance(arg, Point):
            return np.asarray((arg.arr))
        elif isinstance(arg, np.ndarray):
            if len(arg.shape) == 1:
                return np.asarray(((Point(*arg).arr, )))
            elif len(arg.shape) == 2 and arg.shape[1] == 3:
                return arg
            else:
                raise err
        elif isinstance(arg, Iterable):
            return np.asarray([Point(*raw_point).arr for raw_point in arg])
        else:
            raise err

    @property
    def arr(self):
        return self._arr

    @property
    def shape(self):
        return self.arr.shape

    def __getitem__(self, index):
        # print("__getitem__", index)
        if len(self) == 0:
            raise IndexError('attempt to deference an empty PointList')
        elif isinstance(index, int):
            return Point(*self._arr[index])
        elif isinstance(index, slice):
            # raise KeyError('slice access not supported')
            return PointList(self._arr[index])
        else:
            raise TypeError('Invalid index/slice type')

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            raise KeyError('slice assignment not supported')
        # print("__setitem__", index, value)
        self._arr[index, :] = value

    def __delitem__(self, index):
        raise NotImplementedError("deletion not supported")

    def __len__(self):
        return self.arr.shape[0]

    def insert(self, index, value):
        # print("insert", index, value)
        if isinstance(index, slice):
            raise KeyError('slice assignment not supported')
        self._arr = np.insert(self._arr, index, value.arr.reshape(1, 3), axis=0)


PL_ZERO = PointList(Point())


def changes(point0, point1):
    result = {}
    for key, elem0, elem1 in zip(('x', 'y', 'z'), point0.arr, point1.arr):
        if not number.isclose(elem0, elem1):
            result[key] = elem1
    return result
