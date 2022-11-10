#!/usr/bin/env python3
#
import os
import ase.io as io
from ase.spacegroup import get_spacegroup
import sys
import datetime


def read_composition(directory):
	files=[]
	tempfiles = os.listdir(directory)
	for file in tempfiles:
		files.append(directory +'/'+ file)

	one_element_cnt = 0
	two_element_cnt = 0
	three_element_cnt = 0
	more_element_cnt = 0
	total_comp = 0
	#
	f0 = open("summary.dat", "w")
	f1 = open("elemental.dat", "w")
	f2 = open("binary.dat", "w")
	f3 = open("ternary.dat", "w")
	f4 = open("others.dat", "w")
	#
	for infile in files:
		data_file = open(infile,"r")
		lines = data_file.readlines()
		elements = lines[5].strip().split()
		composition = [eval(i) for i in lines[6].strip().split()]
		#
		structure = io.read(infile)
		#
		spg = get_spacegroup(structure,symprec=1e-5)
		if len(elements) == 1:
			one_element_cnt += 1
			printline1 = directory + "|" + infile + "|" + str(elements) + "|" + str(composition) + "|" + "spg # " + str(spg.no) + '|' + spg.symbol + '|' + str(len(elements)) + '\n'
			f1.write(printline1)
		elif len(elements) == 2:
			two_element_cnt += 1
			printline2 = directory + "|" + infile + "|" + str(elements) + "|" + str(composition) + "|" + "spg # " + str(spg.no) + '|' + spg.symbol + '|' + str(len(elements)) + '\n'
			f2.write(printline2)
		elif len(elements) == 3:
			three_element_cnt += 1
			printline3 = directory + "|" + infile + "|" + str(elements) + "|" + str(composition) + "|" + "spg # " + str(spg.no) + '|' + spg.symbol + '|' + str(len(elements)) + '\n'
			f3.write(printline3)
		elif len(elements) >= 4:
			more_element_cnt += 1
			printline4 = directory + "|" + infile + "|" + str(elements) + "|" + str(composition) + "|" + "spg # " + str(spg.no) + '|' + spg.symbol + '|' + str(len(elements)) + '\n'
			f4.write(printline4)
		#
		# write to file
		#
		
		printline0 = directory + "|" + infile + "|" + str(elements) + "|" + str(composition) + "|" + "spg # " + str(spg.no) + '|' + spg.symbol + '|' + str(len(elements)) + '\n'
		f0.write(printline0)
		
		#print(directory,"|",infile , "|" , elements ,"|" ,composition , "|" , "spg # ",spg.no , '|' , spg.symbol, '|',len(elements))
		#print(spg.symbol,spg.symbol)
		total_comp += 1
	total = one_element_cnt + two_element_cnt + three_element_cnt + more_element_cnt
	#
	f0.close()
	f1.close()
	f2.close()
	f3.close()
	f4.close()
	#
	print(" >>>  Output directory          :",directory)
	print(" >>>  Total # of files          :",len(files))
	print(" >>>  Total Compositions        :",total_comp)
	print(" >>> --------------------------------------------------")
	print(" >>>  Elemental Compositions    : {:10d} ({:2.2f}%) ".format(one_element_cnt,((float(one_element_cnt)*100.0)/float(total))))
	print(" >>>  Binary Compositions       : {:10d} ({:2.2f}%) ".format(two_element_cnt,((float(two_element_cnt)*100.0)/float(total))))
	print(" >>>  Ternary Compositions      : {:10d} ({:2.2f}%) ".format(three_element_cnt,((float(three_element_cnt)*100.0)/float(total))))
	print(" >>>  Other Compositions        : {:10d} ({:2.2f}%) ".format(more_element_cnt,((float(more_element_cnt)*100.0)/float(total))))
	print(" >>> --------------------------------------------------")
	print(" >>>  Sum of above Compositions : {:10d} ({:2.2f}%) ".format(total,((float(total)*100.0)/float(total))))
	print(" >>> --------------------------------------------------")
	print(" >>>  Raw summary file          : summary.dat")
	print(" >>>  Elemental summary file    : elemental.dat")
	print(" >>>  Binary summary file       : binary.dat")
	print(" >>>  Ternary summary file      : ternary.dat")
	print(" >>>  Other summary file        : others.dat")
	print(" >>> --------------------------------------------------")
	print(" >>> Program ended at              :",datetime.datetime.now().strftime("%x %X"))
	print(" >>> ==================================================")

if len(sys.argv) != 2:
	print("Usage: Summary.py [output_directory]")
	exit()
else:
	print(" ")
	print(" >>> ==================================================")
	print(" >>> Summary")
	print(" >>> ==================================================")
	print(" >>> Program Started at            :",datetime.datetime.now().strftime("%x %X"))
	print(" >>> Reading files from directory  :",sys.argv[1])
	print(" >>> --------------------------------------------------")
	read_composition(sys.argv[1])
