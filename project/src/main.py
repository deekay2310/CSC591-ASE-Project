from misc import cli
import sys
from test_engine import test


help = """   
script.lua : an example script with help text and a test suite
(c)2022, Tim Menzies <timm@ieee.org>, BSD-2 
USAGE:   script.lua  [OPTIONS] [-g ACTION]
OPTIONS:
  -d  --dump  on crash, dump stack = false
  -f  --file    name of file       = data/data.csv
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

the = cli(sys.argv[1:])

test(the)
if the['help']:
    exit (print("\n" + str(help) + "\n"))


