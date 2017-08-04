'''polygon library'''
import numpy as np
from numpy.linalg import norm
import math
import itertools
from .. import iter_util
from .. import point
from .. import transform
from ..debug import DBGP
from . import fill


def unit(vec):
    '''return unit vector for given vec'''
    return vec / norm(vec)


def poly_circle_verts(segments_per_circle=32):
    spc = segments_per_circle
    assert spc >= 3
    phi0 = np.pi / 2
    if spc % 2 == 0:
        phi0 += np.pi / spc
    vertices = [(np.cos(phi + phi0), np.sin(phi + phi0)) for phi in np.linspace(0, 2 * np.pi, spc, endpoint=False)]
    return point.PointList(vertices)


class PolygonError(Exception):
    pass


class Polygon(transform.TransformablePointList):
    '''Polygon of 3d points.
    This polygon may represent a skew polygon, but this limits the useful methods on it.
    The vertex initializer argument assumes there is an edge between each point and the next, with an
    additional edge between the last point and the first.
    For example, for a 2x2 square centered at origin in x/y plane
    sqr = Polygon(PointList([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], ]))
'''
    def __init__(self, vertices=None):
        super().__init__(vertices)
        if len(self) < 3:
            raise PolygonError("Polygon vertices initializer must have at least 3 vertices")

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
                expected_normal = np.fabs(unit(cprod))
            elif not np.allclose(expected_normal, np.fabs(unit(cprod))):
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

    @property
    def bounds(self):
        '''returns array:
        [[xmin, xmax],
         [ymin, ymax],
         [zmin, zmax], ]'''
        bounds = []
        # print(self.arr.shape[1])
        for dim_num in range(self.arr.shape[1]):
            bounds.append((np.min(self.arr[:, dim_num]), np.max(self.arr[:, dim_num]), ))
        bounds = np.asarray(bounds)
        return bounds

    # @property
    # def boundingBox(self, ):
    #     if self._boundingBox is None:
    #         self._boundingBox = vertex.getBoundingBox(self.vertices)
    #     return self._boundingBox
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


class CoplanarPolygon(Polygon):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_coplanar():
            raise PolygonError("CoplanarPolygon vertices must be coplanar")
        if self.is_all_collinear():
            raise PolygonError("CoplanarPolygon vertices must not all be collinear")

    def get_normal(self):
        '''returns unit vector normal to the polygon plane'''
        cprods = self.get_corner_vector_crossproducts()
        result = cprods[0]
        for cprod in cprods[1:]:
            result += cprod
        return unit(result)

    def get_corner_angle_class(self):
        '''return a list of numbers, one per corner matching the vertex order,
        where the value is:
        -1 if the corner interior angle is > Pi (reflex angle) (concave)
         0 if the corner interior angle is Pi (straight angle) (collinear)
         1 if the corner interior angle is < Pi (acute, right, or obtuse angle) (convex)
         '''
        cprods = self.get_corner_vector_crossproducts()
        poly_normal = self.get_normal()
        result = []
        for cprod in cprods:
            if np.allclose(cprod, np.asarray((0, 0, 0))):  # early test on collinear to prevent div0
                result.append(0)
            elif np.allclose(poly_normal, unit(cprod)):
                result.append(1)
            elif np.allclose(poly_normal, -unit(cprod)):
                result.append(-1)
            else:
                PolygonError("Unexpected error in get_corner_angle_class()")
        return result

    def is_convex(self):
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

    def is_simple(self):
        if self.is_convex():
            return True
        else:
            # lifted from my old code
            edges = self.get_edges()
            for edge_idx_pair in itertools.combinations(range(len(self.arr)), 2):
                if np.allclose(((edge_idx_pair[0] + 1) % len(edges)), edge_idx_pair[1]):
                    # print("adjacent")
                    continue
                elif np.allclose(((edge_idx_pair[0] - 1) % len(edges)), edge_idx_pair[1]):
                    # print("adjacent")
                    continue
                else:
                    # DBGP(edge_idx_pair)
                    # DBGP(edges[edge_idx_pair[0]])
                    # DBGP(edges[edge_idx_pair[1]])
                    # print("** NOT adjacent **")
                    if (is_edge_intersect(edges[edge_idx_pair[0]], edges[edge_idx_pair[1]])):
                        # print("** Intersected! **")
                        return False
            return True
        return self._simple


def is_edge_intersect(edge0, edge1):
    left = max(min(edge0[0][0], edge0[1][0]), min(edge1[0][0], edge1[1][0]))
    right = min(max(edge0[0][0], edge0[1][0]), max(edge1[0][0], edge1[1][0]))
    top = max(min(edge0[0][1], edge0[1][1]), min(edge1[0][1], edge1[1][1]))
    bottom = min(max(edge0[0][1], edge0[1][1]), max(edge1[0][1], edge1[1][1]))
    if top > bottom or left > right:
        return False
    else:
        return True


class SimplePolygon(CoplanarPolygon):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_simple():
            raise PolygonError("SimplePolygon vertices must form a simple polygon's mathematical definition")

    def shrink(self, amount):
        poly_normal = self.get_normal()
        correction_vecs = []
        for corner_vecs, corner_class in zip(self.get_corner_vectors(), self.get_corner_angle_class()):
            # DBGP(corner_vecs)
            # DBGP(corner_class)
            u_prev_vec = unit(corner_vecs[0])
            u_next_vec = unit(corner_vecs[1])
            # DBGP(u_prev_vec)
            # DBGP(u_next_vec)
            if corner_class == 0:  # straight, handle first to avoid div0
                u_correction_vec = unit(np.cross(poly_normal, u_prev_vec))
                correction_vec_len = amount
            elif corner_class == 1:  # convex
                u_correction_vec = unit(-u_prev_vec + u_next_vec)
            elif corner_class == -1:  # concave
                u_correction_vec = -unit(-u_prev_vec + u_next_vec)
            # DBGP(u_correction_vec)
            if corner_class == 0:  # straight, handle first to avoid div0
                correction_vec_len = amount
            else:
                # correction_vec_len = amount / np.cross(u_next_vec, u_correction_vec)
                dot_prod = np.dot(u_correction_vec, u_next_vec)
                base_correction_len = np.sqrt(1 / (1 - (dot_prod**2)))
                # DBGP(base_correction_len)
                correction_vec_len = amount * base_correction_len
            # DBGP(correction_vec_len)
            correction_vecs.append(correction_vec_len * u_correction_vec)
        newVerts = point.PointList(self.arr + np.asarray(correction_vecs))
        # DBGP(newVerts.arr)
        result = SimplePolygon(newVerts)
        return result

    def grow(self, amount):
        return self.shrink(-amount)



