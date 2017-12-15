Python 2.7.14 (v2.7.14:84471935ed, Sep 16 2017, 12:01:12) 
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "copyright", "credits" or "license()" for more information.
>>> WARNING: The version of Tcl/Tk (8.5.9) in use may be unstable.
Visit http://www.python.org/download/mac/tcltk/ for current information.
import math

def my_reverse(lst):
#    return list(reversed(lst))
    rev = []
    for i in range(len(lst)-1,-1,-1):
        rev.append(lst[i])
    return rev
