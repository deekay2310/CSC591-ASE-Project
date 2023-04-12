
from Sym import *
from Num import *
from Data import *
from misc import *
import random



egs = {}
def eg(key, str, fun):
    egs[key] = fun

def SYM(the):
    sym = Sym()
    for x in ["a","a","a","a","b","b","c"]:
        sym.add(x)
    if "a" == sym.mid() and 1.379 == rnd(sym.div()):
        return True
    else:
        return False

def NUM(the):
    num = Num()
    for x in [1,1,1,1,2,2,3]:
        num.add(x)
    if 11/7 == num.mid() and 0.787 == rnd(num.div()):
        return True
    else:
        return False

def THE(the):
    oo(the)

def RAND(the):
    num1  = Num()
    num2 = Num()
    random.seed = the["seed"]
    for _ in range(1, (10**3)):
        num1.add(rand(0, 1, the["seed"]))
    random.seed = the["seed"]
    for _ in range(1, (10**3)):
        num2.add(rand(0, 1, the["seed"]))
    m1 = rnd(num1.mid(), 10)
    m2 = rnd(num2.mid(), 10)
    if m1 == m2 and .6  == rnd(m1, 1):
        return True
    else:
        return False

def CSV(the):
    n = 0
    def fun(t):
        nonlocal n 
        n = n + len(t)
    csv('data/data.csv', fun)
    return n == 8*399

def DATA(the):
    data = Data(str(the['file']))
    print("DATAA", data.cols.x)
    return len(data.rows) == 398 and len(data.cols.x) == 4 and int(data.cols.x[1].at) == 1 and int(data.cols.y[1].w) == -1

def CLONE(the):
    data1 = Data('data/data.csv')
    data2 = data1.clone(data1.rows)
    return len(data1.rows) == len(data2.rows) and len(data1.cols.x) == len(data2.cols.x) and int(data1.cols.x[1].at) == int(data2.cols.x[1].at) and int(data1.cols.y[1].w) == int(data2.cols.y[1].w)

def STATS(the):
    data = Data(str(the['file']))
    dict = {'y': data.cols.y, 'x': data.cols.x }
    for k,cols in dict.items():
            print(k, "   ", "mid", "   ", o(data.stats("mid", cols, 2)))
            print("", "    ", "div", "   ", o(data.stats("div", cols, 2)))

def AROUND(the):
    data = Data(str(the['file']))
    print("Data", data)
    print(0, 0, o(data.rows[1].cells))
    for i, t in enumerate(data.around(data.rows[1], the)):
        if i%50 == 0:
            print(i, t['dist'], (t['row'].cells))

def HALF(the):
    data = Data(str(the["file"]))
    left, right, A, B, mid, c = data.half(the)
    print(len(left), len(right), len(data.rows))
    print(o(A.cells), c)
    print(o(mid.cells))
    print(o(B.cells))

def CLUSTER(the):
    data = Data(str(the['file']))
    show(data.cluster(the), "mid", data.cols.y, 1)
    
    
def OPTIMIZE(the):
    data = Data(str(the['file']))
    show(data.sway(the), "mid", data.cols.y,1)

def SWAY(the):
    data = Data(str(the['file']))
    best,rest,_ = data.sway(the)
    print("\nall ", data.stats('mid', data.cols.y, 2))
    print("    ", data.stats('div', data.cols.y, 2))
    print("\nbest",best.stats('mid', best.cols.y, 2))
    print("    ", best.stats('div', best.cols.y, 2))
    print("\nrest", rest.stats('mid', rest.cols.y, 2))
    print("    ", rest.stats('div', rest.cols.y, 2))


def BINS(the):
    data = Data(str(the['file']))
    best,rest,_= data.sway(the)
    print("all","","","",{'best':len(best.rows), 'rest':len(rest.rows)})
    for k,t in enumerate(bins(the,data.cols.x,{'best':best.rows, 'rest':rest.rows})):
        for range in t:
            print(range['txt'],range['lo'],range['hi'],rnd(value(range['y'].has, len(best.rows),len(rest.rows),"best")),range['y'].has)

def XPLN(the):
    data = Data(str(the['file']))
    best, rest, evals = data.sway(the)
    rule, most = data.xpln(best, rest, the)
    print("\n-----------\nexplain=", data.showRule(rule))
    selects = data.selects(rule,data.rows)
    data_selects = [s for s in selects if s!=None]
    data1= data.clone(data_selects)
    print("all               ",data.stats('mid', data.cols.y, 2),data.stats('div', data.cols.y, 2))
    print("sway with",evals,"evals",best.stats('mid', best.cols.y, 2),best.stats('div', best.cols.y, 2))
    print("xpln on",evals,"evals",data1.stats('mid', data1.cols.y, 2),data1.stats('div', data1.cols.y, 2))
    top,_ = data.betters(len(best.rows))
    top = data.clone(top)
    print("sort with",len(data.rows),"evals",top.stats('mid', top.cols.y, 2),top.stats('div', top.cols.y, 2))



eg("sym", "check syms", SYM)
eg("num", "check nums", NUM)
eg("the", "show settings", THE)
eg("rand", "generate, reset, regenerate same", RAND)
eg("csv", "read from csv", CSV)
# eg("sway", "optimizing", SWAY)
# eg("bins", "find deltas between best and rest", BINS)
eg("xpln","explore explanation sets", XPLN)
# eg("data", "read DATA csv", DATA)
# eg("clone", "duplicate structure", CLONE)
# eg("stats", "stats from DATA", STATS)
# eg("around", "sorting nearest neighbors", AROUND)
# eg("half", "1-level bi-clustering", HALF)
# eg("cluster", "N-level bi-clustering", CLUSTER)
# eg("optimize", "semi-supervised optimization", OPTIMIZE)





def test(the):
    fails = 0
    for what, fun in egs.items():
        if the['go'] == "all" or what == the['go']:
            random.seed = the["seed"]
            if egs[what] == "SYM" or egs[what] == "NUM" or egs[what] == "CSV" or egs[what] == 'CLONE':
                if egs[what]() == False:
                    fails += 1
                    print("❌ fail:",what)
                else:
                    print("✅ pass:",what) 
            else:
                if egs[what](the) == False:
                    fails += 1
                    print("❌ fail:",what)
                else:
                    print("✅ pass:",what)  

