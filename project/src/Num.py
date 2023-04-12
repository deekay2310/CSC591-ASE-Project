import re
import math
from misc import *

class Num:
    """
    creating a class Num to accomodate all functions that help in summarizing a stream of numbers.
    """
    def __init__(self, at='', txt="") -> None:
        self.n, self.mu, self.m2 = 0,0,0
        self.lo = math.inf
        self.hi = -math.inf
        self.at = at
        self.txt = txt
        if re.match("-$", self.txt) is None:
            self.w = 1
        else:
            self.w = -1
        self.has = {}

    def add(self, x):
        """
        -- Update one COL with `x` (values from one cells of one row).
        -- Used  by (e.g.) the `row` and `adds` function.
        -- `SYM`s just increment a symbol counts.
        -- `NUM`s store `x` in a finite sized cache. When it
        -- fills to more than `the.Max`, then at probability 
        -- `the.Max/col.n` replace any existing item
        -- (selected at random). If anything is added, the list
        -- may not longer be sorted so set `col.ok=false`.
        """
        if x != '?':
            self.n = self.n + 1
            if self.n <= 512: # the['max]
                self.has[x] = x
            d = float(x) - self.mu
            self.mu = self.mu + d/self.n
            self.m2 = self.m2 + d*(float(x) - self.mu)
            self.lo = min(float(x), self.lo)
            self.hi = max(float(x), self.hi)
       

    def mid(self):
        """
        -- A query that  returns a `cols`'s central tendency  
        -- (mode for `SYM`s and median for `NUM`s). Called by (e.g.) the `stats` function.
        """
        return self.mu
    
    def div(self):
        """
        -- A query that returns a `col`'s deviation from central tendency    
        -- (entropy for `SYM`s and standard deviation for `NUM`s)..
        """
        return 0 if (self.m2 <0 or self.n < 2) else (self.m2/(self.n-1))**0.5
    
    def rnd(self,x,n):
        """
        Round numbers
        """
        if x == "?":
            return x
        else:
            return rnd(x,n)
        
    def norm(self, n):
        """
        -- A query that normalizes `n` 0..1. Called by (e.g.) the `dist` function.
        """
        if n == "?":
            return n
        else:
            return (float(n) - self.lo)/(self.hi - self.lo + math.pow(10, -32))
        
    def dist(self, n1, n2):
        """
        -- A query that returns the distances 0..1 between rows `t1` and `t2`.   
        -- If any values are unknown, assume max distances.
        """
        if n1  == "?" and n2 == "?":
            return 1
        n1 = self.norm(n1)
        n2 = self.norm(n2)
        if n1 == "?":
            if n2 < 0.5:
                n1 = 1
            else:
                n1 = 0
        if n2 == "?":
            if n1 < 0.5:
                n2 = 1
            else:
                n2 = 0
        return abs(n1 - n2)