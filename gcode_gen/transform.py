"""
Homogenous affine/linear transforms for x/y/z coordinates.
"""
import numpy as np
from numpy.linalg import norm
from . import vertex


def translateMat(x=0, y=0, z=0):
    mat = np.identity(4)
    mat[0, 3] = x
    mat[1, 3] = y
    mat[2, 3] = z
    return mat


def scaleMat(sx=1, sy=1, sz=1):
    mat = np.identity(4)
    mat[0, 0] = sx
    mat[1, 1] = sy
    mat[2, 2] = sz
    return mat


def rotateMat(phi, x=0, y=0, z=1):
    """Rotate by phi radians about axis defined by (x, y, z),
    (x,y,z) defaults to xy rotation where +phi is a counterclockwise rotation
    """
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
        self.append(("T", translateMat(x, y, z)))

    def scale(self, sx=1, sy=1, sz=1):
        self.append(("S", scaleMat(sx, sy, sz)))

    def rotate(self, phi, x=0, y=0, z=1):
        self.append(("R", rotateMat(phi, x, y, z)))

    def customTransform(self, mat, name=None):
        if name is None:
            name = "C"
        self.append((name, mat))

    def getComposition(self):
        result = np.identity(4)
        for (id, mat) in self:
            result = np.dot(mat, result)
        return result

    def doTransform(self, points):
        """Accepts 2d or 3d points, always returns 3d points"""
        pVecs = points.copy()
        if (points.shape[1] == 2):
            zeroVec = np.zeros((pVecs.shape[0], 1))
            pVecs = np.concatenate((pVecs, zeroVec), axis=1)
        elif (points.shape[1] == 3):
            pass
        else:
            raise Exception("in doTransform, points must have 2 or 3 coordinates")
        oneVec = np.ones((pVecs.shape[0], 1))
        pVecs = np.concatenate((pVecs, oneVec), axis=1)
        result = np.dot(self.getComposition(), pVecs.T)
        result = result[:-1].T
        return result


class Transformable(object):
    """Base clase for an object on which basic transforms are defined"""
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

    def customTransform(self, mat, name=None):
        self.transforms.customTransform(mat, name)
        return self

    def transformVertices(self, vertices):
        return self.transforms.doTransform(vertices)
