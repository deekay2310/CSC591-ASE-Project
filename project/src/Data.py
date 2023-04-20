from misc import *
from Rows import *
from Cols import *
from Num import *
import operator
import math 
import copy
from functools import cmp_to_key
from sklearn.cluster import KMeans
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import pairwise_distances

class DATA:
    def __init__(self, src = None, rows = None):
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
        self.rows = []
        self.cols = None
        if src or rows:
            if isinstance(src, str):
                csv(src, self.add)
            else:
                self.cols = Cols(src.cols.names)
                for row in rows:
                    self.add(row)

    def add(self, t):
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

        
    def stats(self, cols = None, nPlaces = 2, what = 'mid'):
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
        
    def clone(data, initial={}):
        """
        -- Create a new DATA with the same columns as  `data`. Optionally, load up the new
        -- DATA with the rows inside `ts`.
        """
        data_obj = DATA()
        data_obj.add(data.cols.names)
        for _, init in enumerate(initial or {}):
            data_obj.add(init)
        return data_obj
   
    def dist(self, row1, row2, the, cols = None):
        """
        -- A query that returns the distances 0..1 between rows `t1` and `t2`.   
        -- If any values are unknown, assume max distances.
        """
        n, d = 0, 0 
        if cols is None:
            cols = self.cols.x
        for col in self.cols.x:
            n = n + 1
            d = d + col.dist(row1.cells[int(col.at)], row2.cells[int(col.at)]) ** 2 
            #the['p']
        # for _, col in self.cols.x.items():
        #     n = n + 1
        #     d = d + (col.dist(row1.cells[col.at], row2.cells[col.at])) ** p
        return (d/n)**(1/2)
    

    # def around(self, row1 ,the, rows=None, cols=None):
    #     """
    #     returns a sorted list of dictionaries containing information about the distances between a given row and other rows in a data matrix.
    #     """
    #     if rows == None:
    #         rows = self.rows
    #     def fun(row2):
    #         return {"row": row2, "dist": self.dist(row1, row2, the, cols)}
    #     return sorted(list(map(fun, rows or self.rows)), key = lambda k : k["dist"])
    
    # def furthest(self, row1, rows = None, cols = None):
    #     """
    #     returns the dictionary for the row that is furthest from a given row in a data matrix.
    #     """
    #     t = self.around(row1,rows,cols)
    #     return t[len(t)-1]

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
        A = above if above and the['Reuse'] else any(some)
        temp = sorted(list(map(function, some)), key = lambda k : k["dist"])
        far = temp[int(float(the['Far']) * len(temp)//1)]
        B = far['row']
        c = far['dist']
        left, right = [], []
        sorted_list = sorted(list(map(project, rows)), key=lambda k: k["dist"])
        for n, tmp in enumerate(sorted_list):
            if n <= len(rows) // 2:
                left.append(tmp['row'])
                mid = tmp['row']
            else:
                right.append(tmp['row'])
        evals = 1 if the['Reuse'] and above else 2
        return left, right, A, B, c, evals

    def half2(self, the, rows = None):

        def euclidean_distance(row1, row2):
            arr1 = np.array(row1.cells)
            arr2 = np.array(row2.cells)
            return np.sqrt(np.sum((arr1 - arr2)**2))

        
        n = len(rows)
        
        i, j = np.random.choice(n, size=2, replace=False)
        A = rows[i]
        B = rows[j]
        
        distances_A = [euclidean_distance(row, A) for row in rows]
        distances_B = [euclidean_distance(row, B) for row in rows]
        distances = np.vstack([distances_A, distances_B])
        
        labels = np.argmin(distances, axis=0)
        cluster_A = [row for row, label in zip(rows, labels) if label == 0]
        cluster_B = [row for row, label in zip(rows, labels) if label == 1]
        
        return cluster_A, cluster_B, A, B, 1
        

    # def cluster(self, the, rows = None,min = None,cols = None,above = None):
    #     """
    #     returns `rows`, recursively halved
    #     """
    #     if rows == None:
    #         rows = self.rows
    #     elif type(rows) == list:
    #         rows = dict(enumerate(rows))
    #     if min == None:
    #         #min = len(rows)^the.min
    #         min = len(rows)**0.5
    #     if cols == None:
    #         cols = self.cols.x
    #     node = {}
    #     node["data"] = self.clone(rows)
    #     if len(rows) > 2*min:
    #         left, right, node['A'], node['B'], node['mid'], c = self.half(the,rows,cols,above)
    #         node['left']  = self.cluster(the, left,  min, cols, node['A'])
    #         node['right'] = self.cluster(the, right, min, cols, node['B'])
    #     return node

    def better(self,row1,row2):
        """
        true if `row1` dominates
        """
        s1,s2,ys = 0,0,self.cols.y
        x,y = None, None
        for col in ys:
            try:
                x  = col.norm(row1.cells[col.at])
                y  = col.norm(row2.cells[col.at])
                s1 = s1 - math.exp(col.w * (x-y)/len(ys))
                s2 = s2 - math.exp(col.w * (y-x)/len(ys))
            except AttributeError:
                pass
        return s1/len(ys) < s2/len(ys)

    def sway(self):
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
        return DATA.clone(self, best), DATA.clone(self, rest), evals1

    def sway2(self):
        """
        SWAY2 Implementation for the project
        """
        data = self
        def worker(rows, worse, evals=None, above=None):
            if len(rows) <= len(data.rows)**float(the['min']):
                return rows, many(worse, int(the['rest'])*len(rows)),evals
            else:
                l, r, A, B, evals1 = self.half2(the, rows) 
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
        return DATA.clone(self, best), DATA.clone(self, rest), evals1
    
    def tree(self, rows = None , min = None, cols = None, above = None):
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

    def betters(self,n):
        key = cmp_to_key(lambda row1, row2: -1 if self.better(row1, row2) else 1)
        tmp = sorted(self.rows, key = key)
        if n is None:
            return tmp
        else:
            return tmp[1:n], tmp[n+1:]