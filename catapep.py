import pdb
import sys
import argparse
import stats
import aljamia
import shutil
import os
import sqlite3
from time import strftime
# *-*-* add further libraries used,
# *-*-* do not forget to include them to klibrate.py when creating the executables

import pprint
pp = pprint.PrettyPrinter(indent=4) # important for looking at lists while pdb-ing

#######################################################

def easterEgg():
	
	print u"""
Diéronles a los dos a probar del vino de una cuba, pidiéndoles su parecer del
estado, cualidad, bondad o malicia del vino. El uno lo probó con la punta de la
lengua, el otro no hizo más de llegarlo a las narices. El primero dijo que
aquel vino sabía a hierro, el segundo dijo que más sabía a cordobán. El dueño
dijo que la cuba estaba limpia, y que el tal vino no tenía adobo alguno por
donde hubiese tomado sabor de hierro ni de cordobán. Con todo eso, los dos
famosos mojones se afirmaron en lo que habían dicho. Anduvo el tiempo, vendióse
el vino, y al limpiar de la cuba hallaron en ella una llave pequeña, pendiente
de una correa de cordobán.

Don Quixote, Part Two, Chapter  XIII."""

#------------------------------------------------------

def getDataFromTXT(fileName,
					iField, #MSFFileCol
					jField = "", #RAWFileCol
					kField = "", #scanNumberCol
					lField = "", #chargeCol
					mField = "", #pepSequenceCol
					nField = "", #XCorrCol
					initialRow = 1,
					filterString = "",
					removeDuplicates = True,
					removeCommas = True):
	
	# adapted from Aljamia v1.04
	
	result = []
	thisHeader = ""
	
	reader = open(fileName, "r")

	currentRowNumber = 1 # one based!
	for myRow in reader:
	
		if currentRowNumber >= initialRow:
			thisRow = myRow.strip().split("\t")
			if removeCommas:
				for i in xrange(len(thisRow)):
					if thisRow[i].endswith('"') and thisRow[i].startswith('"'):
						thisRow[i] = thisRow[i][1:-1]
			
			if currentRowNumber == initialRow:
				# remove brackets if present
				for i in xrange(len(thisRow)):
					if thisRow[i].startswith('[') and thisRow[i].endswith(']'):
						thisRow[i] = thisRow[i][1:-1]
					thisHeader = thisRow
			else:
				# check for fields
				filterOk = aljamia.checkFilter(filterString, isXML = False, currentRow = thisRow, headers = thisHeader)
			
				if filterOk:
					
					dataRow = []
					
					if len(iField) > 0:
						iValue = aljamia.replaceValuesTXT(thisRow, thisHeader, iField)
						dataRow.append(iValue)
					
					if len(jField) > 0:
						jValue = aljamia.replaceValuesTXT(thisRow, thisHeader, jField)
						dataRow.append(jValue)
					
					if len(kField) > 0:
						kValue = aljamia.replaceValuesTXT(thisRow, thisHeader, kField)
						dataRow.append(kValue)
						
					if len(lField) > 0:
						lValue = aljamia.replaceValuesTXT(thisRow, thisHeader, lField)
						dataRow.append(lValue)
						
					if len(mField) > 0:
						mValue = aljamia.replaceValuesTXT(thisRow, thisHeader, mField)
						dataRow.append(mValue)
						
					if len(nField) > 0:
						nValue = aljamia.replaceValuesTXT(thisRow, thisHeader, nField)
						dataRow.append(nValue)
						
					result.append(dataRow)
		
		currentRowNumber += 1
		
	if removeDuplicates:
		result = stats.removeDuplicates(result)
		
	return result

#------------------------------------------------------

def main(options, programName, programVersion):

## REGION: DEFAULT VALUES AND VARIABLE ACQUISITION

	# *-*-* add any default values here, such as default names of files
	# basic default info
	inputFile = ""
	MSFFileCol = ""
	RAWFileCol = ""
	scanNumberCol = ""
	chargeCol = ""
	pepSequenceCol = ""
	XCorrCol = ""
	initialRow = 1
	verbose = False
	QuiXMLResults = False # otherwise, QuiXML will be considered
	changeOriginalMSFFile = False # False = copy MSF to MSF_zeroed, True = change original file
	
	logFile = ""
	analysisName = ""
	analysisFolder = ""
	defaultAnalysisName = programName.lower()
	
	# default extensions
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	
	# default file names
	defaultLogFile = "logFile"
	leadingFile = "" # *-*-* change this by the data file or any important file defining the operation
	
	# basic log file
	logList = [[programName + " " + programVersion], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	# parsing arguments from commandline
	# *-*-* add any arguments used
	options.add_argument("-a", "--analysis", type = str, default = "", required = True, help = "Use a prefix for the output files.")
	options.add_argument("-p", "--place", type = str, default = "", required = True, help = "To use a different common folder for the output files. If this is not provided, the the folder used will be the same as the FASTA file folder.")
	options.add_argument("-L", "--logfile", type = str, default = "", required = False, help = "To use a non-default name for the log file.")
	
	# -d[nombre archivo donde están los xcorr = 0]
	# -M[columna con nombre del msf]
	# -r[rawfilecol]
	# -s[scannumbercol]
	# -q[chargecol]
	# -P[pepsequencecol]
	# -x[xcorrcol]
	# -R[initialrow]
	options.add_argument("-d", "--inputfile", type = str, default = "", required = True, help = "Name of the text file containing the list of PSMs to keep in the MSF.")
	options.add_argument("-M", "--msffile", type = str, default = "", required = True, help = "Name of the MSF file having the PSMs to modify.")
	options.add_argument("-r", "--rawfilecol", type = str, default = "", required = False, help = "Header of the column contaning the name of the RAW files. Default is \"RAWFileName\".")
	options.add_argument("-s", "--scannumbercol", type = str, default = "", required = False, help = "Header of the column containing the scan numbers. Default is \"FirstScan\".")
	options.add_argument("-q", "--chargecol", type = str, default = "", required = False, help = "Header of the column containing the charge. Default is \"Charge\".")
	options.add_argument("-S", "--pepsequencecol", type = str, default = "", required = False, help = "Header of the column containing the identified peptide sequences. Default is \"Sequence\"")
	options.add_argument("-x", "--xcorrcol", type = str, default = "", required = False, help = "Header of the column containing the XCorr. Default is \"XC1D\".")
	options.add_argument("-R", "--initialrow", type = str, default = "1", required = False, help = "The position of the row containing the headers. Default is 1.")
	options.add_argument("-v", "--verbose", action='store_true', help = "Show extra info while operating.")
	options.add_argument("-Q", "--quixml", action='store_true', help = "Use column headers for QuiXML results tab separated table file (otherwise, pRatio results file headers will be used by default).")
	options.add_argument("-O", "--changeoriginalmsf", action='store_true', help = "Do not copy the MSF file to be modified, just remove bad PSMs in the original file.")
	
	# *-*-* add easter egg if wanted
	
	arguments = options.parse_args()
	
	# copying parsed arguments
	# copy any arguments used
	
	verbose = arguments.verbose
	QuiXMLResults = arguments.quixml
	changeOriginalMSFFile = arguments.changeoriginalmsf
	
	if QuiXMLResults:
		RAWFileCol = "RAWFileName"
		scanNumberCol = "FirstScan"
		chargeCol = "Charge"
		pepSequenceCol = "Sequence"
		XCorrCol = "XC1D"
		initialRow = 24
	else: # pRatio results are default
		RAWFileCol = "RAWFile"
		scanNumberCol = "FirstScan"
		chargeCol = "Charge"
		pepSequenceCol = "Sequence"
		XCorrCol = "Xcorr1Search"
		initialRow = 1
		
	
	if len(arguments.analysis) > 0: analysisName = arguments.analysis
	if len(arguments.place) > 0: analysisFolder = arguments.place
	if len(arguments.logfile) > 0: logfile = arguments.logFile

	if len(arguments.inputfile) > 0: inputFile = arguments.inputfile
	if len(arguments.msffile) > 0: MSFFile = arguments.msffile
	if len(arguments.rawfilecol) > 0: RAWFileCol = arguments.rawfilecol
	if len(arguments.scannumbercol) > 0: scanNumberCol = arguments.scannumbercol
	if len(arguments.chargecol) > 0: chargeCol = arguments.chargecol
	if len(arguments.pepsequencecol) > 0: pepSequenceCol = arguments.pepsequencecol
	if len(arguments.xcorrcol) > 0: XCorrCol = arguments.xcorrcol
	if len(arguments.initialrow) > 0: initialRow = int(arguments.initialrow)
	
	RAWFileCol = "[" + RAWFileCol + "]"
	scanNumberCol = "[" + scanNumberCol + "]"
	chargeCol = "[" + chargeCol + "]"
	pepSequenceCol = "[" + pepSequenceCol + "]"
	XCorrCol = "[" + XCorrCol + "]"
	
## END REGION: DEFAULT VALUES AND VARIABLE ACQUISITION
## **********************************************************
## REGION: FILE NAMES SETUP

	# replace leadingfile by the real leading file
	if len(analysisName) == 0:
		if len(leadingFile) > 0:
			analysisName = os.path.splitext(os.path.basename(leadingFile))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	# input

	# *-*-* add input file setup
	
	if len(os.path.dirname(inputFile)) == 0:
		inputFile = os.path.join(analysisFolder, inputFile)
	
	if len(os.path.dirname(MSFFile)) == 0:
		MSFFile = os.path.join(analysisFolder, MSFFile)
	
	if os.path.splitext(MSFFile)[1] != ".msf":
		print
		print "Warning: your MSF file does not seem to be an MSF file."

	if changeOriginalMSFFile:
		newMSFFile = MSFFile
	else:
		newMSFFile = os.path.splitext(MSFFile)[0] + "_zeroed" + os.path.splitext(MSFFile)[1]
	
	# output
	
	# *-*-* add output file setup
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)

	# *-*-* add to the log the input and output filenames
	logList.append([""])
	logList.append(["Output log file: " + logFile])
	logList.append([""])

## END REGION: FILE NAMES SETUP			
## **********************************************************
## REGION: PROGRAM BASIC STRUCTURE

	# *-*-* add basic structure
	
	print
	
	if not changeOriginalMSFFile:
		message = "Creating new file: %s" % newMSFFile
		logList.append([message])
		print message
		shutil.copyfile(MSFFile, newMSFFile)
	
	message = "Loading PSMs to keep from: %s" % inputFile
	logList.append([message])
	print message
	myList = getDataFromTXT(inputFile,
				iField = RAWFileCol,
				jField = scanNumberCol,
				kField = chargeCol,
				lField = pepSequenceCol,
				initialRow = initialRow,
				filterString = XCorrCol  + ">0",
				removeDuplicates = True,
				removeCommas = True)
	
	if len(myList) == 0:
		message = "\nWarning!! No PSMs found in the text file provided,\nDeleting all XCorrs.\n"
	else:
		message = "PSMs found in text file: %i" % len(myList)
	logList.append([message])
	print message
	
	
	compareListIdentified = []
	for element in myList:
		
		myRAWFilePath = element[0]
		myRAWFile = os.path.basename(myRAWFilePath)
		myScanNumber = element[1]
		myCharge = element[2]
		myPepSequence = element[3] # currently unused
		
		compareListIdentified.append([myRAWFile, int(myScanNumber), int(myCharge)])
	
	
	
	connexion = sqlite3.connect(newMSFFile)
	c = connexion.cursor()
	
	existingScanQuery = """select
	p.peptideid,
	fi.filename,
	sh.firstscan,
	sh.lastscan,
	sh.charge,
	p.sequence,
	ps.scorevalue
from
	peptides p,
	peptideScores ps,
	spectrumHeaders sh,
	massPeaks mp,
	fileInfos fi,
	processingNodeScores scoreNames
where
	p.peptideid = ps.peptideid and
	sh.spectrumid = p.spectrumid and
	(fi.fileid = mp.fileid or mp.fileid = -1) and
	mp.masspeakid = sh.masspeakid and
	scoreNames.scoreid = ps.scoreid and
	scoreNames.ScoreName = 'Xcorr'
order by fi.filename desc,
	sh.firstscan asc,
	sh.lastscan asc,
	sh.charge asc,
	ps.scorevalue desc;"""
	
	message = "Searching all PSMs in database..."
	logList.append([message])
	print message
	wholeMSFList = []	
	for psm in c.execute(existingScanQuery):
		wholeMSFList.append(psm)
	
	checked = 0
	changed = 0
	alreadyZero = 0
	
	message = "Zeroing...!"
	logList.append([message])
	message = "Original MSF contains %i PSMs."  % len(wholeMSFList)
	logList.append([message])
	logList.append([""])
	logList.append(["Zeroed\tRAWFileName\tScanNumber\tCharge\tSequence (without PTMs)\tOriginal XCorr"])
	
	print message
	for psm in wholeMSFList:
		checked += 1
		pepId = int(psm[0])
		rawFilePath = str(psm[1])
		rawFile = os.path.basename(rawFilePath)
		firstScan = int(psm[2])
		lastScan = int(psm[3])
		charge = int(psm[4])
		sequence = str(psm[5])
		XCorr = float(psm[6])
		# now check whether this is in the given list. If not, then make XCorr = 0
		
		# compareListIdentified.append([myRAWFile, myScanNumber, myCharge, myPepSequence])
		compareListInMSF = [rawFile, firstScan, charge]
		
		msfScanPresentInList = (compareListInMSF in compareListIdentified)
		
		if XCorr == 0:
			alreadyZero += 1

		if not msfScanPresentInList and XCorr != 0:
			changed += 1
			zeroSettingQuery = """update
	peptideScores
set
	scoreValue = 0
where
	peptideID in (
		select
			p.peptideID
		from
			fileinfos fi,
			massPeaks mp,
			spectrumHeaders sh,
			peptides p
		where
			(fi.fileid = mp.fileid or mp.fileid = -1) and
			mp.masspeakid = sh.masspeakid and
			sh.spectrumid = p.spectrumid and
			sh.firstScan = %i and
			sh.charge = %i and
			fi.fileName like "%%%s"
	) and
	scoreID = (
		select
			scoreId
		from
			processingNodeScores
		where
			scoreName = "XCorr"
			);""" % (firstScan, charge, rawFile)
			# pdb.set_trace()
			c.execute(zeroSettingQuery)
			message = """%i\t%s\t%i\t%i\t%s\t%f""" % (checked, rawFile, firstScan, charge, sequence, XCorr)
			logList.append([message])
			
			if verbose:
				message = """Zeroed (%i/%i):\nraw = "%s"\nscan = %i\ncharge = %i\nsequence = %s\nXCorr = %f\n""" % (checked, len(wholeMSFList), rawFile, firstScan, charge, sequence, XCorr)
				print message
	
	print
	message = "PTMs found: %i,\nPTMs zeroed: %i,\nDifference: %i,\nAlready zero: %i" % (checked, changed, checked - changed, alreadyZero)
	print message
	logList.append([""])
	logList.append([message])
	print
	print "Saving changes..."
	connexion.commit()
	print
	print "Closing connexion..."
	connexion.close()
		
## END REGION: PROGRAM BASIC STRUCTURE
## **********************************************************
## REGION: SAVING FILES
	
	# *-*-* add any files to be saved here
	try:
		# operations here
		logList.append(["Most probably, everything went fine."])
	except getopt.GetoptError:
		logList.append(["Error."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	stats.saveFile(logFile, logList, "LOG FILE")
	
	print "Done!"
	
## END REGION: SAVING FILES

#######################################################

if __name__ == "__main__":
    
	# *-*-* change programStarter by the real name of the program
	programName = "cataPep"
	# *-*-* change programVersion by the program version (yeah, this is tricky)
	programVersion = "v1.03"
	# *-*-* change the programUse for another to be included in the help
	# make sure it makes sense within the sentence "used to ..."
	programUse = "make zero the XCorrs of all the PSMs in an MSF file, excluding those provided in a list."
	
	main(argparse.ArgumentParser(description = u"%s %s is a program made in the Jesus Vazquez Cardiovascular Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to %s." % (programName, programVersion, programUse)), programName, programVersion)
