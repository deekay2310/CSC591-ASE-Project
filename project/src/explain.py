from misc import *

the = { 'dump': False, 'go': None, 'seed': 937162211, 'bootstrap':512, 'conf':0.05, 'cliff':.4, 'cohen':.35, 'Fmt': "{:.2f}", 'width':40, 'n_iter': 20, 'min': 0.5, 'Halves': 512, 'Far': 0.95, 'Reuse': True, 'rest': 10, 'bins': 16, 'd': 0.35}


class XPLN:
    def __init__(self, best, rest):
        self.tmp = []
        self.maxSizes = {}
        self.best = best
        self.rest = rest

    def score(self, ranges):
        rule = self.RULE(ranges, self.maxSizes)
        if rule:
            bestr = selects(rule, self.best.rows)
            restr = selects(rule, self.rest.rows)
            if len(bestr) + len(restr) > 0:
                return value({'best': len(bestr), 'rest': len(restr)}, len(self.best.rows), len(self.rest.rows), 'best'), rule
        return None,None
    
    def firstN(self, sort_ranges, s_fun):
        """
        takes a list sort_ranges and a function s_fun as input, and returns a tuple containing the output of s_fun and the maximum value of a certain quantity.
        """
        
        
        def useful(val):
            if val['val']> first_val/10 and val['val']>.05:
                return val
        
        
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



    def xpln(self, data, best, rest):
        def v(has):
            return value(has, len(best.rows), len(rest.rows), 'best')
        
        tmp,self.maxSizes = [],{}
        for _,ranges in enumerate(bins(data.cols.x,{'best':best.rows, 'rest':rest.rows})):
            self.maxSizes[ranges[0]['txt']] = len(ranges)
            for _,range in enumerate(ranges):
                tmp.append({'range':range, 'max':len(ranges),'val': v(range['y'].has)})
        rule,most=self.firstN(sorted(tmp,key = lambda x: x['val'],reverse=True),self.score)
        return rule,most
    
    def prune(self, rule, maxSize):
        """
        takes a dictionary rule and a dictionary maxSize as input and returns the modified dictionary rule.
        """
        n = 0
        rule2 = {}
        for txt, ranges in rule.items():
            n = n + 1
            if(len(ranges) == maxSize[txt]):
                n -= 1
                rule[txt] = None
            else:
                rule2[txt] = ranges
        if n > 0:
            return rule2
        else:
            return None
                
    
    def RULE(self, ranges,maxSize):
        """
        takes a list of dictionaries containing information about ranges, and an integer maxSize as input, and returns a pruned version of the dictionary of ranges.
        """
        t = {}
        for range in ranges:
            t[range['txt']] = t.get(range['txt'], []) 
            t[range['txt']].append({'lo' : range['lo'],'hi' : range['hi'],'at':range['at']})
        return self.prune(t, maxSize)

def selects(rule, rows):
    """
    takes a dictionary of rules and a list of rows as input, and returns a list of rows that satisfy the rules.
    """
    def disjunction(ranges, row):
        for rang in ranges:
            at = rang['at']
            x = row.cells[at]
            lo = rang['lo']
            hi = rang['hi']  
            if x == '?' or (lo == hi and lo == x) or (lo <= x and x< hi):
                return True
        return False

    def conjunction(row):
        for _,ranges in rule.items():
            if not disjunction(ranges, row):
                return False
        return True

    def function(r):
        return r if conjunction(r) else None
    
    r = []
    for item in list(map(function, rows)):
        if item:
            r.append(item)
    return r