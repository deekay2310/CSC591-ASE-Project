from misc import *
from explain import *
from explain2 import *
from Data import *
from tabulate import tabulate
import numpy as np
import csv
import os
import sys
import argparse



tbl1 = {'all': {'data' : [], 'evals' : 0},
             'sway1': {'data' : [], 'evals' : 0},
             'sway2': {'data' : [], 'evals' : 0},
             'xpln1': {'data' : [], 'evals' : 0},
             'xpln2': {'data' : [], 'evals' : 0},
             'top': {'data' : [], 'evals' : 0}}

tbl2 = [[['all', 'all'],None],
                [['all', 'sway1'],None],
                [['sway1', 'sway2'],None],
                [['sway1', 'xpln1'],None],
                [['sway2', 'xpln2'],None],
                [['sway1', 'top'],None]]


def main():
    parser = argparse.ArgumentParser(description='Read CSV file')
    parser.add_argument('-file', type=str, help='CSV filename')

    args = parser.parse_args()

    filename = args.file

    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    
    data_file_path = os.path.join(parent_dir, "data", filename)

    iterations = 0
    while iterations < the['n_iter']:
        data = DATA(data_file_path)
        data = data_manipulation(data_file_path, DATA)
        best,rest,evals = data.sway()
        best2,rest2,evals2 = data.sway2()
        xp = XPLN(best, rest)
        xp2 = XPLN2(best2, rest2)
        rule,_= xp.xpln(data,best,rest)
        rule2,_ = xp2.xpln2(data,best2,rest2)
        if rule != -1 and rule2 != 1:
            betters, _ = data.betters(len(best.rows))
            tbl1['top']['data'].append(DATA(data,betters))
            tbl1['xpln1']['data'].append(DATA(data,selects(rule,data.rows)))
            tbl1['xpln2']['data'].append(DATA(data,selects(rule2,data.rows)))
            tbl1['all']['data'].append(data)
            tbl1['sway1']['data'].append(best)
            tbl1['sway2']['data'].append(best2)
            tbl1['all']['evals'] += 0
            tbl1['sway1']['evals'] += evals
            tbl1['sway2']['evals'] += evals2
            tbl1['xpln1']['evals'] += evals
            tbl1['xpln2']['evals'] += evals2
            tbl1['top']['evals'] += len(data.rows)
            
            for i in range(len(tbl2)):
                [base, diff], result = tbl2[i]
                if result == None:
                    tbl2[i][1] = ['=' for _ in range(len(data.cols.y))]
                for k in range(len(data.cols.y)):
                    if tbl2[i][1][k] == '=':
                        y0, z0 = tbl1[base]['data'][iterations].cols.y[k],tbl1[diff]['data'][iterations].cols.y[k]
                        is_equal = bootstrap(y0.vals(), z0.vals()) and cliffsDelta(the, y0.vals(), z0.vals())
                        if not is_equal:
                            tbl2[i][1][k] = '≠'
            iterations += 1
    headers = [y.txt for y in data.cols.y]
    res = []
    print(headers)
    
    for k1,v1 in tbl1.items():
        u = {}
        for x in v1['data']:
            for k,v in x.stats().items():
                u[k] = u.get(k,0) + v
        for k,v in u.items():
            u[k] /= the['n_iter']
        
        out = [k1] + [u[y] for y in headers]
        out += [v1['evals']/the['n_iter']]
        res.append(out)
    
    print(tabulate(res, headers=headers+["avg num_evals"], numalign="right"))
    print()
    
    res = []
    for [base, diff], result in tbl2:
        res.append([f"{base} to {diff}"] + result)
    print(tabulate(res, headers=headers,numalign="right"))
    
if __name__ == '__main__':
    main()
