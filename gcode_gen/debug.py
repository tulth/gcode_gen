import inspect
import re


def debug_str(arg):
    '''Return string of arg varible name and str(arg) value.'''
    frame = inspect.currentframe().f_back
    s = inspect.getframeinfo(frame).code_context[0]
    r = re.search(r"\((.*)\)", s).group(1)
    return str("{} = {}".format(r, arg))


def debug_print(arg):
    '''Print arg varible name and str(arg) value.'''
    frame = inspect.currentframe().f_back
    s = inspect.getframeinfo(frame).code_context[0]
    r = re.search(r"\((.*)\)", s).group(1)
    print("{} = {}".format(r, arg))


DBGP = debug_print  # shortened alias
DBGS = debug_str  # shortened alias
