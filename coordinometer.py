import pdb
import sys
import argparse
import stats
import os
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4) # important for looking at lists while pdb-ing

#######################################################

#------------------------------------------------------

def getRels(qcInputFile = "", listChangingCats = [], qcInputNoOutsFile = "", modeSanXoTSieve = "newWay", caseSensitive = True, outlierTag = "out"):

	qcInputRawList = []
	qcInput = []
	qcInputNoOutsRawList = []
	qcInputNoOuts = []
	numRelsChangingCats = 0
	numOutliersChangingCats = 0
	numOutliersNonChangingCats = 0
	
	# lists of lists for filterByElement, needed to speed it up
	qcInputSortedList = []
	qcInputNoOutsSortedList = []
	listChangingCatsList = []
	listChangingCatsSortedList = []

	# when no qcInputFileNoOuts file is present, the newWay option is used
	# this has already been sorted previously, but just in case...
	if len(qcInputNoOutsFile) == 0: modeSanXoTSieve = "newWay"

	qcInputRawList = stats.loadStatsDataFile(qcInputFile, FDRasText = True, ZasText = True, includeTags = True)
	
	# next line is needed to nest list within list and make it work with the filterByElement method
	for cat in listChangingCats:
		if caseSensitive:
			listChangingCatsList.append([cat])
		else:
			listChangingCatsList.append([cat.lower()])
			
	# important NOT to sort listChangingCats, as this is not a list of lists and
	# sorting would only affect the first character instead of the first string
	listChangingCatsSortedList = stats.sortByIndex(listChangingCatsList, 0)	
	
	# get list of rels
	# next line is needed to nest list within list and make it work with the filterByElement method
	for qc in qcInputRawList:
		if caseSensitive:
			qcInput.append([[qc[0], qc[3], qc[9]]])
		else:
			qcInput.append([[qc[0].lower(), qc[3].lower(), qc[9]]])
			
	qcInputSortedList = stats.sortByIndex(qcInput, 0)
	
	if modeSanXoTSieve == "newWay":

		for qc in qcInputSortedList:
		
			if len(stats.filterByElement(listChangingCatsSortedList, qc[0][0], sort = False)) > 0:
				# get list of rels pointing to changing cats
				# get outlier rels
				numRelsChangingCats += 1
				if stats.tagIsPresent(qc[0][2], outlierTag):
					numOutliersChangingCats += 1
					
			else:
				# relations pointing to non changing cats
				if stats.tagIsPresent(qc[0][2], outlierTag):
					# outliers pointing to non changing cats
					numOutliersNonChangingCats += 1

	if modeSanXoTSieve == "oldWay":
	
		# quitar si sale bien sacándolo fuera
		
		# # next line is needed to nest list within list and make it work with the filterByElement method
		# for qc in qcInputRawList:
			# # if modeSanXoTSieve == "oldWay" and len(qc)
			# if caseSensitive:
				# qcInput.append([[qc[0], qc[3]]])
			# else:
				# qcInput.append([[qc[0].lower(), qc[3].lower()]])
				
		# qcInputSortedList = stats.sortByIndex(qcInput, 0)
		
		if len(qcInputNoOutsFile) > 0:
			qcInputNoOutsRawList = stats.loadStatsDataFile(qcInputNoOutsFile, FDRasText = True, ZasText = True, includeTags = False)
			
			# next line is needed to nest list within list and make it work with the filterByElement method
			for qcno in qcInputNoOutsRawList:
				if caseSensitive:
					qcInputNoOuts.append([[qcno[0], qcno[3]]])
				else:
					qcInputNoOuts.append([[qcno[0].lower(), qcno[3].lower()]])
				
			qcInputNoOutsSortedList = stats.sortByIndex(qcInputNoOuts, 0)
			

		
		print
		print "calculating with %i relations and %i changing categories..." % (len(qcInputSortedList), len(listChangingCats))
		
		for qc in qcInputSortedList:
			
			# better do not use something like "if x in list..." because that is quite slow
			if len(stats.filterByElement(listChangingCatsSortedList, qc[0][0], sort = False)) > 0:
				# is the category qc[0] in listChangingCatsSorted? If no --> 0
				# this relation points to a changing category
				numRelsChangingCats += 1
				if len(stats.filterByElement(qcInputNoOutsSortedList, qc[0][0:2], sort = False)) == 0:
					# is the relation qc in qcInputNoOuts? If no --> 0
					# this relation is an outlier in a changing category
					# the [0:2] part is to remove the space for tags
					numOutliersChangingCats += 1
			else:
				# this relation points to a non-changing category
				if len(stats.filterByElement(qcInputNoOutsSortedList, qc[0][0:2], sort = False)) == 0:
					# is the relation qc in qcInputNoOuts? If no --> 0
					# this relation is an outlier in a non-changing category
					numOutliersNonChangingCats += 1
					
	return numRelsChangingCats, numOutliersChangingCats, numOutliersNonChangingCats

#------------------------------------------------------
	
def getListChangingCats(caInputFile = "", caFDR = 0.05):

	caOutStats = []
	caOutStatsAll = stats.loadStatsDataFile(caInputFile, FDRasText = False, ZasText = True, includeTags = False)
	
	for row in caOutStatsAll:
		if row[8] < caFDR:
			caOutStats.append(row[3])
	
	return caOutStats

#------------------------------------------------------

def main(options, programName, programVersion):

## REGION: DEFAULT VALUES AND VARIABLE ACQUISITION

	# basic default info
	logFile = ""
	analysisName = ""
	analysisFolder = ""
	defaultAnalysisName = programName.lower()
	caFDR = 0.05
	modeSanXoTSieve = "newWay" # alternatively, "oldWay"
	coordination = 0
	caseSensitive = True
	
	# default extensions
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	
	# default file names
	defaultLogFile = "logFile"
	qcInputFile = "qcInput"
	qcInputFileNoOuts = ""
	caInputFile = "caInput"
	
	# basic log file
	logList = [[programName + " " + programVersion], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	# parsing arguments from commandline
	options.add_argument("-a", "--analysis", type = str, default = "", required = False, help = "Use a prefix for the output files.")
	options.add_argument("-p", "--place", type = str, default = "", required = False, help = "To use a different common folder for the output files. If this is not provided, the the folder used will be the same as the FASTA file folder.")
	options.add_argument("-L", "--logfile", type = str, default = "", required = False, help = "To use a non-default name for the log file.")
	options.add_argument("-q", "--qcinput", type = str, default = "", required = True, help = "Input outstats file with the q2c integration, including outliers. It must include outliers tagged in new SanXoTSieve files, or, alternatively, it must add the corresponding file with no outliers (see -n argument) for SanXoTSieve in oldWay mode.")
	options.add_argument("-n", "--qcinputnoouts", type = str, default = "", required = False, help = "Input outstats file with the q2c integration, NOT including outliers (using this parameter automatically implies the oldWay option has been used in SanXoTSieve, i.e. removing outliers from the relations file, instead of just tagging them).")
	options.add_argument("-c", "--cainput", type = str, default = "", required = True, help = "Input outstats file with the c2a integration, defining in the FDR column which cateogries are considered to be changing.")
	options.add_argument("--cafdr", type = str, default = "0.05", required = False, help = "To consider a non-default FDR value for changing categories in the c2a integration (default is 0.05).")
	options.add_argument("--caseinsensitive", action='store_true', help = "Consider case insensitive categories and protein identifiers (by default, they are case sensitive).")
		
	arguments = options.parse_args()
	
	# copying parsed arguments
	# copy any arguments used
	if len(arguments.analysis) > 0: analysisName = arguments.analysis
	if len(arguments.place) > 0: analysisFolder = arguments.place
	if len(arguments.logfile) > 0: logFile = arguments.logfile
	if len(arguments.qcinput) > 0: qcInputFile = arguments.qcinput
	if len(arguments.qcinputnoouts) > 0:
		qcInputFileNoOuts = arguments.qcinputnoouts
		modeSanXoTSieve = "oldWay"
	if len(arguments.cainput) > 0: caInputFile = arguments.cainput
	if len(str(arguments.cafdr)) > 0:
		try:
			caFDR = float(arguments.cafdr)
		except:
			message = "Warning: FDR for categories changing could not be parsed, %f will be used instead." % caFDR
			logList.append([""])
			logList.append([message])
			logList.append([""])
			print ""
			print message
			print ""
	caseSensitive = not arguments.caseinsensitive
	
## END REGION: DEFAULT VALUES AND VARIABLE ACQUISITION
## **********************************************************
## REGION: FILE NAMES SETUP

	if len(analysisName) == 0:
		if len(qcInputFile) > 0:
			analysisName = os.path.splitext(os.path.basename(qcInputFile))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
	
	if len(analysisFolder) == 0:
		analysisFolder = os.getcwd()
	
	# input

	if len(os.path.dirname(qcInputFile)) == 0:
		qcInputFile = os.path.join(analysisFolder, qcInputFile)
	
	if len(os.path.dirname(qcInputFileNoOuts)) == 0 and modeSanXoTSieve == "oldWay":
		qcInputFileNoOuts = os.path.join(analysisFolder, qcInputFileNoOuts)
		
	if len(os.path.dirname(caInputFile)) == 0:
		caInputFile = os.path.join(analysisFolder, caInputFile)
	
	# output
	
	# the only output is the logFile, which includes a last line with the coordination
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)

	logList.append([""])
	logList.append(["Input protein-to-category outstats file: " + qcInputFile])
	logList.append(["Input category-to-all outstats file: " + caInputFile])
	if len(qcInputFileNoOuts) > 0: logList.append(["Input protein-to-category outstats with NO outliers: " + qcInputFileNoOuts])
	logList.append(["Output log file: " + logFile])
	logList.append(["category-to-all FDR used: %f" % caFDR])
	logList.append(["SanXoTSieve mode: " + modeSanXoTSieve])
	logList.append([""])

## END REGION: FILE NAMES SETUP			
## **********************************************************
## REGION: PROGRAM BASIC STRUCTURE

	listChangingCats = getListChangingCats(caInputFile, caFDR)
	numRelsChangingCats, numOutliersChangingCats, numOutliersNonChangingCats = getRels(qcInputFile, listChangingCats, qcInputFileNoOuts, modeSanXoTSieve, caseSensitive)
	
	# explanation
	#	coord = (C - B)/(C + A)
	#	where
	#		C = numRelsChangingCats = qc-relations pointing to categories changing in ca
	#		B = numOutliersChangingCats = outlier qc-relations in categories changing in ca
	#		A = numOutliersNonChangingCats = outlier qc-relations in categories not changing in ca
	#		hence, B + A = outlier qc-relations in any category
	
	coordination = (float(numRelsChangingCats) - float(numOutliersChangingCats)) / (float(numRelsChangingCats) + float(numOutliersNonChangingCats))

## END REGION: PROGRAM BASIC STRUCTURE
## **********************************************************
## REGION: SAVING FILES
	
	try:
		message = "Degree of coordination: %f" % coordination
		logList.append(["Total number of changing categories: %i" % len(listChangingCats)])
		logList.append(["Total number of relations pointing to changing categories: %i" % numRelsChangingCats])
		logList.append(["Total number of outlier relations pointing to changing categories: %i" % numOutliersChangingCats])
		logList.append(["Total number of outlier relations pointing to non-changing categories: %i" % numOutliersNonChangingCats])
		logList.append([message])
		print ""
		print "Find more details in the log file, at: %s" % logFile
		print ""
		print message
		print ""
		
	except getopt.GetoptError:
		logList.append(["Error."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	stats.saveFile(logFile, logList, "LOG FILE")
	
## END REGION: SAVING FILES

#######################################################

if __name__ == "__main__":
    
	programName = "Coordinometer"
	programVersion = "v1.01"
	programUse = """calculate the degree of coordination for a given q>c and c>a integration. Input files are the outstats files (part of the output of these integrations), and the output is the coordination calculated from them (presented in both the command prompt and within the logFile). If the -n argument is omitted, the newWay mode for SanXoTSieve (relations file with outliers tagged as "out") will be considered; conversely, if the -n argument is used, the oldWay mode for SanXoTSieve (no tags in the resulting relations file, outliers are just removed) will be assumed"""
	
	main(argparse.ArgumentParser(description = u"%s %s is a program made in the Jesus Vazquez Cardiovascular Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to %s." % (programName, programVersion, programUse)), programName, programVersion)
