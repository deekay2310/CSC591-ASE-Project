import math
import random
import re
from Num import *

the = { 'dump': False, 'go': None, 'seed': 937162211, 'bootstrap':512, 'conf':0.05, 'cliffs':.4, 'cohen':.35, 'Fmt': "{:.2f}", 'width':40, 'n_iter': 20, 'min': 0.5, 'Halves': 512, 'Far': 0.95, 'Reuse': True, 'rest': 10, 'bins': 16, 'd': 0.35}

def erf(x, a1, a2, a3, a4, a5, p, sign): 
    """
    -- from Abramowitz and Stegun 7.1.26 
    -- https://s3.amazonaws.com/nrbook.com/AandS-a4-v1-2.pdf
    -- (easier to read at https://en.wikipedia.org/wiki/Error_function#Approximation_with_elementary_functions)
    """
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1 
    if x < 0: 
        sign = -1
    
    x = math.abs(x)
    t = 1.0 / (1.0 + p*x)
    aa = (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)
    y = 1.0 - aa * t * math.exp(-x * x)
    return sign * y 

# def gaussian(mu, sd):
#     """
#     n;
#     return a sample from a Gaussian with mean `mu` and sd `sd`
#     """
#     mu = mu if mu is not None else 0
#     sd = sd if sd is not None else 1
#     return mu + sd * math.sqrt(-2 * math.log(random.random())) * math.cos(2 * math.pi * random.random())

# def samples(t, n=None):
#     """
#     function samples that takes argument t and n.
#     n here is None by default unless specified.
#     """
#     u = []
#     for i in range(1, n or len(t)+1):
#         u.append(t[random.randint(0, len(t)-1)])
#     return u

# def cliffsDelta(ns1, ns2):
#     """
#     bool;
#     true if different by a trivial amount
#     """
#     n, gt, lt = 0, 0, 0
#     if len(ns1) > 128:
#         ns1 = samples(ns1, 128)
#     if len(ns2) > 128:
#         ns2 = samples(ns2, 128)
#     for x in ns1:
#         for y in ns2:
#             n += 1
#             if x > y:
#                 gt += 1
#             if x < y:
#                 lt += 1
#     return abs(lt - gt) / n <= the['cliff']
    
# def delta(i, other):
#     """
#     calculating Cohen's d, which is a common effect size measure that standardizes the difference between means by dividing by the pooled standard deviation of the two groups.
#     """
#     e, y, z = 1E-32, i, other
#     return abs(y.mu - z.mu) / (e + y.sd ** 2 / (y.n) + z.sd ** 2 / (z.n) ** .5)
    
# def bootstrap(y0,z0):
#     """
#     --- x will hold all of y0,z0
#     --- y contains just y0
#     --- z contains just z0
#     --- tobs is some difference seen in the whole space
#     --- yhat and zhat are y,z fiddled to have the same mean
#     -- if we have seen enough n, then we are the same
#     -- On Tuesdays and Thursdays I lie awake at night convinced this should be "<"
#     -- and the above "> obs" should be "abs(delta - tobs) > someCriticalValue".
#     """
#     x, y, z, yhat, zhat = Num(), Num(), Num(), [], []
#     for y1 in y0:
#         x.add(y1)
#         y.add(y1)

#     for z1 in z0:
#         x.add(z1)
#         z.add(z1)
  
#     xmu, ymu, zmu = x.mu, y.mu, z.mu
  
#     for y1 in y0:
#         yhat.append(y1 - ymu + xmu)
  
#     for z1 in z0:
#         zhat.append(z1 - zmu + xmu)
    
  
#     tobs = delta(y,z)
#     n = 0
#     for i in range(0,the['bootstrap'] + 1):
#         if delta(Num(samples(yhat)), Num(samples(zhat))) > tobs:
#             n = n + 1 
   
#     return (n/the['bootstrap']) >= the['conf']
  
# def RX(t, s = None):
#     """
#     takes argument t and s where s is defaulted to None unless specified.
#     sort t and return a dictionary based on value of s
#     """
#     t.sort()
    
#     if s == None:
#         return {'name': '', 'rank': 0, 'n': len(t), 'show': '', 'has': t}
    
#     return {'name': s, 'rank': 0, 'n': len(t), 'show': '', 'has': t}

# def mid(t):
#     """
#     calculates the median of a list of numbers.
#     """
#     if 'has' in t.keys():
#         t = t['has']
    
#     n = len(t) // 2
#     if len(t) % 2 == 0:
#         return (t[n] + t[n+1])/2
        
#     return t[n+1]

# def div(t):
#     """
#     operation based on presence of 'has' in `t`.
#     """
#     if 'has' in t.keys():
#         t = t['has']
    
#     return (t[int(len(t)*9/10)] - t[int(len(t)*1/10)]) / 2.56

def merge_stat(rx1, rx2):
    """
    Merges two RX objects and returns a new RX object.
    """
    rx3 = RX([], rx1['name'])
    
    rx3['has'] = rx1['has'] + rx2['has']
    rx3['has'].sort()
    rx3['n'] = len(rx3['has'])
    return rx3
    
def scottKnot(rxs):
    """
    Sorts a list of RX objects by their median and assigns ranks to each object based on Scott-Knott clustering.
    """
    def merges(i, j):
        out = RX([], rxs[i]['name'])
        for k in range(i, j + 1):
            out = merge_stat(out, rxs[j])
        return out

    def same(lo, cut, hi):
        l = merges(lo, cut)
        r = merges(cut + 1, hi)
        return cliffsDelta(l['has'], r['has']) and bootstrap(l['has'], r['has'])

    def recurse(lo, hi, rank):
        b4 = merges(lo, hi)
        cut, best = None, 0
        for j in range(lo, hi + 1):
            if j < hi:
                l = merges(lo, j)
                r = merges(j+1, hi)
                now = (l['n']*(mid(l) - mid(b4))**2 + r['n']*(mid(r) - mid(b4))**2) / (l['n'] + r['n'])
                if now > best:
                    if abs(mid(l) - mid(r)) >= the['cohen']:
                        cut, best = j, now
        if cut is not None and not same(lo, cut, hi):
            rank = recurse(lo, cut, rank) + 1
            rank = recurse(cut + 1, hi, rank)
        else:
            for i in range(lo, hi+1):
                rxs[i]['rank'] = rank
        return rank

    rxs.sort(key=lambda x: mid(x))
    cohen = div(merges(0, len(rxs) - 1)) * the['cohen']
    recurse(0, len(rxs)-1, 1)
    return rxs
    
def tiles(rxs):
    """
    ss;
    makes on string per treatment showing rank, distribution, and values
    """
    lo, hi = math.inf, -math.inf
    for rx in rxs:
        lo, hi = min(lo, rx['has'][0]), max(hi, rx['has'][-1])
    for rx in rxs:
        t, u = rx['has'], [' '] * the['width']
        
        def of(x, most):
            return max(1, min(most, x))
        
        def at(x):
            return t[of(math.floor(len(t)*x), len(t)-1)]
        
        def pos(x):
            return math.floor(of(the['width']*(x-lo)/(hi-lo+1E-32), the['width']-1))
        
        a, b, c, d, e = at(.1), at(.3), at(.5), at(.7), at(.9)
        A, B, C, D, E = pos(a), pos(b), pos(c), pos(d), pos(e)
        
        for i in range(A, B+1):
            u[i] = '-'
        
        for i in range(D, E+1):
            u[i] = '-'
        
        u[the['width']//2] = '|'
        u[C] = '*'
        x = []
        for i in [a, b, c, d, e]:
            x.append("{:6.2f}".format(i))
        rx["show"] = "".join(u) + str(x)
        
    return rxs
