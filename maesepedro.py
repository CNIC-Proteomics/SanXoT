import pdb
import sys
import getopt
import stats
import os
import subprocess
from scipy.stats import norm
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4)

#######################################################

def easterEgg():
	
	print u"""
Real y verdaderamente os digo, señores que me oís, que a mí me pareció todo lo
que aquí ha pasado que pasaba al pie de la letra: que Melisendra era
Melisendra, don Gaiferos don Gaiferos, Marsilio Marsilio, y Carlomagno
Carlomagno: por eso se me alteró la cólera, y, por cumplir con mi profesión de
caballero andante, quise dar ayuda y favor a los que huían, y con este buen
propósito hice lo que habéis visto; si me ha salido al revés, no es culpa mía,
sino de los malos que me persiguen.

Don Quixote, Part Two, Chapter XXVI."""
	
	# print u"""
# Si me ha salido al revés, no es culpa mía, sino de los malos que me persiguen.

# Don Quixote, Part Two, Chapter XXVI."""

#------------------------------------------------------

def readAndWriteNewFASTAFile(inputFileName,
							outPutFileName,
							digestionPoints = "KR",
							maxPepLength = 200,
							minPepLength = 1,
							removePalindromes = False):

	reader = open(inputFileName, "r")
	writer = open(outPutFileName, "w")
	
	proteinHeader = ""
	proteinSequence = ""
	stringLength = 0

	for readerLine in reader:
	
		line = readerLine.strip()
		if len(line) > 0:
		
			newProtein = line.startswith(">")
			
			if newProtein:
			
				if len(proteinHeader) > 0:
				
					newProteinHeader = generateInvertedProteinHeader(proteinHeader)
					newProteinSequence =  pseudoInvertProteinSequence(proteinSequence,
																		digestionPoints,
																		maxPepLength,
																		minPepLength,
																		removePalindromes)
																		
					writeInvertedProtein(writer, newProteinHeader, newProteinSequence, stringLength)
					
				proteinHeader = line
				proteinSequence = ""
				newProtein = False
				
			else:
				if len(line) > stringLength: stringLength = len(line)
				proteinSequence += line
			

	# adding the last element
	newProteinHeader = generateInvertedProteinHeader(proteinHeader)
	newProteinSequence =  pseudoInvertProteinSequence(proteinSequence)
	writeInvertedProtein(writer, newProteinHeader, newProteinSequence, stringLength)
	
	writer.close()

#------------------------------------------------------

def generateInvertedProteinHeader(header, invertedSuffix = "_INV_"):

	invertedProteinHeader = ">" + invertedSuffix + header[1:]
	
	return invertedProteinHeader

#------------------------------------------------------

def writeInvertedProtein(writer, header, sequence, stringLength = 60):

	if stringLength < 1: 
		stringLength = 60
		
	rowList = []
	for position in range(len(sequence))[::stringLength]:
		rowList.append(sequence[position:position + stringLength])
		
	sequenceWithLineBreaks = "\n".join(rowList)
		 
	writer.write(header + "\n" + sequenceWithLineBreaks + "\n")
	
	return

#------------------------------------------------------

def pseudoInvertProteinSequence(proteinSequence,
							digestionPoints = "KR",
							maxPepLength = 200,
							minPepLength = 1,
							removePalindromes = False):
							
	peptides = separatePeptides(proteinSequence, digestionPoints)
	
	newPeptides = []
	for peptide in peptides:
		invertedPeptide = pseudoInvertPeptideSequence(peptide, digestionPoints)
		newPeptides.append(invertedPeptide)
	
	newProteinSequence = joinPeptideSequences(newPeptides, maxPepLength, minPepLength, removePalindromes)
	
	return newProteinSequence
	
#------------------------------------------------------

def separatePeptides(proteinSequence, digestionPoints = "KR"):
	
	for cutpoint in digestionPoints:
		proteinSequence = proteinSequence.replace(cutpoint, cutpoint + " ") 
	
	peptideList = proteinSequence.split(" ")
	
	return peptideList

#------------------------------------------------------
	
def pseudoInvertPeptideSequence(peptide, digestionPoints = "KR"):

	invertedPeptideSequence = peptide[::-1]
	for cleaveSite in digestionPoints:
		if peptide.endswith(cleaveSite):
			SequenceToInvert = peptide[0:-1]
			SequenceInvertedPart = SequenceToInvert[::-1]
			invertedPeptideSequence = SequenceInvertedPart + cleaveSite

	return invertedPeptideSequence
	
#------------------------------------------------------

def joinPeptideSequences(peptideList,
							maxPepLength = 200,
							minPepLength = 1,
							removePalindromes = False,
							digestionPoints = "KR"):
							
	newPeptides = []
	
	for peptide in peptideList:
		if len(peptide) <= maxPepLength and len(peptide) >= minPepLength and not(removePalindromes and isPalindrome(peptide, digestionPoints)):
			newPeptides.append(peptide)
			
	newPeptides = "".join(newPeptides)
	
	return newPeptides

#------------------------------------------------------

def isPalindrome (peptide, digestionPoints = "KR"):
	
	return peptide == pseudoInvertPeptideSequence(peptide, digestionPoints)

#------------------------------------------------------
	
def printHelp(version = None):

	print """
MaesePedro %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to
generate pseudoinverted FASTA files.

Sanson needs one input files:

     * a FASTA file (using the -f command)

And delivers two output files:

     * the inverted FASTA file
     * a log file (default suffix: "_logFile")

Usage: maesepedro.py -f[FASTAFile]

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files.
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the FASTA file folder.
   -c, --cleavesites=string
                       The residues after which the protease is cleaving.
                       Default is trypsin (KR). Note that only C-terminal
                       cleaving proteases are being considered in this version.
   -f, --fastafile=string
                       The input FASTA file to invert.
   -r, --removepalindromes
                       Remove peptides unchanged upon pseudoinversion, i.e.,
                       peptides such as ASSAK, EGTGER (when using trypsin).
                       Palindromic peptides are not removed by default.
""" % version

	return

#------------------------------------------------------

def main(argv):

	version = "v0.04"
	analysisName = ""
	cleaveSites = "KR" # trypsin default
	removePalindromes = False
	defaultAnalysisName = "inversor"
	analysisFolder = ""
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	defaultFastaExtension = ".fasta"
	graphFileFormat = "png"
	defaultFastaFile = "fastadef"
	invertedFastaFile = ""
	defaultInvertedFileSuffix = "inv"
	defaultLogFile = "logFile"
	fastaFile = ""
	logFile = ""
	logList = [["Inversor " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:p:f:c:rh", ["analysis=", "folder=", "fastafile=", "cleavesites=", "place=", "removepalindromes", "help", "egg", "easteregg"])
	except getopt.GetoptError:
		logList.append(["Error while getting parameters."])
		sys.exit(2)
	
	if len(opts) == 0:
		printHelp(version)
		sys.exit()
		
	for opt, arg in opts:
		if opt in ("-a", "--analysis"):
			analysisName = arg
		elif opt in ("-p", "--place", "--folder"):
			analysisFolder = arg
		elif opt in ("-f", "--fastafile"):
			fastaFile = arg
		elif opt in ("-c", "--cleavesites"):
			cleaveSites = arg.strip()
		elif opt in ("-r", "--removepalindromes"):
			removePalindromes = True
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("--egg", "--easteregg"):
			easterEgg()
			sys.exit()

# REGION: FILE NAMES SETUP

	if len(analysisName) == 0:
		if len(fastaFile) > 0:
			analysisName = os.path.splitext(os.path.basename(fastaFile))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	if len(fastaFile) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(fastaFile)) > 0:
			analysisFolder = os.path.dirname(fastaFile)

	# input
	if len(os.path.dirname(fastaFile)) == 0 and len(fastaFile) > 0:
		fastaFile = os.path.join(analysisFolder, fastaFile)
		
	# output
	
	if len(invertedFastaFile) == 0:
		invertedFastaFile = os.path.join(analysisFolder, analysisName + "_" + defaultInvertedFileSuffix + defaultFastaExtension)
	
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)

	logList.append([""])
	logList.append(["Input FASTA file: " + fastaFile])
	logList.append(["Inverted FASTA file: " + invertedFastaFile])
	logList.append(["Cleave sites used: " + cleaveSites])
	logList.append([""])

# END REGION: FILE NAMES SETUP			
	
	try:
		readAndWriteNewFASTAFile(fastaFile,
								invertedFastaFile,
								digestionPoints = cleaveSites,
								removePalindromes = removePalindromes)
		
		logList.append(["Everything went fine."])
	except getopt.GetoptError:
		logList.append(["Error."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	stats.saveFile(logFile, logList, "LOG FILE")
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])