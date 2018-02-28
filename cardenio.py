import pdb
import sys
import argparse
import stats
import os
import gc
from datetime import datetime
from time import strftime


import pprint
pp = pprint.PrettyPrinter(indent=4) # important for looking at lists while pdb-ing

#######################################################

def easterEgg():
	
	# print u"""***"""
	pass

#------------------------------------------------------

def readTagFile(tagFile, defaultSuffix = "_lowerNormV.xls", defaultFolder = ""):
	
	tagList = []
	fileList = []
	
	lineList = stats.load2stringList(tagFile, removeCommas = True)
	
	for line in lineList[1:]: # [1:] is to remove the header
		newTag = line[0].strip()
		newFile = newTag + defaultSuffix
		
		if len(line) > 1:
			newFile = line[1].strip()
			
		if len(os.path.dirname(newFile)) == 0 and len(defaultFolder) > 0:
			newFile = os.path.join(defaultFolder, newFile)
			
		tagList.append(newTag)
		fileList.append(newFile)
	
	return tagList, fileList

#------------------------------------------------------

def processFiles(tagList, dataFileList, verbose = False, separator = "_", dataFile = "", relsFile = "", relsHeader = "idsup\tidinf", dataHeader = "idinf\tX'inf\tVinf"):

	message = []
	newRelsList = []
	newDataList = []
	newRelsListPart = []
	newDataListPart = []
	
	time1 = 0
	time2 = 0
	
	relsWriter = open(relsFile, "w")
	dataWriter = open(dataFile, "w")
	
	if len(relsHeader) > 0:
		relsWriter.write(relsHeader + "\n")
	if len(dataHeader) > 0:
		dataWriter.write(dataHeader + "\n")
	for i in xrange(len(dataFileList)):
		
		if os.path.isfile(dataFileList[i]):
			# pdb.set_trace()
		
			dataList = stats.loadInputDataFile(dataFileList[i])
			for row in dataList:
				oldId = row[0].strip()
				newId = oldId + separator + tagList[i]
				newRelRow = [oldId, newId]
				newDataRow = [newId, row[1], row[2]]
				
				stats.saveRow(relsWriter, newRelRow)
				stats.saveRow(dataWriter, newDataRow)
				
			now = datetime.now()
			time1 = float(now.strftime("%H")) * 3600 + float(now.strftime("%M")) * 60 + float(now.strftime("%S.%f"))
			
			if verbose:
				if time1 != 0 and time2 != 0:
					print
					print "Total time: %f" % (time1 - time2)
				print ("Reading file #%i: " + dataFileList[i]) % i
				print "dataList: %i" % len(dataList)			
				
			dataList = []
			gc.collect()
			
		else:
			msg = "Error: looks like input file %s does not exist." % dataFileList[i]
			message.append(msg)
			print
			print msg
			print

		gc.collect()
		
		now = datetime.now()
		time2 = float(now.strftime("%H")) * 3600.0 + float(now.strftime("%M")) * 60.0 + float(now.strftime("%S.%f"))
	
	# from v0.03, no duplicate removal is performed
	# if verbose:
		# print "Removing duplicates..."
	# newDataList = stats.removeDuplicates(newDataList)
	# newRelsList = stats.removeDuplicates(newRelsList)
	# if verbose:
		# print "Duplicates removed"
	
	relsWriter.close()
	dataWriter.close()
	
	return message
			
#------------------------------------------------------

def main(options, programName, programVersion):

## REGION: DEFAULT VALUES AND VARIABLE ACQUISITION

	# basic default info
	logFile = ""
	tagFile = ""
	analysisName = ""
	analysisFolder = ""
	defaultAnalysisName = programName.lower()
	verbose = False
	separator = "_"
	
	# default extensions
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	
	# default file names
	defaultLogFile = "logFile"
	defaultNewRelsFile = "newRels"
	defaultNewDataFile = "newData"
	newRelsFile = ""
	newDataFile = ""
	
	# basic log file
	logList = [[programName + " " + programVersion], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	# parsing arguments from commandline
	options.add_argument("-a", "--analysis", type = str, default = "", required = True, help = "Use a prefix for the output files.")
	options.add_argument("-p", "--place", type = str, default = "", required = True, help = "To use a different common folder for the output files. If this is not provided, the the folder used will be the same as the FASTA file folder.")
	options.add_argument("-L", "--logfile", type = str, default = "", required = False, help = "To use a non-default name for the log file.")
	options.add_argument("-t", "--tagfile", type = str, default = "", required = True, help = "The file containing the tags used for the different experiments to be joined.")
	options.add_argument("-d", "--datafile", type = str, default = "", required = False, help = "To use a non-default merged data file name.")
	options.add_argument("-r", "--relfile", type = str, default = "", required = False, help = "To use a non-default merged relations file name.")
	options.add_argument("-s", "--separator", type = str, default = "_", required = False, help = """To use a non-default suffix separator (default is "_").""")
	options.add_argument("-v", "--verbose", action = "store_true", help = "To write down extra information about operations performed.")
	
	# *-*-* add easter egg
	
	arguments = options.parse_args()
	
	# copying parsed arguments
	# copy any arguments used
	if len(arguments.analysis) > 0: analysisName = arguments.analysis
	if len(arguments.place) > 0: analysisFolder = arguments.place
	if len(arguments.logfile) > 0: logFile = arguments.logfile
	if len(arguments.tagfile) > 0: tagFile = arguments.tagfile
	if len(arguments.datafile) > 0: newDataFile = arguments.datafile
	if len(arguments.relfile) > 0: newRelsFile = arguments.relfile
	if len(arguments.separator) > 0: separator = arguments.separator
	verbose = arguments.verbose
	
## END REGION: DEFAULT VALUES AND VARIABLE ACQUISITION
## **********************************************************
## REGION: FILE NAMES SETUP

	if len(analysisName) == 0:
		if len(tagFile) > 0:
			analysisName = os.path.splitext(os.path.basename(tagFile))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	# input

	if len(os.path.dirname(tagFile)) == 0:
		tagFile = os.path.join(analysisFolder, tagFile)
		
	# output
	
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)
		
	if len(newRelsFile) == 0:
		newRelsFile = os.path.join(analysisFolder, analysisName + "_" + defaultNewRelsFile + defaultTextExtension)
	if len(os.path.dirname(newRelsFile)) == 0 and len(os.path.basename(newRelsFile)) > 0:
		newRelsFile = os.path.join(analysisFolder, newRelsFile)
		
	if len(newDataFile) == 0:
		newDataFile = os.path.join(analysisFolder, analysisName + "_" + defaultNewDataFile + defaultTextExtension)
	if len(os.path.dirname(newDataFile)) == 0 and len(os.path.basename(newDataFile)) > 0:
		newDataFile = os.path.join(analysisFolder, newDataFile)

	logList.append([""])
	logList.append(["Input tags file: " + tagFile])
	logList.append(["Output new data file: " + newDataFile])
	logList.append(["Output new relations file: " + newRelsFile])
	logList.append(["Output log file: " + logFile])
	logList.append([""])

## END REGION: FILE NAMES SETUP			
## **********************************************************
## REGION: PROGRAM BASIC STRUCTURE

	tagList, dataFileList = readTagFile(tagFile, defaultFolder = analysisFolder)
	
	processMessage = processFiles(tagList,
									dataFileList,
									verbose = verbose,
									separator = separator,
									dataFile = newDataFile,
									relsFile = newRelsFile)
	
	logList.extend(processMessage)
	
## END REGION: PROGRAM BASIC STRUCTURE
## **********************************************************
## REGION: SAVING FILES
	
	## exceptionally, due to memory errors, the data are read and written in processFiles
	# try:
		# # operations here
		# logList.append(["Saving new data file..."])
		# stats.saveFile(newDataFile, newDataList, "idinf\tX'inf\tVinf")
	# except Exception:
		# logList.append(["Error."])
		# stats.saveFile(logFile, logList, "LOG FILE")
		# sys.exit(2)
	
	# try:
		# # operations here
		# logList.append(["Saving new relations file..."])
		# stats.saveFile(newRelsFile, newRelsList, "idsup\tidinf")
	# except Exception:
		# stats.saveFile(logFile, logList, "LOG FILE")
		# logList.append(["Error."])
		# sys.exit(2)
	
	try:
		# operations here
		logList.append(["Looks like everything went fine."])
	except Exception:
		logList.append(["Error."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	stats.saveFile(logFile, logList, "LOG FILE")
	
## END REGION: SAVING FILES

#######################################################

if __name__ == "__main__":
    
	programName = "Cardenio"
	programVersion = "v0.03"
	# *** improve
	programUse = "generate joined integration data and relations files from different experiments."
	
	main(argparse.ArgumentParser(description = u"%s %s is a program made in the Jesus Vazquez Cardiovascular Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to %s." % (programName, programVersion, programUse)), programName, programVersion)
