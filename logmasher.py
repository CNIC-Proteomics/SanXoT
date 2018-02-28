import pdb
import sys
import argparse
import stats
import os
from time import strftime
import glob
import re

import pprint
pp = pprint.PrettyPrinter(indent=4) # important for looking at lists while pdb-ing

#######################################################

def getDataFromFolder(directoryUsed, recursive = False):
	
	listOfFiles = glob.glob(directoryUsed)
	
	resultListPartial = []
	# pdb.set_trace()
	for element in listOfFiles:
		if os.path.isdir(element) and recursive:
			resultListPartial.extend(getDataFromFolder(element + "\\*", recursive = recursive))
		else:
			if len(element) > 13:
				if element[-13:] == "_infoFile.txt":
					fileContents = stats.load2stringList(element)
					
					if fileContents[0][0] == "INFO FILE" and (bool(re.match("SanXoT v[0-9]{1,2}.[0-9]{2}", fileContents[1][0]))):
						prefix = os.path.basename(element)[:-13]
						variance, varianceOk = stats.extractVarianceFromVarFile(element, verbose = False, defaultSeed = float("nan"))
						path = element
						if varianceOk:
							resultRow = [prefix, variance, path]
						else:
							resultRow = [prefix, "not found", path]
						resultListPartial.append(resultRow)
					
	return resultListPartial

#------------------------------------------------------

def main(options, programName, programVersion):

## REGION: DEFAULT VALUES AND VARIABLE ACQUISITION

	# basic default info
	logFile = ""
	analysisName = ""
	analysisFolder = ""
	defaultAnalysisName = programName.lower()
	directoryUsed = ""
	resultList = []
	recursiveFolders = False
	
	# default extensions
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	
	# default file names
	outputFile = ""
	defaultOutputFile = "output"
	defaultLogFile = "logFile"
	
	# basic log file
	logList = [[programName + " " + programVersion], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	# parsing arguments from commandline
	options.add_argument("-a", "--analysis", type = str, default = "", required = True, help = "Use a prefix for the output files.")
	options.add_argument("-p", "--place", type = str, default = "", required = True, help = "To use a different common folder for the output files. If this is not provided, the the folder used will be the same as the FASTA file folder.")
	options.add_argument("-L", "--logfile", type = str, default = "", required = False, help = "To use a non-default name for the log file.")
	options.add_argument("-d", "--directory", type = str, default = "", required = True, help = "Path where the log files are. It accepts common path wildcards, such as '*' and '?'.")
	# options.add_argument("--checkallfiles", type = str, default = "", required = False, help = "To check the first row of all files, not just those ending in infoFile.txt; important when non-standard log files are present")
	options.add_argument("-r", "--recursive", action = "store_true", required = False, help = "If only the path is given, it searches all log files in the given directory _and_ all its subdirectories.")
	
	arguments = options.parse_args()
	
	# copying parsed arguments
	# copy any arguments used
	if len(arguments.analysis) > 0: analysisName = arguments.analysis
	if len(arguments.place) > 0: analysisFolder = arguments.place
	if len(arguments.logfile) > 0: logFile = arguments.logfile
	if len(arguments.directory) > 0: directoryUsed = arguments.directory
	recursiveFolders = arguments.recursive
	
## END REGION: DEFAULT VALUES AND VARIABLE ACQUISITION
## **********************************************************
## REGION: FILE NAMES SETUP

	if len(analysisName) == 0:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	# input

	if directoryUsed[-1] == "\\": directoryUsed = directoryUsed[:-1]
	# if os.path.isdir(directoryUsed): directoryUsed += "\\*"
		
	# output
	
	if len(outputFile) == 0:
		outputFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputFile + defaultTableExtension)
	if len(os.path.dirname(outputFile)) == 0 and len(os.path.basename(outputFile)) > 0:
		outputFile = os.path.join(analysisFolder, outputFile)
		
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)

	logList.append([""])
	logList.append(["Output log file: " + logFile])
	logList.append(["Search string: " + directoryUsed])
	logList.append([""])

## END REGION: FILE NAMES SETUP			
## **********************************************************
## REGION: PROGRAM BASIC STRUCTURE

	resultListPartial = getDataFromFolder(directoryUsed, recursiveFolders)
	resultList.extend(resultListPartial)

	message = "%i variances extracted from info files." % len(resultList)
	print
	print message
	print
	logList.append([message])
	
## END REGION: PROGRAM BASIC STRUCTURE
## **********************************************************
## REGION: SAVING FILES
	
	try:
		stats.saveFile(outputFile, resultList, "prefix\tvariance\tpath")
		logList.append(["Everything went fine."])
	except getopt.GetoptError:
		logList.append(["Error."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	stats.saveFile(logFile, logList, "LOG FILE")
	
## END REGION: SAVING FILES

#######################################################

if __name__ == "__main__":
    
	programName = "LogMasher"
	programVersion = "v0.02"
	programUse = "collect general information from a bunch of log files generated by SanXoT for a given path"
	# programUse = "collect general information from a bunch of log files generated by SanXoT or SanXoTSieve for a given path"
	
	main(argparse.ArgumentParser(description = u"%s %s is a program made in the Jesus Vazquez Cardiovascular Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to %s." % (programName, programVersion, programUse)), programName, programVersion)
