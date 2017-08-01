'''
Homogenous affine/linear transforms for x/y/z coordinates.
'''
import numpy as np
from numpy.linalg import norm
from . import point


def translate_mat(x=0, y=0, z=0):
    mat = np.identity(4)
    mat[0, 3] = x
    mat[1, 3] = y
    mat[2, 3] = z
    return mat


def scale_mat(sx=1, sy=1, sz=1):
    mat = np.identity(4)
    mat[0, 0] = sx
    mat[1, 1] = sy
    mat[2, 2] = sz
    return mat


def rotate_mat(phi, x=0, y=0, z=1):
    '''Rotate by phi radians about axis defined by (x, y, z),
    (x,y,z) defaults to xy rotation where +phi is a counterclockwise rotation
    '''
    veclen = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    ux, uy, uz = x / veclen, y / veclen, z / veclen
    mat = np.identity(4)
    cosphi = np.cos(phi)
    sinphi = np.sin(phi)
    r = np.asarray([
        [ux * ux * (1 - cosphi) + 1 * cosphi,
         uy * ux * (1 - cosphi) - uz * sinphi,
         uz * ux * (1 - cosphi) + uy * sinphi],
        [ux * uy * (1 - cosphi) + uz * sinphi,
         uy * uy * (1 - cosphi) + 1 * cosphi,
         uz * uy * (1 - cosphi) - ux * sinphi],
        [ux * uz * (1 - cosphi) - uy * sinphi,
         uy * uz * (1 - cosphi) + ux * sinphi,
         uz * uz * (1 - cosphi) + 1 * cosphi],
    ])
    mat[:3, :3] = r
    return mat


class TransformList(list):

    def translate(self, x=0, y=0, z=0):
        self.append(('T', translate_mat(x, y, z)))

    def scale(self, sx=1, sy=1, sz=1):
        self.append(('S', scale_mat(sx, sy, sz)))

    def rotate(self, phi, x=0, y=0, z=1):
        self.append(('R', rotate_mat(phi, x, y, z)))

    def matrix_transform(self, mat, name=None):
        if name is None:
            name = 'M'
        self.append((name, mat))

    def get_composition(self):
        result = np.identity(4)
        for (id, mat) in self:
            result = np.dot(mat, result)
        return result

    def __call__(self, arr):
        if not isinstance(arr, np.ndarray):
            raise TypeError("expected argument to be numpy ndarray")
        if len(arr.shape) != 2:
            raise TypeError("expected argument.shape to be length 2, not {}".format(len(arr.shape)))
        if arr.shape[1] != 3:
            raise TypeError("expected argument to be array of 3-d points")
        if arr.shape[0] == 0:
            raise IndexError("expected at least one point!")
        one_vec = np.ones((arr.shape[0], 1))
        point_vectors = np.concatenate((arr, one_vec), axis=1)
        result = np.dot(self.get_composition(), point_vectors.T)
        result = result[:-1].T
        return result

    def __str__(self):
        results = []
        for transform in self:
            results.append(str(transform))
        return '\n'.join(results) + '\n'


class TransformableMixin(object):
    def __init__(self, *args, **kwargs):
        self.transforms = TransformList()
        super().__init__(*args, **kwargs)

    def translate(self, x=0, y=0, z=0):
        self.transforms.translate(x, y, z)
        return self

    def scale(self, sx=1, sy=1, sz=1):
        self.transforms.scale(sx, sy, sz)
        return self

    def rotate(self, phi, x=0, y=0, z=1):
        self.transforms.rotate(phi, x, y, z)
        return self

    def matrix_transform(self, mat, name=None):
        self.transforms.matrix_transform(mat, name)
        return self

    def apply_transforms(self):
        '''Define in subclass.  Typically of the form:
        return self.transforms(point_array)'''
        raise NotImplementedError()


class TransformablePointList(TransformableMixin, point.PointList):
    '''Base clase for an object on which basic transforms are defined.
    NOTE: transform application is deferred until apply_transforms() is called'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply_transforms(self):
        '''Note! returns a copy! does not transform in place!'''
        return self.__class__(self.transforms(self.arr))
