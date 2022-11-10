#!/usr/bin/env python3
#
import os
import ase.io as io
from ase.spacegroup import get_spacegroup

def read_composition(directory):
	files=[]
	tempfiles = os.listdir(directory)
	for file in tempfiles:
		files.append(directory +'/'+ file)

	directory
	for infile in files:
		data_file = open(infile,"r")
		lines = data_file.readlines()
		elements = lines[5].strip().split()
		composition = [eval(i) for i in lines[6].strip().split()]
		#
		structure = io.read(infile)
		#
		spg = get_spacegroup(structure,symprec=1e-5)
		print(directory,"|",infile , "|" , elements ,"|" ,composition , "|" , "spg # ",spg.no , '|' , spg.symbol, '|',len(elements))
		#print(spg.symbol,spg.symbol)
read_composition("./output")
