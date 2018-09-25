import pdb
import math
import sys
import getopt
import stats
import sanxot
import os
from time import strftime

import pprint

def X_VpCollector(dataFiles,relationsFile):
	#w=open("m_peptideMwoQ2proteins_relations.txt","w")
	mod=[]
	dic={}
	for line1 in open(dataFiles):
	    if line1!="\n":
	        splits1=line1.split("\t")
	        seqData=splits1[0].strip()
		#pdb.set_trace()
	        xp=splits1[1].strip()
	        vp=splits1[2].strip()
	        if seqData not in dic:
	            dic[seqData]=[xp,vp]

	#file1=open("R_peptide2proteins_relations_peptideMwoQ2proteins_relations.txt")
	for line in open(relationsFile):
	    if line!="\n":
	        splits=line.split("\t")
	        seq=splits[1].strip()
	        # pdb.set_trace()
	        for s in dic:
	            if seq ==s:
	                x=dic[seq][0]
	                v=dic[seq][1]
	                mod.append([str(seq), x,v])
	
	return mod

##########
def printHelp(version=None, advanced=False):
	print """%s
As the name suggest, this programme collects the Xp Vp values from data file
for any given relation files. 
For example:
   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the data
                       file.
   -o, --outputfile=string
                       The new outstasts file containing ALL peptides.
   -r, --relfile=string
                       The SanXoT relations file for peptides to proteins.
   -d, --dataFile=string
                       The SanXoT logFile containing the variance of an
                       integration from NONMODIFIED peptide to PROTEIN.           
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the input folder.
""" % version
#-------------------------------------------------------
def main(argv):
	version = "v0.01"
	analysisName = ""
	analysisFolder = ""
	relationsFile = ""
	dataFiles = ""
	outputFile = ""
	defaultOutput = "OutStats"
	defaultOutputInfo = "infoFile"
	defaultRelationsFile = "rels"
	defaultDataFiles = "datafile"
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	defaultAnalysisName = "xpvpAnalysis"
	infoFile = ""
	logList = [["XVpCollector " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]
	try:
		opts, args = getopt.getopt(argv, "a:p:r:o:d:h",
                                   ["analysis=", "folder=", "relfile=", "outputfile=", "dataFile=", "help"])
	except getopt.GetoptError:
		logList.append(["Error while getting parameters."])
		stats.saveFile(infoFile, logList, "INFO FILE")
		sys.exit(2)
	if len(opts) == 0:
		printHelp(version)
		sys.exit()
	for opt, arg in opts:
		if opt in ("-a", "--analysis"):
			analysisName = arg
		if opt in ("-p", "--place", "--folder"):
			analysisFolder = arg
		if opt in ("-r", "--relfile"):
			relationsFile = arg
		if opt in ("-o", "--outputfile"):
			outputFile = arg
		if opt in ("-d", "--dataFile"):
			dataFiles = arg
		elif opt in ("-h", "--help"):
			printHelp(version)

# REGION: FILE NAMES SETUP
	if len(analysisName) == 0:
		if len(dataFiles) > 0:
			analysisName = os.path.splitext(os.path.basename(dataFiles))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart

	if len(dataFiles) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(dataFiles)) > 0:
			analysisFolder = os.path.dirname(dataFiles)


    # input
	if len(dataFiles) == 0:
		dataFiles = os.path.join(analysisFolder, analysisName + "_" + defaultDataFiles + defaultTableExtension)

	if len(os.path.dirname(dataFiles)) == 0 and len(analysisFolder) > 0:
		dataFiles = os.path.join(analysisFolder, dataFiles)

	if len(relationsFile) == 0:
		relationsFile = os.path.join(analysisFolder, analysisName + "_" + defaultRelationsFile + defaultTableExtension)

	if len(os.path.dirname(relationsFile)) == 0 and len(analysisFolder) > 0:
		relationsFile = os.path.join(analysisFolder, relationsFile)

	# output
	if len(outputFile) == 0:
		outputFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutput + defaultTableExtension)
	else:
		if len(os.path.dirname(outputFile)) == 0:
			outputFile = os.path.join(analysisFolder, outputFile)

	if len(infoFile) == 0:
		infoFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputInfo + defaultTableExtension)


	logList.append(["Input dataFiles " + str(dataFiles)])	
	logList.append(["Input relations file: " + relationsFile])
	logList.append(["Input dataFile: " + dataFiles])
	logList.append(["Output stats file: " + outputFile])
	logList.append(["Output info file: " + infoFile])

	outputList = X_VpCollector(dataFiles=dataFiles,relationsFile=relationsFile)
	header = "idsup\tX'sup,\t,V'sup" #"Sequence\tFASTAProteinDescription\tXp\tVp\tcount\tZp" "idsup\tX'sup,\t,V'sup"
    #######("Fix the header for Xp and Vp")
	stats.saveFile(outputFile, outputList, header)

	if len(infoFile) > 0:
		stats.saveFile(infoFile, logList, "INFO FILE")


if __name__ == "__main__":
	main(sys.argv[1:])



        


	

