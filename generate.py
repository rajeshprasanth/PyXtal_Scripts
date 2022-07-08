#!/usr/bin/env python3
#
import os
import itertools
from pyxtal.crystal import random_crystal
from pyxtal.symmetry import get_symbol_and_number
from spglib import get_symmetry_dataset
from time import time
import numpy as np
from datetime import timedelta
from pyxtal import pyxtal




#
sg_min_3d=2
sg_max_3d=230
#
dimension=3
minatom=1
maxatom=8
elementlist=['Si','Ge','Sn']
#elementlist=['Si']
maxstruct=50
#
verbosity = "high"
#
#---------------------------
#Do not touch below
#
genstruct=0
#
failed_cnt=0
success_cnt=0

def generator_fn(minatom,maxatom,elementlist):
	final=[]
	for pattern in itertools.product(range(0,maxatom+1), repeat = len(elementlist)):
		if sum(list(pattern)) >= minatom and sum(list(pattern)) <= maxatom:
			final.append(list(pattern))
	return final



def generate():
	
	start_time = time()
	genstruct=0
#
	failed_cnt=0
	success_cnt=0
	for j in range(len(numion)):
		for sg in range(2,231):
			try:
				if verbosity == "high":
					print(" ==================================================")
					print(" Structure # ",genstruct+1,"/",len(numion)*len(range(2,231)))
					print(" ==================================================")
					print(" Requested Composition   : ",elementlist,"->",numion[j])

					req_symbol, temp = get_symbol_and_number(sg, dimension)
					print(" Requested Spacegroup #  : ",sg,"(",req_symbol,")")
					#
					#
					#
					rand_crystal = pyxtal()
					rand_crystal.from_random(dimension,sg, elementlist,numion[j])

					if rand_crystal.valid:
						print(" Generation Status       :  [SUCCESS]",)
						success_cnt += 1
					else:
						print(" Generation Status       :  [FAILED]",)
						failed_cnt += 1
					print(" Strucures completed  #  : {:10d} ".format(success_cnt))
					print(" Strucures failed     #  : {:10d} ".format(failed_cnt))
					#
					write_to_file(rand_crystal,genstruct+1)
					#
					print(" Output file             : ./output/{:s}.vasp".format(str(genstruct+1)))
					end = time()
					timespent = np.around((end - start), decimals=2)
					td_str = str(timedelta(seconds=timespent)).split(':')
					#
					print(" Time Elapsed            : {:2d}h : {:2d}m : {:.2f}s\n".format(int(td_str[0]),int(td_str[1]),float(td_str[2])))
					print(" ==================================================")
					genstruct += 1
				else:
					rand_crystal = pyxtal()
					rand_crystal.from_random(dimension,sg, elementlist,numion[j])
					success_cnt += 1
					genstruct += 1
				
			except Exception as e:
				if verbosity == "high":
					print(" Generation Status       :  [FAILED]",)
					failed_cnt += 1
					print(" Strucures completed  #  : {:10d} ".format(success_cnt))
					print(" Strucures failed     #  : {:10d} ".format(failed_cnt))
					end = time()
					timespent = np.around((end - start), decimals=2)
					td_str = str(timedelta(seconds=timespent)).split(':')
					print(" Time Elapsed            : {:2d}h : {:2d}m : {:.2f}s\n".format(int(td_str[0]),int(td_str[1]),float(td_str[2])))
					print(" ==================================================")
					genstruct += 1
				else:
					failed_cnt += 1
					genstruct += 1
	end_time = time()
	return (genstruct,success_cnt,failed_cnt)

def summary(genstruct,success_cnt,failed_cnt,start_time,end_time):
	print(" ")
	print(" >>> ==================================================")
	print(" >>> Summary")
	print(" >>> ==================================================")
	print(" >>> structures generated   # : {:10d} ({:.2f}%)".format(genstruct,((float(genstruct)*100.0)/float(genstruct))))
	print(" >>> --------------------------------------------------")
	print(" >>> structures valid       # : {:10d} ({:.2f}%)".format(success_cnt,((float(success_cnt)*100.0)/float(genstruct))))
	print(" >>> structures invalid     # : {:10d} ({:.2f}%)".format(failed_cnt,((float(failed_cnt)*100.0)/float(genstruct))))
	print(" >>> ==================================================")
	print(" >>> Total Structures       # : {:10d} ({:.2f}%)".format((success_cnt+failed_cnt),(float(100.0))))
	print(" >>> ==================================================")
	timespent = np.around((end_time - start_time), decimals=2)
	td_str = str(timedelta(seconds=timespent)).split(':')
	print(" >>> Total time Elapsed       : {:2d}h : {:2d}m : {:.2f}s".format(int(td_str[0]),int(td_str[1]),float(td_str[2])))
	print(" >>> ==================================================")


def write_to_file(crystal,genstruct):
	if not os.path.exists('output'):
        	os.mkdir('output/')

	filename = str('output/') + str(genstruct) +'.vasp'
	crystal.to_ase().write(filename, format='vasp', vasp5=True,direct=True)

numion = generator_fn(minatom,maxatom,elementlist)
start=time()
genstruct,success_cnt,failed_cnt = generate()
end=time()
summary(genstruct,success_cnt,failed_cnt,start,end)

