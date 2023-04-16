import math 
import re
import sys
import random
from csv import reader
from Sym import *
import copy
import io
from Num import *

# the = {'bootstrap': 512, 'conf' : 0.05, 'cliff' : 0.4, 'cohen' : 0.35, 'Fmt' : """'%6.2f'""", 'width' : 40}


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
    for i in t:
        k = t.index(i)
        i, k =fun(k,i)
        x[k or len(x)] = i
    return x

def dkap(t, fun):
    """
    takes a dictionary t and a function fun as input, applies the function to the keys and values of the dictionary, and returns a new dictionary.
    """
    u = {}
    print("t is ",t)
    print("fun is ",fun)
    for k,v in t.items():
        v, k = fun(k,v) 
        u[k or len(u)] = v
    return u

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
    temp = 1 if c == 0 else 2*c
    x1 = (a**2 + c**2 - b**2) // temp
    x2 = max(0, min(1, x1)) 
    y  = abs((a**2 - x2**2)**0.5)
    return x2, y

def coerce(s):
    """
    -- Coerce string to boolean, int,float or (failing all else) strings.
    """
    def fun(s1):
        if s1 == "true":
            return True
        elif s1 == "false":
            return False
        else:
            return s1
    if s.isnumeric():
        return int(s)
    elif type(s) != bool:
        return fun(re.search('^[\s]*[\S+]*[\s]*$', s).group(0))

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
    t = {}
    for k,v in re.findall("[-][\S]+[\s]+[-][-]([\S]+)[^\n]+= ([\S]+)", s): 
        t[k] = coerce(v)
    return t

def cli(command_line_args):
    """
    -- Update `t` using command-line options. For boolean
    -- flags, just flip the default values. For others, read
    -- the new value from the command line.
    """
    options = {}
    options = settings(help)
    for k, v in options.items():
        v = str(v)
        for n, x in enumerate(command_line_args):
            if x == '-'+k[0] or x == '--'+k:
                if v == "true":
                    v = "false"
                elif v == "false":
                    v = "true"
                else:
                    v = command_line_args[n+1]
        options[k] = coerce(v)

    return options

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
    if(len(ns1)>256):
        ns1 = many(ns1, 256)
    if(len(ns2)>256):
        ns2 = many(ns2, 256)
    if(len(ns1)>10*len(ns2)):
        ns1 = many(ns1, 10*len(ns2))
    if(len(ns2)>10*len(ns1)):
        ns2= many(ns2, 10*len(ns1))
    
    n, gt, lt = 0, 0, 0
    for _,x in enumerate(ns1):
        for _,y in enumerate(ns2):
            n+=1
            if x > y:
                gt = gt + 1
            if x < y: 
                lt = lt + 1
    
    return abs(lt-gt)/n > the['cliffs']

def bins(the,cols,rowss):
    """
    -- Return RANGEs that distinguish sets of rows (stored in `rowss`).
    -- To reduce the search space,
    -- values in `col` are mapped to small number of `bin`s.
    -- For NUMs, that number is `the.bins=16` (say) (and after dividing
    -- the column into, say, 16 bins, then we call `mergeAny` to see
    -- how many of them can be combined with their neighboring bin).
    """
    out =[]
    for col in cols:
        ranges = {}
        for y, rows in rowss.items():
            for row in rows:
                x = row.cells[col.at]
                if x!= '?':
                    k = int(bin(the,col,x))
                    if not k in ranges:
                        ranges[k] = RANGE(col.at, col.txt, x)
                    extend(ranges[k], x, y)
        ranges = list(dict(sorted(ranges.items())).values())
        if(isinstance(col, Sym)):
            r = ranges
        else:
            r = mergeAny(ranges)
        out.append(r)
    return out

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

def RANGE(at,txt,lo,hi=None):
    """
    -- Create a RANGE  that tracks the y dependent values seen in 
    -- the range `lo` to `hi` some independent variable in column number `at` whose name is `txt`. 
    -- Note that the way this is used (in the `bins` function, below)
    -- for  symbolic columns, `lo` is always the same as `hi`.
    """
    return {'at':at,'txt':txt,'lo':lo,'hi':lo or hi or lo,'y':Sym()}

def extend(range,n,s):
    """
    -- Update a RANGE to cover `x` and `y`
    """
    range['lo'] = min(float(n), float(range['lo']))
    range['hi'] = max(float(n), float(range['hi']))
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


def merge2(col1,col2):
    """
    -- If the whole is as good (or simpler) than the parts,
    -- then return the 
    -- combination of 2 `col`s.
    -- Called by function `mergeMany`.
    """
    new = merge(col1,col2)
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