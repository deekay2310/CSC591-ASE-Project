from misc import *
from Rows import *
from Cols import *
from Num import *
import operator
import math 
import copy

class Data:
    def __init__(self,src):
        """
        -- Create a `DATA` to contain `rows`, summarized in `cols`.
        -- Optionally, is any `rows` are supplied, load those in.   
        -- Case [1]: `src` is a filename of a csv file
        -- whose first row 
        -- are the comma-separate names processed by `COLS` (above).
        -- into a new `DATA`. Every other row is stored in the DATA by
        -- calling the 
        -- `row` function (defined below).   
        -- Case [2]: `src` is another data in which case we minic its
        -- column structure.
        """
        self.rows, self.cols = [], None
        def fun(x):
            self.add(x)
        if type(src) == str:
            csv(src,fun)
        else:
            self.add(src)

    def add(self,t):
        """
        -- Update `data` with  row `t`. If `data.cols`
        -- does not exist, the use `t` to create `data.cols`.
        -- Otherwise, add `t` to `data.rows` and update the summaries in `data.cols`.
        -- To avoid updating skipped columns, we only iterate
        -- over `cols.x` and `cols.y`.
        """
        if self.cols:
            if type(t) == list:
                t = Row(t)
            else:
                t = t
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = Cols(t)

        
    def stats(self, what, cols, nPlaces):
        """
        -- A query that returns `mid` or `div` of `cols` (defaults to `data.cols.y`).
        """
        def fun(_, col):
            if what == 'div':
                value = col.div()
            else:
                value = col.mid()
            rounded_value = col.rnd(value, nPlaces)
            return rounded_value, col.txt

        return kap(cols or self.cols.y, fun)
        
    def clone(self, initial):
        """
        -- Create a new DATA with the same columns as  `data`. Optionally, load up the new
        -- DATA with the rows inside `ts`.
        """
        data = Data(self.cols.names)
        # for _,r in initial.items():
        #     data.add(r)
        # return data
        def push(x):
            data.add(x)
        list(map(push, initial))
        return data
   
    def dist(self, row1, row2, the, cols=None):
        """
        -- A query that returns the distances 0..1 between rows `t1` and `t2`.   
        -- If any values are unknown, assume max distances.
        """
        n, d = 0, 0 
        if cols is None:
            cols = self.cols.x
        for col in self.cols.x:
            n = n + 1
            d = d + col.dist(row1.cells[int(col.at)], row2.cells[int(col.at)]) ** 2 #the['p']
        # for _, col in self.cols.x.items():
        #     n = n + 1
        #     d = d + (col.dist(row1.cells[col.at], row2.cells[col.at])) ** p
        return (d/n)**(1/2)
    

    def around(self, row1 ,the, rows=None, cols=None):
        """
        returns a sorted list of dictionaries containing information about the distances between a given row and other rows in a data matrix.
        """
        if rows == None:
            rows = self.rows
        def fun(row2):
            return {"row": row2, "dist": self.dist(row1, row2, the, cols)}
        return sorted(list(map(fun, rows or self.rows)), key = lambda k : k["dist"])
    
    def furthest(self, row1, rows = None, cols = None):
        """
        returns the dictionary for the row that is furthest from a given row in a data matrix.
        """
        t = self.around(row1,rows,cols)
        return t[len(t)-1]

    def half(self, the, rows = None, cols = None, above = None):
        """
        -- Cluster `rows` into two sets by
        -- dividing the data via their distance to two remote points.
        -- To speed up finding those remote points, only look at
        -- `some` of the data. Also, to avoid outliers, only look
        -- `the.Far=.95` (say) of the way across the space. 
        """
        def project(row):
            return {'row' : row, 'dist' : cosine(gap(row,A), gap(row,B), c)}
        def gap(r1, r2):
            return self.dist(r1, r2, the, cols)
        def function(r):
            return {'row' : r, 'dist' : gap(r, A)}
        rows = rows or self.rows
        some = many(rows,the['Halves'])
        # A = above or any(some)
        # A = above or rows[1]
        A = above if above and the['Reuse'] else any(some)
        temp = sorted(list(map(function, some)), key = lambda k : k["dist"])
        far = temp[int(float(the['Far']) * len(temp)//1)]
        # B = self.around(A, the, some)[int(float(the['Far']) * len(rows))//1]['row']
        # B = self.furthest(A,rows)['row']
        B = far['row']
        c = far['dist']
        # c = dist(A,B, the)
        left, right = [], []
        # for _, row in rows.items():
        #     l.append(project(row))
        # sorted_list = sorted(l, key=lambda x:x['dist'])
        sorted_list = sorted(list(map(project, rows)), key=lambda k: k["dist"])
        for n, tmp in enumerate(sorted_list):
            if n <= len(rows) // 2:
                left.append(tmp['row'])
                mid = tmp['row']
            else:
                right.append(tmp['row'])
        evals = 1 if the['Reuse'] and above else 2
        return left, right, A, B, c, evals


    def cluster(self, the, rows = None,min = None,cols = None,above = None):
        """
        returns `rows`, recursively halved
        """
        if rows == None:
            rows = self.rows
        elif type(rows) == list:
            rows = dict(enumerate(rows))
        if min == None:
            #min = len(rows)^the.min
            min = len(rows)**0.5
        if cols == None:
            cols = self.cols.x
        node = {}
        node["data"] = self.clone(rows)
        if len(rows) > 2*min:
            left, right, node['A'], node['B'], node['mid'], c = self.half(the,rows,cols,above)
            node['left']  = self.cluster(the, left,  min, cols, node['A'])
            node['right'] = self.cluster(the, right, min, cols, node['B'])
        return node

    def better(self,row1,row2):
        """
        true if `row1` dominates
        """
        s1,s2,ys = 0,0,self.cols.y
        x,y = None, None
        #print(ys)
        for col in ys:
            try:
                x  = col.norm(row1.cells[col.at])
                y  = col.norm(row2.cells[col.at])
                s1 = s1 - math.exp(col.w * (x-y)/len(ys))
                s2 = s2 - math.exp(col.w * (y-x)/len(ys))
            except AttributeError:
                pass
        return s1/len(ys) < s2/len(ys)

    def sway(self, the):
        """
        -- Recursively prune the worst half the data. Return
        -- the survivors and some sample of the rest.
        """
        data = self
        def worker(rows, worse, evals=None, above=None):
            if len(rows) <= len(data.rows)**float(the['min']):
                return rows, many(worse, int(the['rest'])*len(rows)),evals
            else:
                l, r, A, B, c, evals1 = self.half(the, rows, None, above) 
                if self.better(B, A):
                    l,r,A,B = r,l,B,A
                for row in r:
                    worse.append(row)
                if evals == None:
                    e = evals1
                else:
                    e = evals+evals1
                return worker(l,worse,e,A) 
        best,rest,evals1 = worker(data.rows,[])
        return self.clone(best), self.clone(rest), evals1  
    
    def tree(self, the, rows = None , mini = None, cols = None, above = None):
        """
        -- Cluster, recursively, some `rows` by  dividing them in two, many times
        """
        rows = rows or self.rows
        mini  = mini or len(rows)**the['min']
        cols = cols or self.cols.x
        node = { 'data' : self.clone(rows) }
        if len(rows) >= 2*mini:
            left, right, node['A'], node['B'], node['mid'], _ = self.half(rows,cols,above)
            node['left']  = self.tree(left,  mini, cols, node['A'])
            node['right'] = self.tree(right, mini, cols, node['B'])
        return node
    
    def xpln(self, best, rest, the):
        """
        -- Collect all the ranges into one flat list and sort them by their `value`.
        """
        tmp = []
        maxSizes = {}
        def v(has):
            return value(has, len(best.rows), len(rest.rows), "best")
        def score(ranges):
            rule = self.RULE(ranges, maxSizes)
            if rule:
                print(self.showRule(rule))
                bestr = self.selects(rule, best.rows)
                restr = self.selects(rule, rest.rows)
                if (len(bestr)+len(restr)) > 0:
                    return v({'best': len(bestr), 'rest':len(restr)}), rule
        for ranges in bins(the,self.cols.x,{'best':best.rows, 'rest':rest.rows}):
            maxSizes[ranges[0]['txt']] = len(ranges)
            print("")
            for range in ranges:
                print(range['txt'], range['lo'], range['hi'])
                tmp.append({'range':range, 'max':len(ranges),'val': v(range['y'].has)})
        rule,most=firstN(sorted(tmp, key=lambda x: x['val']),score)
        return rule,most
    
    def RULE(self, ranges, maxSize):
        """
        takes a list of dictionaries containing information about ranges, and an integer maxSize as input, and returns a pruned version of the dictionary of ranges.
        """
        t = {}
        for range in ranges:
            t[range['txt']] = t.get(range['txt'], []) 
            t[range['txt']].append({'lo' : range['lo'],'hi' : range['hi'],'at':range['at']})
        return prune(t, maxSize)
    
    def showRule(self, rule):
        """
        takes a dictionary of rules as input and prints a formatted version of the rule.
        """
        print("rule", rule)
        def pretty(range):
            if range['lo'] == range['hi']:
                return range['lo']
            else:
                return [range['lo'], range['hi']]
        def merges(attr, ranges):
            return list(map(pretty, merge(sorted(ranges, key = lambda x: x['lo'])))), attr
        def merge(t0):
            t = []
            j = 1
            while j<=len(t0):
                left = t0[j-1]
                if j < len(t0):
                    right = t0[j]
                else:
                    right = None
                if right and left['hi'] == right['lo']:
                    left['hi'] = right['hi']
                    j = j + 1
                t.append({'lo' :left['lo'], 'hi' : left['hi']})
                j = j + 1
            return t if len(t0)==len(t) else merge(t)
        
        return dkap(rule, merges)
    
    def betters(self,n):
        """
        takes an integer n as input, sorts the rows of the class instance using the "better" method and returns a tuple containing two lists. The first list contains the first n rows, and the second list contains the remaining rows.
        """
        tmp=sorted(self.rows, key=lambda row: self.better(row, self.rows[self.rows.index(row)-1]))
        return  n and tmp[0:n], tmp[n+1:]  or tmp
    
    def selects(self, rule, rows):
        """
        takes a dictionary of rules and a list of rows as input, and returns a list of rows that satisfy the rules.
        """
        def disjunction(ranges, row):
            for range in ranges:
                lo, hi, at = range['lo'], range['hi'], range['at']
                x = row.cells[at]
                if x == "?":
                    return True
                if lo == hi and lo == x:
                    return True
                if float(lo) <= float(x) and float(x) < float(hi):
                    return True
            return False
        def conjunction(row):
            for ranges in rule.values():
                if not disjunction(ranges, row):
                    return False
            return True

        def function(r):
            if conjunction(r):
                return r

        return list(map(function, rows))