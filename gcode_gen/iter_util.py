'''Common iterators'''
import itertools


def twice_iter(arg):
    for val in arg:
        yield val
        yield val


def pairwise_iter(arg):
    '''s -> (s0,s1), (s1,s2), (s2, s3), ...'''
    a, b = itertools.tee(iter(arg))
    next(b, None)
    return zip(a, b)


def all_plus_first_iter(arg):
    '''Yield each element of a list, then yield the first one more time at the end'''
    iter_arg = iter(arg)
    first_element = next(iter_arg)
    yield first_element
    for remaining in iter_arg:
        yield remaining
    yield first_element


def loop_pairwise_iter(arg):
    '''pairwise plus a final pair that is the last and first repeated'''
    return pairwise_iter(all_plus_first_iter(arg))


def serpent_iter(starts, stops):
    '''yield start[0], stop[0], stop[1], start[1], start[2], stop[2], etc, walking back and forth.
    For example, serpent_iter((1, 0, -1), (2, 3, 4), ) yields
    (1, 2, 3, 0, -1, 4, )
    '''
    direction_start_to_stop = True
    for start, stop in zip(iter(starts), iter(stops)):
        if direction_start_to_stop:
            yield start
            yield stop
        else:
            yield stop
            yield start
        direction_start_to_stop = not(direction_start_to_stop)


def fill_walk_iter(y_steps, x_start_steps, x_stop_steps):
    '''Intended to be used as a pattern for motion of milling out an area'''
    for x_coord, y_coord in zip(serpent_iter(x_start_steps, x_stop_steps), twice_iter(y_steps)):
        yield x_coord, y_coord
