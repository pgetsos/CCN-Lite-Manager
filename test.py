#!/usr/bin/python3.5

import sys
from test1 import run_auto_11, run_auto_12
from test2 import run_auto_21, run_auto_22
from test3 import run_auto_31, run_auto_32
from test4 import run_auto_41, run_auto_42, run_auto_43
from test5 import run_auto_51
from test6 import run_auto_61


if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] == "test":
			if sys.argv[2] == "11":
				run_auto_11()
			elif sys.argv[2] == "12":
				run_auto_12()
			elif sys.argv[2] == "21":
				run_auto_21()
			elif sys.argv[2] == "22":
				run_auto_22()
			elif sys.argv[2] == "31":
				run_auto_31()
			elif sys.argv[2] == "32":
				run_auto_32()
			elif sys.argv[2] == "41":
				run_auto_41()
			elif sys.argv[2] == "42":
				run_auto_42()
			elif sys.argv[2] == "43":
				run_auto_43()
			elif sys.argv[2] == "51":
				run_auto_51(sys.argv[3])
			elif sys.argv[2] == "61":
				run_auto_61(sys.argv[3])
