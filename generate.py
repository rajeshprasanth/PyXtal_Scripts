#!/usr/bin/env python3
#
import os
import sys
import itertools
from pyxtal.crystal import random_crystal
from pyxtal.symmetry import get_symbol_and_number
from spglib import get_symmetry_dataset
from time import time
import numpy as np
from datetime import timedelta
from pyxtal import pyxtal
import configparser



class inputdata:
	def __init__(self):
		self.verbosity = None
		self.outdir = None
		self.prefix = None
		#
		self.dimension = 3
		self.calculation = None
		self.atomic_elements = None
		#
		self.min_atom = None
		self.max_atom = None
		#
		self.composition = None
		#
		self.sg_start = None
		self.sg_end = None
		
	def read_input_file(self,inputfilename):
		config = configparser.ConfigParser()
		config.read(inputfilename)
		#
		self.verbosity = str(config.get("control", "verbosity"))
		self.outdir = str(config.get("control", "outdir"))
		self.prefix = str(config.get("control", "prefix"))
		#
		self.dimension = int(config.get("system", "dimension"))
		self.calculation = str(config.get("system", "calculation"))
		self.atomic_elements = config.get("system", "atomic_elements").split(",")
		#
		self.min_atom = int(config.get("varcomp", "min_atom"))
		self.max_atom = int(config.get("varcomp", "max_atom"))
		#
		composition_str = config.get("fixedcomp", "composition").split(",")
		self.composition = list(map(int, composition_str))
		#		
		if self.dimension == 3:
			self.sg_start = 2
			self.sg_end = 230

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

def main_function(min_atom_in,max_atom_in,atomic_elements_in,sg_start_in,sg_end_in,dimension_in,outdir_in,prefix_in,verbosity_in,calculation_in,composition_in):
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
	if calculation_in == 'varcomp':
		for i in ions:
			a,b = dict2list(i)
			elementlist.append(a)
			ionslist.append(b)
	elif calculation_in == 'fixedcomp':
		elementlist.append(atomic_elements_in)
		ionslist.append(composition_in)
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
			if verbosity_in == "high":
				#
				print(" ==================================================")
				print(" Structure # ",genstruct+1,"/",len(elementlist)*len(range(sg_start_in,sg_end_in)))
				print(" ==================================================")
				print(" Running mode            : ",calculation_in)
				print(" Requested Composition   : ",elementlist[i],"->",ionslist[i])
				#
				# use Spglib to find the corresponding spacegroup number
				# 
				req_symbol, temp = get_symbol_and_number(sg, dimension_in)
				print(" Requested Spacegroup #  : ",sg,"(",req_symbol,")")
				
				ans = get_symmetry_dataset(crystal.spg_struct, symprec=1e-1)["international"]
				req_symbol, temp = get_symbol_and_number(ans, dimension_in)
				print(" Generated Spacegroup #  : ",ans,"(",req_symbol,")")
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
					
					print(" Output file             : {:s}/{:s}.{:s}.vasp".format(outdir_in,prefix_in,str(genstruct+1)))
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
					if not os.path.exists(outdir_in):
						os.mkdir(outdir_in)
					#
					filename = str(outdir_in) +'/'+ prefix_in +str(genstruct+1) +'.vasp'
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

def main():
	if len(sys.argv) != 2:
		print("Usage: generate.py [input_file]")
		exit()

	data = inputdata()
	data.read_input_file(sys.argv[1])
	main_function(min_atom_in = data.min_atom,
		max_atom_in = data.max_atom,
		atomic_elements_in = data.atomic_elements,
		sg_start_in = data.sg_start,
		sg_end_in = data.sg_end ,
		dimension_in = data.dimension,
		outdir_in = data.outdir,
		prefix_in = data.prefix,
		verbosity_in = data.verbosity,
		calculation_in = data.calculation,
		composition_in = data.composition)

if __name__ == "__main__":
	main()
