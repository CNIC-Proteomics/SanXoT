__author__ = 'nbagwan'
import pprint
import pdb
import math
import sys
import os
from optparse import OptionParser


usage = "usage: %prog -m XMLfile -r RelationsFile -o outputName"

parser = OptionParser(usage=usage)

parser.add_option("-m", "--modSymbolFile", action="store", type="string", dest="Dir", help="Enter the xml file")
parser.add_option("-r", "--relsfile", action="store", type="string", dest="FileName", help="Enter relation file")
parser.add_option("-o", "--Outfile", action= "store", type="string", dest="OutDir", help="enter the output file")


(options, args) = parser.parse_args()

if options.Dir: #### belog to parser(dest)
	Dir = options.Dir
else:
	parser.error("enter xml file name -m")

if options.FileName:
	FileName = options.FileName
else:
	parser.error("enter the file name -r")

if options.OutDir:
	OutDir=options.OutDir
else:
	parser.error("enter the output folder -o")





""" To make PTM relation file for use in sanxotguass for sigmoids
"""
def relation_seprator(SymbolFile, RelationFile,outputfile):
	

## creating list of all symbols..
	def ExtractSymbolFromXml(XmlFile):
		file1 =open(XmlFile)
		dic={}
		symbol_list=[]
		for line in file1:
			if line!="\n":
				splits=line.split(">")
				if splits[0].strip()=="<symbol":
					symbol_list.append(splits[1].split("<")[0])
		return symbol_list

## check if sequence have any symbol present or not
	def checksymbolPresence(sequence,list1):
		for i in list1:
			if i in sequence:
				return False
		return True
#####   main ######
	import pdb
	symbols=ExtractSymbolFromXml(SymbolFile)
	headers=["modifications","peptide","\n"]
	out = open(outputfile, "w")
	out.write("\t".join(headers))
	ln1=[]
	ln2=[]
	ln3=[]
	for rels in open(RelationFile):
		if rels!="\n":
			splits=rels.split("\t")
			pep_seq= splits[1].strip()
			nm="NonMod"
			for i in pep_seq:
				if not (i.isalpha()):
					if i in symbols:
						ln2=[i,"\t",pep_seq,"\n"]
						out.writelines(ln2)
			if checksymbolPresence(pep_seq,symbols):	
				ln1=[nm,"\t",pep_seq,"\n"]
				out.writelines(ln1)
				

	out.close()
if __name__ == '__main__':

	relation_seprator(SymbolFile=Dir,RelationFile=FileName,outputfile=OutDir)
####----------

