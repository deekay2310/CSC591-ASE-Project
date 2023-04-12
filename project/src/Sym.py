import math

class Sym:
    """
    -- Create a `Sym` class to summarize a stream of symbols.
    """
    def __init__(self, at=0, txt="") -> None:
        self.n = 0
        self.has = {}
        self. most = 0
        self.mode = None
        self.at = at
        self.txt = txt
        
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
            self.has[x] = 1 + self.has.get(x, 0)
            if self.has[x] > self.most:
                self.most, self.mode = self.has[x], x

    def mid(self):
        """
        -- A query that  returns a `cols`'s central tendency  
        -- (mode for `SYM`s and median for `NUM`s). Called by (e.g.) the `stats` function.
        """
        return self.mode

    def div(self):        
        """
        -- A query that returns a `col`'s deviation from central tendency    
        -- (entropy for `SYM`s and standard deviation for `NUM`s)..
        """
        def fun(p):
            return p*math.log(p,2)
        e = 0
        for _,n in self.has.items():
            e = e + fun(n/self.n)
        return -e
    
    def rnd(self, x, n):
        """
        round numbers
        """
        return x
    
    def dist(self, s1, s2):
        """
        -- A query that returns the distances 0..1 between rows `t1` and `t2`.   
        -- If any values are unknown, assume max distances.
        """
        if s1 == "?" and s2 == "?":
            return 1
        elif s1 == s2:
            return 0
        else:
            return 1

