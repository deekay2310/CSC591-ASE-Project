import math
from Cols import *
from Rows import *
from misc import *

class BINS:
    def __init__(self, cols, rowss):
        """
        -- Return RANGEs that distinguish sets of rows (stored in `rowss`).
        -- To reduce the search space,
        -- values in `col` are mapped to small number of `bin`s.
        -- For NUMs, that number is `is.bins=16` (say) (and after dividing
        -- the column into, say, 16 bins, then we call `mergeAny` to see
        -- how many of them can be combined with their neighboring bin).
        """
        out = {}
        for _,col in cols:
            ranges = {}
            for y, rows in rowss:
                for _, row in rows:
                    x, k = row[col.at]
                    if x!= "?":
                        k = self.bin(col, x)
                        ranges[k] = ranges[k] or RANGE(col.at, col.txt, x)
                        extend(ranges[k], x, y)
            ranges = sorted(map(ranges, lambda x: x['lo']))
            out[1 + len(out)] = col.isSym and ranges or mergeAny(ranges)
        return out 