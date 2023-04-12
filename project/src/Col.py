from Num import *
from Sym import *

def COL(n, s):
    """
    -- Create a `NUM` or a `SYM`. Column
    -- names are a little language that    
    -- e.g. makes `NUM`s if name starts in upper case; or
    -- e.g. makes goals if the name ends with
    -- the maximize (`+`) or minimize (`-`) or klass (`!`) symbol.
    """
    is_num = s[0].isupper()
    if is_num:
        col = Num(n,s)
    else:
        col = Sym(n, s)
    col.isIgnored = s.endswith("X")
    col.isKlass = s.endswith("!")
    col.isGoal = s.endswith("!") or s.endswith("+") or s.endswith("-")
    
    return col
