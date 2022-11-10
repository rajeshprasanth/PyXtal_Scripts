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



def generate_ions_list(min_atom_in,max_atom_in,atomic_elements_in):
	ions_list = []
	temp0_list = []
	temp1_list = []
	#
	# Generate number of ions
	#
	for pattern in itertools.product(range(0,max_atom_in+1), repeat = len(atomic_elements_in)):
		if sum(list(pattern)) >= min_atom_in and sum(list(pattern)) <= max_atom_in:
			temp0_list.append(list(pattern))
	#
	# Build dictionary out of zipped atomic_elements_in and number of ions
	#
	for i in temp0_list:
		 temp1_list.append(dict(zip(atomic_elements_in,i)))
	#
	# Cleanup zero value atomic_elements_in from list
	#
	for i in temp1_list:
		dic_in = i
		dic_out = {x:y for x,y in dic_in.items() if y!=0}
		ions_list.append(dic_out)
	#print(ions_list)
	#print(ions_list[0]['Si'])
	return ions_list

def dict2list(dict_in):
	#
	# Converts input dictionary to list
	#
	elements_list = list(dict_in.keys())
	num_ions_list = list(dict_in.values())
	return elements_list,num_ions_list


def generate_crystal(dimension_in,sg_in,elementlist_in,ionslist_in):
	#
	# Create initiator for pyxtal method
	#
	rand_crystal = pyxtal()
	#
	# Generate random cell for given inputs
	#
	start_time = time()
	try:
		rand_crystal.from_random(dimension_in,sg_in, elementlist_in,ionslist_in)
	except Exception as e:
		pass
	end_time = time()
	#
	# Verify the structure is valid.
	#
	if rand_crystal.valid:
		isvalid = 1
	else:
		isvalid = 0
	return(isvalid,rand_crystal,start_time,end_time)

def main(min_atom_in,max_atom_in,atomic_elements_in,sg_start_in,sg_end_in,dimension_in,outdir_in,prefix_in):
	start_time = time()
	#
	# Initialize lists
	#
	elementlist = []
	ionslist = []
	#
	# Initialize counters
	#
	genstruct=0
	failed_cnt=0
	success_cnt=0
	#
	# Generates list of elements and corresponding number of ions
	#
	ions = generate_ions_list(min_atom_in,max_atom_in,atomic_elements_in)
	#
	# convert list of elements and corresponding number of ions to pyxtal format
	#
	for i in ions:
		a,b = dict2list(i)
		elementlist.append(a)
		ionslist.append(b)
	#
	# Generate random cell for given inputs
	#
	for i in range(len(elementlist)):
		for sg in range(sg_start_in,sg_end_in+1):
			#
			# Call generate_cell function
			#
			valid,crystal,starting_time,ending_time = generate_crystal(dimension_in,sg,elementlist[i],ionslist[i])
			#
			# Verbose output
			# 
			if verbosity == "high":
				#
				print(" ==================================================")
				print(" Structure # ",genstruct+1,"/",len(elementlist)*len(range(sg_start,sg_end)))
				print(" ==================================================")
				print(" Requested Composition   : ",elementlist[i],"->",ionslist[i])
				#
				# use Spglib to find the corresponding spacegroup number
				# 
				req_symbol, temp = get_symbol_and_number(sg, dimension_in)
				print(" Requested Spacegroup #  : ",sg,"(",req_symbol,")")
				
				#ans = get_symmetry_dataset(crystal, symprec=1e-1)["international"]
				#req_symbol, temp = get_symbol_and_number(ans, dimension_in)
				#print(" Generated Spacegroup #  : ",ans,"(",req_symbol,")")
				#print(dir(crystal))
				#
				# Check validity and print status and write output to file
				# 
				if valid == 1:
					#
					# If valid update status as SUCCESS and write the data to file
					# 
					print(" Generation Status       :  [SUCCESS]",)
					#
					# Create directory, if doesn't exist
					# 
					if not os.path.exists(outdir_in):
        					os.mkdir(outdir_in)
					#
					filename = str(outdir_in) +'/'+ prefix_in + '.' +str(genstruct+1) +'.vasp'
					#
					# Convert crystal to vasp output and write to file
					# 
					crystal.to_ase().write(filename, format='vasp', vasp5=True,direct=True)
					
					print(" Output file             : {:s}/{:s}.{:s}.vasp".format(outdir,prefix,str(genstruct+1)))
					success_cnt += 1
				else:
					print(" Generation Status       :  [FAILED]",)
					failed_cnt += 1
				print(" Strucures completed  #  : {:10d} ".format(success_cnt))
				print(" Strucures failed     #  : {:10d} ".format(failed_cnt))
				timespent = np.around((ending_time - starting_time), decimals=2)
				td_str = str(timedelta(seconds=timespent)).split(':')
				print(" Time spent              : {:2d}h : {:2d}m : {:.2f}s".format(int(td_str[0]),int(td_str[1]),float(td_str[2])))
				#
				current_time = time()
				timespent = np.around((current_time - start_time), decimals=2)
				td_str = str(timedelta(seconds=timespent)).split(':')
				print(" Time Elapsed            : {:2d}h : {:2d}m : {:.2f}s\n".format(int(td_str[0]),int(td_str[1]),float(td_str[2])))
				
				print(" ==================================================")
				genstruct += 1
			else:	
				if valid == 1:
					if not os.path.exists(outdir):
						os.mkdir(outdir)
					#
					filename = str(outdir) +'/'+ prefix +str(genstruct+1) +'.vasp'
					#
					# Convert crystal to vasp output and write to file
					# 
					crystal.to_ase().write(filename, format='vasp', vasp5=True,direct=True)
					success_cnt += 1
					genstruct += 1
				else:
					failed_cnt += 1
					genstruct += 1

	end_time = time()
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

#main(min_atom,max_atom,atomic_elements,sg_start,sg_end,dimension,outdir,prefix)
#
# 
#
#------------------#
# Input Parameters #
#------------------#
min_atom = 1
max_atom = 12
atomic_elements = ['Mg','Si','Ge','Sn']
#atomic_elements = ['Mg']
dimension = 3
verbosity = 'high'
outdir = './output/'
prefix = 'cfg'
fixed_composition = False
composition = []

if dimension == 3:
	sg_start = 2
	sg_end = 230

main(min_atom,max_atom,atomic_elements,sg_start,sg_end,dimension,outdir,prefix)

