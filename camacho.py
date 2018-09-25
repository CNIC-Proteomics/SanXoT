import pdb
import sys
import argparse
import stats
import os
import gc
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4) # important for looking at lists while pdb-ing

#######################################################

def easterEgg():
	
	print u"""
Estando, pues, asidos de las manos Basilio y Quiteria, el cura, tierno y
lloroso, los echó la bendición y pidió al cielo diese buen poso al alma del
nuevo desposado; el cual, así como recibió la bendición, con presta ligereza se
levantó en pie, y con no vista desenvoltura se sacó el estoque, a quien servía
y de vaina su cuerpo.
Quedaron todos los circunstantes admirados, y algunos dellos, más simples
que curiosos, en altas voces, comenzaron a decir:
-¡Milagro, milagro!
Pero Basilio replicó:
-¡No "milagro, milagro", sino industria, industria!

Don Quixote, Part Two, Chapter XXI."""

#------------------------------------------------------

def getRelations(bigTable, qCol, cCol, qSeparator = ",", cSeparator = ",", cPrefix = "", removeHeader = True, FASTAHeaders = []):
	
	relations = []
	if removeHeader: bigTable = bigTable[1:]
	
	for row in bigTable:

		if len(row) >= qCol and len(row) >= cCol:
		
			qString = row[qCol - 1]
			qList = qString.split(qSeparator)
			
			cString = row[cCol - 1]
			cList = cString.split(cSeparator)
			
			for c in cList:
				cs = c.strip()
				if len(cs) > 0:
					for q in qList:
						qs = q.strip()
						if len(qs) > 0:
							relations.append([(cPrefix + cs), qs])
	
	newRelations = replaceRelations(relations, FASTAHeaders)
	
	return newRelations

#------------------------------------------------------

def replaceRelations(relations, FASTAHeaders = []):
	
	newRelations = []
	relationsSorted = stats.sortByIndex(relations, 1)
	FASTAHeadersSorted = stats.sortByIndex(FASTAHeaders, 0)
	
	
	if len(FASTAHeadersSorted) > 0:
		for relation in relationsSorted:
			element = relation[1]
			searchResult = stats.filterByElement(FASTAHeadersSorted, element, index = 0, sort = False)
			if len(searchResult) > 0:
				newRelations.append([relation[0], searchResult[0][1]])
	else:
		return relationsSorted
	
	return newRelations

#------------------------------------------------------

def getFASTAHeaders(FASTAFile):

	FASTAHeaders = []
	headerRelations = []
	if len(FASTAFile) > 0:
		wholeFASTA = stats.load2stringList(FASTAFile, removeCommas = False)
	else:
		return []

	# keep only headers
	for line in wholeFASTA:
		if line[0][0] == ">": FASTAHeaders.append(line[0])
		
	for header in FASTAHeaders:
		if len(header) > 0:
			headerRelations.append([header.split("|")[1], header])
		
	return headerRelations

#------------------------------------------------------

def main(options, programName, programVersion):

## REGION: DEFAULT VALUES AND VARIABLE ACQUISITION

	# basic default info
	logFile = ""
	analysisName = ""
	analysisFolder = ""
	defaultAnalysisName = programName.lower()
	
	relFile = ""
	DBFile = ""
	FASTAFile = ""
	previousFile = ""
	accNumCol = 1
	catCol = 2
	catPrefix = ""
	header = "idsup\tidinf"
	
	previousList = []
	
	# default extensions
	defaultTableExtension = ".tsv"
	defaultTextExtension = ".txt"
	
	# default file names	
	defaultLogFile = "logFile"
	defaultRelFile = "rels"
	
	# basic log file
	logList = [[programName + " " + programVersion], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	# parsing arguments from commandline
	options.add_argument("-a", "--analysis", type = str, default = "", required = True, help = "Use a prefix for the output files.")
	options.add_argument("-p", "--place", type = str, default = "", required = True, help = "To use a different common folder for the output files. If this is not provided, the the folder used will be the same as the FASTA file folder.")
	options.add_argument("-L", "--logfile", type = str, default = "", required = False, help = "To use a non-default name for the log file.")
	options.add_argument("-d", "--dbfile", type = str, default = "", required = True, help = "The input file containing accession numbers and categories.")
	options.add_argument("-x", "--previousfile", type = str, default = "", required = False, help = "An optional relation file to which concatenate resulting relations (if omitted, a new file will be produced).")
	options.add_argument("-q", "--accnumcol", type = str, default = "1", required = False, help = "Column where accession numbers of genes/proteins are. First column is 1. Default is 1.")
	options.add_argument("-c", "--categorycol", type = str, default = "2", required = False, help = "Column where categories are. First column is 1. Default is 2.")
	options.add_argument("-f", "--prefix", type = str, default = "", required = False, help = "Prefix to add to all categories found in this parsing (such as \"GO-full_\", \"Panther_\", or \"KEGG=2017-01-10_\".")
	options.add_argument("--fasta", type = str, default = "", required = False, help = "FASTA file contaning the identifiers we want to replace by FASTA headers in the final file. Note that identifiers not appearing in this FASTA file will be removed from the final list.")
	# add string with category separator
	# add string with accNum separator
	
	
	# *-*-* add easter egg if wanted
	
	arguments = options.parse_args()
	
	# copying parsed arguments
	# copy any arguments used
	if len(arguments.analysis) > 0: analysisName = arguments.analysis
	if len(arguments.place) > 0: analysisFolder = arguments.place
	if len(arguments.logfile) > 0: logFile = arguments.logfile
	if len(arguments.dbfile) > 0: DBFile = arguments.dbfile
	if len(arguments.fasta) > 0: FASTAFile = arguments.fasta
	if len(arguments.previousfile) > 0: previousFile = arguments.previousfile
	if len(arguments.accnumcol) > 0: accNumCol = int(arguments.accnumcol)
	if len(arguments.categorycol) > 0: catCol = int(arguments.categorycol)
	if len(arguments.prefix) > 0: catPrefix = arguments.prefix
	
## END REGION: DEFAULT VALUES AND VARIABLE ACQUISITION
## **********************************************************
## REGION: FILE NAMES SETUP

	if len(analysisName) == 0:
		if len(DBFile) > 0:
			analysisName = os.path.splitext(os.path.basename(DBFile))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	# input

	if len(os.path.dirname(DBFile)) == 0:
		DBFile = os.path.join(analysisFolder, DBFile)
	
	if len(previousFile) > 0:
		if len(os.path.dirname(previousFile)) == 0:
			previousFile = os.path.join(analysisFolder, previousFile)
	
	if len(FASTAFile) > 0:
		if len(os.path.dirname(FASTAFile)) == 0:
			FASTAFile = os.path.join(analysisFolder, FASTAFile)
		
	# output
	
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)
		
	if len(relFile) == 0:
		relFile = os.path.join(analysisFolder, analysisName + "_" + defaultRelFile + defaultTableExtension)
	if len(os.path.dirname(relFile)) == 0 and len(os.path.basename(relFile)) > 0:
		relFile = os.path.join(analysisFolder, relFile)

	logList.append([""])
	logList.append(["Input table with categories and proteins: " + DBFile])
	if len(previousFile) > 0:
		logList.append(["Previous file to which new qc relations are added: " + previousFile])
	if len(FASTAFile) > 0:
		logList.append(["FASTA file to replace identifiers for FASTA headers: " + FASTAFile])
	logList.append(["Category column: %i, protein column: %i" % (catCol, accNumCol)])
	logList.append(["Prefix added to categories: " + catPrefix])
	logList.append(["Output relations file: " + relFile])
	logList.append(["Output log file: " + logFile])
	logList.append([""])

## END REGION: FILE NAMES SETUP			
## **********************************************************
## REGION: PROGRAM BASIC STRUCTURE

	if len(previousFile) > 0: #otherwise, previousList = []
		previousList = stats.load2stringList(previousFile, removeCommas = True)
		header = ""

	AccNum2FASTAHeader = getFASTAHeaders(FASTAFile)
	gc.collect()
	
	DBList = stats.load2stringList(DBFile, removeCommas = True)
	newRelations = getRelations(bigTable = DBList,
							qCol = accNumCol,
							cCol = catCol,
							cPrefix = catPrefix,
							FASTAHeaders = AccNum2FASTAHeader)
	newRelationsSorted = stats.sortByIndex(newRelations, 0)
	relationList = previousList + newRelationsSorted
	
	gc.collect()
							

## END REGION: PROGRAM BASIC STRUCTURE
## **********************************************************
## REGION: SAVING FILES
	
	try:
		stats.saveFile(relFile, relationList, header)
		
		logList.append(["Everything went fine."])
		stats.saveFile(logFile, logList, "LOG FILE")
	except getopt.GetoptError:
		logList.append(["Error."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
## END REGION: SAVING FILES

#######################################################

if __name__ == "__main__":
    
	programName = "Camacho"
	programVersion = "v0.03"

	# make sure it makes sense within the sentence "used to ..."
	programUse = "take a table including proteins and categories (mainly from DAVID), and organise them as relations file ready to be used in the Systems Biology Triangle"
	
	main(argparse.ArgumentParser(description = u"%s %s is a program made in the Jesus Vazquez Cardiovascular Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to %s." % (programName, programVersion, programUse)), programName, programVersion)
