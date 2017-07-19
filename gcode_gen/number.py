import math
import numpy as np

mm_per_inch = 25.4
NUM2STR_FORMAT = "{:.5f}"
CLOSE_TOLERANCE = 1.0e-6


def isclose(arg_a, arg_b, close_tolerance=CLOSE_TOLERANCE):
    return math.isclose(arg_a, arg_b, abs_tol=close_tolerance)


def num2str(arg):
    return NUM2STR_FORMAT.format(arg)


def safe_ceil(arg):
    '''Ceiling of arg, but if arg is math.isclose() integer just return that int.
    Example: safeCeil(3.999999) == 4
    Example: safeCeil(4.00000001) == 4
    Example: safeCeil(4.1) == 5'''
    if isclose(arg, round(arg)):
        return int(round(arg))
    else:
        return int(math.ceil(arg))


def calc_steps_with_max_spacing(start, stop, max_spacing):
    # NOTE: safe_ceil(abs(stop-start) / max_spacing) gives the number of intervals,
    # but the number of steps is +1.
    # Why? Think of fenceposts and connections
    num_steps = safe_ceil(abs(stop - start) / max_spacing) + 1
    step_list = np.linspace(start, stop, num_steps)
    return step_list
