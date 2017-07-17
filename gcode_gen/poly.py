'''polygon library'''
import numpy as np
from numpy.linalg import norm
from . import iter_util
from . import point
from . import transform


def unit(vec):
    '''return unit vector for given vec'''
    return vec / norm(vec)


class PolygonException(Exception):
    pass


class Polygon(transform.Transformable):
    '''Polygon of 3d points.
    This polygon may represent a skew polygon, but this limits the useful methods on it.
    The vertex initializer argument assumes there is an edge between each point and the next, with an
    additional edge between the last point and the first.
    For example, for a 2x2 square centered at origin in x/y plane
    sqr = Polygon(PointList_from_list([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], ]))
'''
    def __init__(self, vertices=None):
        if not isinstance(vertices, point.PointList):
            raise PolygonException("Polygon vertices initializer must be of type point.PointList")
        if len(vertices) < 3:
            raise PolygonException("Polygon vertices initializer must have at least 3 vertices")
        super().__init__(vertices)

    def get_vertices(self):
        '''Return vertices with implied connection between each and the next.
        Also implied connection from last to first vertex in list.'''
        return self.arr

    def get_edges(self):
        '''Return vertex pairs representing each edge.'''
        return list(iter_util.loop_pairwise_iter(self.get_vertices()))

    def get_corners(self):
        '''Return corners made up of 2 edges (see get_edges).
        NOTE: starts with the corner centered on self.get_vertices()[0]'''
        vec0s = list(zip(np.roll(self.arr, 1, axis=0), self.arr))
        vec1s = list(zip(self.arr, np.roll(self.arr, -1, axis=0)))
        return list(zip(vec0s, vec1s))

    def get_corner_vectors(self):
        '''Return vectors for each corner....
        The first element of each is the vector from the previous vertex to the corner center vertex.
        The second element of each is the vector from the corner center vertex to the next vertex.
        NOTE: starts with the corner centered on self.get_vertices()[0]'''
        vec0s = self.arr - np.roll(self.arr, 1, axis=0)
        vec1s = np.roll(self.arr, -1, axis=0) - self.arr
        return list(zip(vec0s, vec1s))

    def get_corner_vector_crossproducts(self):
        '''for each vector pair from get_corner_vectors,
             perform the crossproduct and
             return all results as list
        '''
        return np.cross(*zip(*self.get_corner_vectors()))

    def is_coplanar(self):
        '''returns true if all vertices are in the same plane'''
        cprods = self.get_corner_vector_crossproducts()
        expected_normal = None
        result = True
        for cprod in cprods:
            if np.allclose(cprod, np.asarray((0, 0, 0))):  # early bail on collinear!
                pass
            elif expected_normal is None:
                expected_normal = unit(cprod)
            elif not np.allclose(expected_normal, unit(cprod)):
                result = False
                break
        return result

    def is_all_collinear(self):
        '''returns true if all vertices along the same line'''
        cprods = self.get_corner_vector_crossproducts()
        result = True
        for cprod in cprods:
            if not np.allclose(cprod, np.asarray((0, 0, 0))):  # early bail on not collinear!
                result = False
                break
        return result

    # def get_orientations(self):
    #     '''for each corner centered on a vertex,
    #          returns 0 if collinear, 1 if clockwise, -1 if counter clockwise'''
    #     cprods = self.get_corner_vector_crossproducts()
    #     result = []
    #     for cprod in cprods:
    #         if not np.allclose(cprod, np.asarray((0, 0, 0))):  # early bail on not collinear!
    #             result.append(0)
    #         elif:

    #     return result
    #     print(self.get_corner_vector_crossproducts())
    #     return np.sign(self.get_corner_vector_crossproducts())


class PolygonCoplanar(Polygon):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_coplanar():
            raise PolygonException("PolygonCoplanar vertices must be coplanar")
        if self.is_all_collinear():
            raise PolygonException("PolygonCoplanar vertices must not all be collinear")

    def get_normal(self):
        '''returns vector normal to the polygon plane'''
        cprods = self.get_corner_vector_crossproducts()
        for cprod in cprods:
            if np.allclose(cprod, np.asarray((0, 0, 0))):  # early bail on collinear!
                pass
            else:
                return unit(cprod)

