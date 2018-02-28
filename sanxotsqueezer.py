import pdb
import sys
import getopt
import stats
import os
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4)

#######################################################

class statsResult:
	# statsResult.id2 --> higher level identifier
	# statsResult.Xj --> higher level X
	# statsResult.Vj --> higher level V
	# statsResult.id1 --> lower level identifier
	# statsResult.Xi --> lower level X (log2Ratio)
	# statsResult.Vi --> lower level weight without adding variance
	# statsResult.Wij --> lower level weight including variance
	# statsResult.nij --> lower level number of elements within the higher level element
	# statsResult.Zij --> distance in sigmas
	# statsResult.FDRij --> false discovery rate
	def __init__(self, id2 = None, Xj = None, Vj = None, id1 = None, Xi = None, Vi = None, Wij = None, nij = None, Zij = None, FDRij = None):
		self.id2 = id2
		self.Xj = Xj
		self.Vj = Vj
		self.id1 = id1
		self.Xi = Xi
		self.Vi = Vi
		self.Wij = Wij
		self.nij = nij
		self.Zij = Zij
		self.FDRij = FDRij

#------------------------------------------------------

def filterNFDRorZ(lowerData, higherData, minN = 2, maxN = 1e6, minZ = 0.0, maxFDR = sys.float_info.max, useFDR = True):
	# filter n
	# listNok, because listNok is for faster searching,
	# while listNok2 is for storing the nij
	listNok = []
	listNok2 = []
	for row in lowerData:
		lowerElement = convertToStatsResult(row)
		if lowerElement.nij >= minN and lowerElement.nij <= maxN and lowerElement.id2 not in listNok:
			listNok.append(lowerElement.id2)
			listNok2.append([lowerElement.id2, lowerElement.nij])
	
	# filter Z
	listNZok = []
	for row in higherData:
		higherElement = convertToStatsResult(row)
		if useFDR:
			if str(higherElement.FDRij) != "nan" and higherElement.id1 in listNok:
				if higherElement.FDRij <= maxFDR:
					index = stats.firstIndex(listNok, higherElement.id1)
					nij = int(listNok2[index][1])
					listNZok.append([higherElement.id1, nij, higherElement.Zij, higherElement.FDRij, higherElement.Xi - higherElement.Xj])
		else:
			if str(higherElement.Zij) != "nan" and higherElement.id1 in listNok:
				if abs(higherElement.Zij) >= minZ:
					index = stats.firstIndex(listNok, higherElement.id1)
					nij = int(listNok2[index][1])
					listNZok.append([higherElement.id1, nij, higherElement.Zij, higherElement.FDRij, higherElement.Xi - higherElement.Xj])
	
	return listNZok

#------------------------------------------------------

def convertToStatsResult(myList = []):
	if len(myList) != 9: return None
	else: return statsResult(id2 = myList[0], Xj = myList[1], Vj = myList[2], id1 = myList[3], Xi = myList[4], Vi = myList[5], nij = myList[6], Zij = myList[7], FDRij = myList[8])

#------------------------------------------------------

def printHelp(version = None):

	print """
SanXoTsqueezer %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used
mainly to find, while using the Systems Biology triangle, which categories
contain a determined number of proteins that are changing more than an FDR
set by the user.

SanXoTsqueezer needs two input files:

     * a lower level stats file (command -l)
     * a higher (or upper) level stats file (command -u)

And delivers one output file:

     * the list of changing higher level elements (which can be used as
     SanXoTGauss input to depict gaussians of relevant higher level elements).

Usage: sanxotsqueezer.py -l[lower level stats file] -u[upper level stats file] [OPTIONS]

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the
                       stats file.
   -f, --fdr=float     FDR to filter data. Default is 0.05. If -z is used, then
                       the program will filter only by Z.
   -l, --lowerstats=filename
                       The lower level stats input file.
   -L, --logfile=filename
                       To use a non-default name for the log file.
   -n, --minelements=integer
                       The minimum number of lower level elements that a higher
                       level element must include in the stats file. Default
                       is 2 (the minimum).
   -N, --maxelements=integer
                       The maximum number of lower level elements that a higher
                       level element must include in the stats file. Default
                       is 1e6.
   -o, --outputfile=filename
                       To use a non-default file name for the sigmoid table.
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the folder used will be the
                       same as the lower stats file folder.
   -u, --upperstats=filename
                       The higher (upper) level stats input file.
   -z, --sigmas=float  Filter by Z (the number of sigmas the higher level
                       element is deviating from the average). Note that by
                       using this option, you will prevent the program from
                       filtering by FDR (see -f).
""" % version

	return

#------------------------------------------------------

def main(argv):

	version = "v0.13"
	verbose = False
	analysisName = ""
	defaultAnalysisName = "squeeze"
	analysisFolder = ""
	# parametres
	minimumElements = 2
	maximumElements = 1e6
	maximumFDR = 0.05
	minimumZ = 0.0 # take all by default
	filterByFDR = True # if false, then it filters by abs(Z)
	# input files
	lowerStats = ""
	higherStats = ""
	defaultLowerStatsFile = "lower"
	defaultHigherStatsFile = "upper"
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	defaultOutputFile = "outList"
	defaultLogFile = "logFile"
	# output files
	logFile = ""
	outputFile = ""
	logList = [["SanXoTSqueezer " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:l:L:o:p:u:n:N:f:z:h", ["analysis=", "lowerstats=", "logfile=", "outputfile=", "place=", "minelements=", "maxelements=", "fdr=", "sigmas=", "help"])
	except getopt.GetoptError:
		logList.append(["Error while getting parameters."])
		sys.exit(2)
	
	if len(opts) == 0:
		printHelp(version)
		sys.exit()
		
	for opt, arg in opts:
		if opt in ("-a", "--analysis"):
			analysisName = arg
		if opt in ("-p", "--place", "--folder"):
			analysisFolder = arg
		if opt in ("-l", "--lowerstats"):
			lowerStats = arg
		if opt in ("-u", "--upperstats"):
			higherStats = arg
		elif opt in ("-L", "--logfile"):
			logFile = arg
		elif opt in ("-o", "--outputfile"):
			outputFile = arg
		elif opt in ("-n", "--minelements"):
			minimumElements = int(arg)
		elif opt in ("-N", "--maxelements"):
			maximumElements = int(arg)
		elif opt in ("-f", "--fdr"):
			maximumFDR = float(arg)
		elif opt in ("-z", "--sigmas"):
			filterByFDR = False
			minimumZ = float(arg)
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()

# REGION: FILE NAMES SETUP			
			
	if len(analysisName) == 0:
		if len(lowerStats) > 0:
			analysisName = os.path.splitext(os.path.basename(lowerStats))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	if len(lowerStats) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(lowerStats)) > 0:
			analysisFolder = os.path.dirname(lowerStats)

	# input
	if len(lowerStats) == 0:
		lowerStats = os.path.join(analysisFolder, analysisName + "_" + defaultLowerStatsFile + defaultTableExtension)
		
	if len(higherStats) == 0:
		higherStats = os.path.join(analysisFolder, analysisName + "_" + defaultHigherStatsFile + defaultTableExtension)
		
	if len(os.path.dirname(lowerStats)) == 0 and len(analysisFolder) > 0:
		lowerStats = os.path.join(analysisFolder, lowerStats)
		
	if len(os.path.dirname(higherStats)) == 0 and len(analysisFolder) > 0:
		higherStats = os.path.join(analysisFolder, higherStats)
	
	# output
	if len(outputFile) == 0:
		outputFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputFile + defaultTableExtension)
		
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
		
	if len(os.path.dirname(outputFile)) == 0 and len(os.path.basename(outputFile)) > 0:
		outputFile = os.path.join(analysisFolder, outputFile)
		
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)
		
	logList.append([""])
	logList.append(["Lower input stats file: " + lowerStats])
	logList.append(["Higher input stats file: " + higherStats])
	logList.append(["Output list: " + outputFile])
	logList.append(["Output log file: " + logFile])
	logList.append(["Minimum elements in higher category: " + str(minimumElements)])
	logList.append(["Maximum elements in higher category: " + str(maximumElements)])
	logList.append(["Minimum z: " + str(minimumZ)])
	logList.append([""])

	# pp.pprint(logList)
	# sys.exit()

# END REGION: FILE NAMES SETUP			

	try:
		lowerData = stats.loadStatsDataFile(lowerStats)
		logList.append(["Lower data files correctly loaded."])
	except getopt.GetoptError:
		logList.append(["Error while getting lower data files."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
		
	try:
		higherData = stats.loadStatsDataFile(higherStats)
		logList.append(["Higher data files correctly loaded."])
	except getopt.GetoptError:
		logList.append(["Error while getting higher data files."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	try:
		filteredList = filterNFDRorZ(lowerData, higherData, minN = minimumElements, maxN = maximumElements, minZ = minimumZ, maxFDR = maximumFDR, useFDR = filterByFDR)
		filteredList = stats.sortByIndex(filteredList, 1)
		logList.append(["Data correctly filtered."])
	except getopt.GetoptError:
		logList.append(["Error while getting data filtered by N and Z."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
		
	try:
		stats.saveFile(outputFile, filteredList, "id\tn\tZ\tFDR\tX")
		logList.append(["Output data correctly saved."])
	except getopt.GetoptError:
		logList.append(["Error while saving output data."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
		
	stats.saveFile(logFile, logList, "LOG FILE")
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])