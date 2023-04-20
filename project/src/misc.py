import math 
import re
import sys
import random
from csv import reader
from Sym import *
import copy
import io
from Num import *
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer

# the = {'bootstrap': 512, 'conf' : 0.05, 'cliff' : 0.4, 'cohen' : 0.35, 'Fmt' : """'%6.2f'""", 'width' : 40}
the = { 'dump': False, 'go': None, 'seed': 937162211, 'bootstrap':512, 'conf':0.05, 'cliffs':.4, 'cohen':.35, 'Fmt': "{:.2f}", 'width':40, 'n_iter': 20, 'min': 0.5, 'Halves': 512, 'Far': 0.95, 'Reuse': True, 'rest': 10, 'bins': 16, 'd': 0.35}

#Numerics
help = """   
script.lua : an example script with help text and a test suite
(c)2022, Tim Menzies <timm@ieee.org>, BSD-2 
USAGE:   script.lua  [OPTIONS] [-g ACTION]
OPTIONS:
  -d  --dump  on crash, dump stack = false
  -f  --file    name of file       = data/SSN.csv
  -F  --Far     distance to "faraway"  = .95
  -g  --go      start-up action        = data
  -h  --help    show help              = false
  -m  --min     stop clusters at N^min = .5
  -p  --p       distance coefficient   = 2
  -s  --seed    random number seed     = 937162211
  -S  --Sample  sampling data size     = 512
  -r  --rest    how many of rest to sample   = 4
  -b  --bins    initial number of bins       = 16
  -H  --Halves  search space for clustering  = 512
  -R  --Reuse   child splits reuse a parent pole = true
ACTIONS:
  -g  the	show settings
  -g  sym	check syms
  -g  num	check nums
  -g  csv	read from csv
  -g  data	read DATA csv
  -g  stats	stats from DATA
"""
# RANGE
def RANGE(at, txt, lo, hi=None):
    """
    -- Create a RANGE  that tracks the y dependent values seen in 
    -- the range `lo` to `hi` some independent variable in column number `at` whose name is `txt`. 
    -- Note that the way this is used (in the `bins` function, below)
    -- for  symbolic columns, `lo` is always the same as `hi`.
    """
    res = {}
    res['at'] = at
    res['txt'] = txt
    res['lo'] = lo
    res['hi'] = lo or hi or lo
    res['y'] = Sym()
    return res
    

def show(node, what, cols, nPlaces, lvl=0):
    """
    -- Cluster can be displayed by this function.
    """
    if node:
        print('| '*lvl + str(len(node['data'].rows)) + " ", end = '')
        if (not node.get('left') or lvl==0):
            print(o(node['data'].stats("mid",node['data'].cols.y, nPlaces )))
        else:
            print("")
        show(node.get('left'), what, cols, nPlaces, lvl+1)
        show(node.get('right'), what, cols, nPlaces, lvl+1)



def rint(lo,hi):
    """
    Rounds to integer
    """
    return math.floor(0.5 + rand(lo, hi))

def rand(lo, hi, Seed = 937162211):
    """
    Random floats
    """
    lo, hi = lo or 0, hi or 1
    Seed = (16807 * Seed) % 2147483647
    return lo + (hi-lo) * Seed / 2147483647

def rnd(n, nPlaces=3):
    """
    Round numbers upto 3 places by default unless another place value is provided.
    """
    mult = 10 ** (nPlaces)
    return math.floor(n * mult + 0.5) / mult

#Lists
def push(t, x):
    """
    Push an item `x` onto  a list.    
    """
    t[1 + len(t)] = x
    return x
 
def kap(t, fun):
    """
    -- Map a function on table (results in items key1,key2,...)
    """
    x = {}
    if type(t) == list:
        tmp = enumerate(t)
    else:
        tmp = t.items()
    for k, v in tmp:
        v, k = fun(k, v)
        if not k:
            x[len(x)] = v
        else:
            x[k] = v
    return x

def any(t):
    """
    -- Return one item at random.    
    """
    return t[random.randint(0, len(t)-1)]

def many(t, n):
    """
    -- Return many items, selected at random.  
    """
    u = []
    for i in range(1,n+1):
        u.append(any(t))
    return u

def cosine(a,b,c):
    """
    --> n,n;  
    find x,y from a line connecting `a` to `b`
    """
    if c != 0:
        return (a**2 + c**2 - b**2) / (2*c)
    
    return 0

def coerce(s):
    """
    -- Coerce string to boolean, int,float or (failing all else) strings.
    """
    bool_s = s.lower()
    for t in [int, float]:
        try:
            return t(s)
        except ValueError:
            pass
    if bool_s in ["true", "false"]:
        return bool_s == "true"
    return s

def oo(t):
    """
    -- Print a nested table (sorted by the keys of the table).
    """
    print(o(t))
    return t

def o(t):
    """
    internal function to enable oo() to print a nested table 
    """
    if type(t)!=dict:
        return str(t)
    def show(k,v):
        if "^_" not in str(k):
            v=o(v)
            return str(k)+" : "+str(v)
    u=[]
    for k in t:
        u.append(show(k,t[k]))
    if len(t)==0:
        u.sort()
    return " ".join(u)

def settings(s):
    """
    --> t;  parse help string to extract a table of options
    """
    return dict(re.findall("\n[\s]+[-][\S]+[\s]+[-][-]([\S]+)[^\n]+= ([\S]+)",s))

def cli(t):
    """
    -- Update `t` using command-line options. For boolean
    -- flags, just flip the default values. For others, read
    -- the new value from the command line.
    """
    args = sys.argv[1:]
    for k, v in t.items():
        for n, x in enumerate(args):
            if x == '-'+k[0] or x == '--'+k:
                if v == 'false':
                    v = 'true'
                elif v == 'true':
                    v = 'false'
                else:
                    v = args[n+1]
        t[k] = coerce(v)
    return t

def csv(sFilename, fun):
    """
    -- Run `fun` on the cells  in each row of a csv file.
    """
    if sFilename:
        src = io.open(sFilename)
        t = []
        for _,l in enumerate(src):
            s = l.strip().split(',')
            r = list(map(coerce, s))
            t.append(r)
            fun(r)
    else:
        print("not opeinng")

def deepcopy(t):
    """
    -- Deep copy of a table `t`.
    """
    return copy.deepcopy(t)

def cliffsDelta(the, ns1, ns2):
    """
    -- Non-parametric effect-size test
    --  M.Hess, J.Kromrey. 
    --  Robust Confidence Intervals for Effect Sizes: 
    --  A Comparative Study of Cohen's d and Cliff's Delta Under Non-normality and Heterogeneous Variances
    --  American Educational Research Association, San Diego, April 12 - 16, 2004    
    --  0.147=  small, 0.33 =  medium, 0.474 = large; med --> small at .2385
    """
    """
    bool;
    true if different by a trivial amount
    """
    n, gt, lt = 0, 0, 0
    if len(ns1) > 128:
        ns1 = samples(ns1, 128)
    if len(ns2) > 128:
        ns2 = samples(ns2, 128)
    for x in ns1:
        for y in ns2:
            n += 1
            if x > y:
                gt += 1
            if x < y:
                lt += 1
    return abs(lt - gt) / n <= the['cliffs']

def bins(the,cols,rowss):
    """
    -- Return RANGEs that distinguish sets of rows (stored in `rowss`).
    -- To reduce the search space,
    -- values in `col` are mapped to small number of `bin`s.
    -- For NUMs, that number is `the.bins=16` (say) (and after dividing
    -- the column into, say, 16 bins, then we call `mergeAny` to see
    -- how many of them can be combined with their neighboring bin).
    """
    def withAllRows(col):
        def xy(x,y):
            nonlocal n
            if x != '?':
                n = n + 1
                k = bin(the, col, x)
                ranges[k] = ranges.get(k, RANGE(col.at,col.txt,x))
                extend(ranges[k], x, y)
        n,ranges = 0,{}
        for y,rows in rowss.items():
            for _,row in enumerate(rows):
                xy(row.cells[col.at],y)
        return n, ranges
    
    def with1Col(col):
        def itself(x):
            return x
        n,ranges = withAllRows(col)
        ranges   = sorted(list(map(itself, ranges.values())),key = lambda x: x['lo'])
        if   type(col) == Sym:
            return ranges 
        else:
            return merges(ranges, n/the['bins'], the['d']*col.div()) 
    
    ret = list(map(with1Col, cols))
    return ret

def bin(the,col,x):
    """
    -- Map `x` into a small number of bins. `SYM`s just get mapped
    -- to themselves but `NUM`s get mapped to one of `the.bins` values.
    -- Called by function `bins`.
    """
    if x=="?" or isinstance(col, Sym):
        return x
    tmp = (col.hi - col.lo)/(int(the['bins']) - 1)
    return  1 if col.hi == col.lo else math.floor(float(x)/tmp + 0.5)*tmp

def merge(col1,col2):
    """
    -- Merge two `cols`. Called by function `merge2`.
    """
    new = deepcopy(col1)
    if isinstance(col1, Sym):
        for n in col2.has:
            new.add(n)
    else:
        for n in col2.has:
            new.add(new,n)
        new.lo = min(col1.lo, col2.lo)
        new.hi = max(col1.hi, col2.hi) 
    return new


def extend(range,n,s):
    """
    -- Update a RANGE to cover `x` and `y`
    """
    range['lo'] = min(n, range['lo'])
    range['hi'] = max(n, range['hi'])
    range['y'].add(s)

def itself(x):
    """
    -- Return self
    """
    return x

def value(has,nB = None, nR = None, sGoal = None):
    """
    -- A query that returns the score a distribution of symbols inside a SYM.
    """
    sGoal,nB,nR = sGoal or True, nB or 1, nR or 1
    b,r = 0,0
    for x,n in has.items():
        if x==sGoal:
            b = b + n
        else:
            r = r + n
    b,r = b/(nB+1/float("inf")), r/(nR+1/float("inf"))
    return b**2/(b+r)


def merge2(col1, col2):
    """
    -- If the whole is as good (or simpler) than the parts,
    -- then return the 
    -- combination of 2 `col`s.
    -- Called by function `mergeMany`.
    """
    new = merge(col1,col2)
    if new.div() <= (col1.div()*col1.n + col2.div()*col2.n)/new.n:
        return new

def merges(ranges0,nSmall,nFar):
    """
    -- Given a sorted list of ranges, try fusing adjacent items
    -- (stopping when no more fuse-ings can be found). When done,
    -- make the ranges run from minus to plus infinity
    -- (with no gaps in between).
    """
    def tyr2merge(left,right,j):
        y = merged(left['y'], right['y'], nSmall, nFar)
        if y: 
            j = j+1
            left['hi'], left['y'] = right['hi'], y
        return j , left

    def noGaps(t):
        if not t:
            return t
        for j in range(1,len(t)):
            t[j]['lo'] = t[j-1]['hi']
        t[0]['lo']  = float('-inf')
        t[len(t)-1]['hi'] =  float('inf')
        return t

    ranges1,j,here = [],0, None
    while j < len(ranges0):
        here = ranges0[j]
        if j < len(ranges0)-1:
            j,here = tyr2merge(here, ranges0[j+1], j)
        j=j+1
        ranges1.append(here)
    return noGaps(ranges0) if len(ranges0)==len(ranges1) else merges(ranges1,nSmall,nFar)
    
    
def merged(col1,col2,nSmall, nFar):
    """
    -- If (1) the parts are too small or
    -- (2) the whole is as good (or simpler) than the parts,
    -- then return the merge.
    """
    new = merge(col1,col2)
    if nSmall and col1.n < nSmall or col2.n < nSmall:
        return new
    if nFar   and not type(col1) == Sym and abs(col1.div() - col2.div()) < nFar:
        return new
    if new.div() <= (col1.div()*col1.n + col2.div()*col2.n)/new.n:
        return new

def mergeAny(ranges0):
    """
    -- Given a sorted list of ranges, try fusing adjacent items
    -- (stopping when no more fuse-ings can be found). When done,
    -- make the ranges run from minus to plus infinity
    -- (with no gaps in between).
    -- Called by function `bins`.
    """
    def noGaps(t):
        for j in range(1,len(t)):
            t[j]['lo'] = t[j-1]['hi']
        t[0]['lo']  = float("-inf")
        t[len(t)-1]['hi'] =  float("inf")
        return t

    ranges1,j = [],0
    while j <= len(ranges0)-1:
        left = ranges0[j]
        right = None if j == len(ranges0)-1 else ranges0[j+1]
        if right:
            y = merge2(left['y'], right['y'])
            if y:
                j = j+1
                left['hi'], left['y'] = right['hi'], y
        ranges1.append(left)
        j = j+1
    return noGaps(ranges0) if len(ranges0)==len(ranges1) else mergeAny(ranges1)

def prune(rule, maxSize):
    """
    takes a dictionary rule and a dictionary maxSize as input and returns the modified dictionary rule.
    """
    n = 0
    for txt, ranges in rule.items():
        n = n + 1
        if(len(ranges) == maxSize[txt]):
            n = n+1
            rule[txt] = None
    if n > 0:
        return rule

def firstN(sort_ranges,s_fun):
    """
    takes a list sort_ranges and a function s_fun as input, and returns a tuple containing the output of s_fun and the maximum value of a certain quantity.
    """
    print(" ")
    def function(num):
        print(num['range']['txt'],
              num['range']['lo'],
              num['range']['hi'],
              rnd(num['val']),
              num['range']['y'].has)
    
    def useful(val):
        if val['val']> first_val/10 and val['val']>.05:
            return val
    
    _ = list(map(function, sort_ranges))
    print()
    
    first_val = sort_ranges[0]['val']
    sort_ranges = [x for x in sort_ranges if useful(x)]
    
    most,out = -1, -1
    for n in range(1,len(sort_ranges)+1):
        sliced_val = sort_ranges[0:n]
        slice_val_range = [x['range'] for x in sliced_val]
        temp,rule = s_fun(slice_val_range)
        if temp and temp > most:
            out,most = rule,temp
    
    return out,most
    
def samples(t,n=0):
    """
    function samples that takes argument t and n.
    n here is None by default unless specified.
    """
    u = []
    for i in range(1, n or len(t)+1):
        u.append(t[random.randint(0, len(t)-1)])
    return u
    
def gaussian(mu,sd):
    """
    n;
    return a sample from a Gaussian with mean `mu` and sd `sd`
    """
    mu = mu or 0
    sd = sd or 1
    return mu + sd * math.sqrt(-2 * math.log(random.random())) * math.cos(2 * math.pi * random.random())
    
def delta(i, other):
    """
    calculating Cohen's d, which is a common effect size measure that standardizes the difference between means by dividing by the pooled standard deviation of the two groups.
    """
    e, y, z = 1E-32, i, other
    return abs(y.mu - z.mu) / ((e + y.sd**2/y.n + z.sd**2/z.n)**0.5)
    
def bootstrap(y0, z0):
    """
    --- x will hold all of y0,z0
    --- y contains just y0
    --- z contains just z0
    --- tobs is some difference seen in the whole space
    --- yhat and zhat are y,z fiddled to have the same mean
    -- if we have seen enough n, then we are the same
    -- On Tuesdays and Thursdays I lie awake at night convinced this should be "<"
    -- and the above "> obs" should be "abs(delta - tobs) > someCriticalValue".
    """
    x, y, z, yhat, zhat = Num(), Num(), Num(), [], []
    for y1 in y0:
        x.add(y1)
        y.add(y1)

    for z1 in z0:
        x.add(z1)
        z.add(z1)
  
    xmu, ymu, zmu = x.mu, y.mu, z.mu
  
    for y1 in y0:
        yhat.append(y1 - ymu + xmu)
  
    for z1 in z0:
        zhat.append(z1 - zmu + xmu)
    
  
    tobs = delta(y,z)
    n = 0
    for i in range(0,the['bootstrap'] + 1):
        if delta(Num(t = samples(yhat)), Num(t = samples(zhat))) > tobs:
            n = n + 1 
   
    return (n/the['bootstrap']) >= the['conf']

def RX(t,s):
    """
    takes argument t and s where s is defaulted to None unless specified.
    sort t and return a dictionary based on value of s
    """
    t.sort()
    
    if s == None:
        return {'name': '', 'rank': 0, 'n': len(t), 'show': '', 'has': t}
    
    return {'name': s, 'rank': 0, 'n': len(t), 'show': '', 'has': t}
    
    
def div(t):
    """
    operation based on presence of 'has' in `t`.
    """
    if 'has' in t.keys():
        t = t['has']
    
    return (t[int(len(t)*9/10)] - t[int(len(t)*1/10)]) / 2.56
    
    
def mid(t):
    """
    calculates the median of a list of numbers.
    """
    if 'has' in t.keys():
        t = t['has']
    
    n = len(t) // 2
    if len(t) % 2 == 0:
        return (t[n] + t[n+1])/2
        
    return t[n+1]
    

def data_manipulation(file, DATA):
    df = pd.read_csv(file)
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].mean(), inplace=True)
        for col in df.columns[df.eq('?').any()]:
            if df[col].dtype == 'O':
                df = df[df[col] != "?"]
            else:
                df[col] = df[col].replace('?', np.nan)
                df[col] = df[col].astype(float)
                df[col].fillna(df[col].mean(), inplace=True)


    oe = OrdinalEncoder()
    for col in df.select_dtypes(include=['object']):
        if col.strip()[0].islower():
            df[col] = oe.fit_transform(df[[col]])

    
    file = file.replace('.csv', '_modified.csv')
    df.to_csv(file, index=False)
    return DATA(file)
