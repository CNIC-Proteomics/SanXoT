import pdb
import getopt
import stats
import sys
import os
import glob
import shutil
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4)

#######################################################

def easterEgg():

	print u"""
Así es la verdad -respondió Anselmo-, y con esa confianza te hago saber,
amigo Lotario, que el deseo que me fatiga es pensar si Camila, mi esposa,
es tan buena y tan perfeta como yo pienso; y no puedo enterarme en esta
verdad, si no es probándola de manera que la prueba manifieste los quilates
de su bondad, como el fuego muestra los del oro.

Don Quixote, Part Two, Chapter XXXIII."""

#------------------------------------------------------

class mode:
	onlyOne = 1
	onePerHigher = 2

#------------------------------------------------------

class higherResult:
	def __init__(self, id2 = None, Xj = None, Vj = None):
		self.id2 = id2
		self.Xj = Xj
		self.Vj = Vj
		
#------------------------------------------------------

class lowerResult:
	def __init__(self, id1 = None, XiXj = None, Wj = None):
		self.id1 = id1
		self.XiXj = XiXj
		self.Wj = Wj
		
#------------------------------------------------------

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

def getMedianIndex(varList = [], variance = 0):
	
	closestFileIndex = 0
	lowestDifference = sys.float_info.max
	for elementIndex in xrange(len(varList)):
		varDifference = abs(variance - float(varList[elementIndex][1]))
		if varDifference < lowestDifference:
			lowestDifference = varDifference
			closestFileIndex = elementIndex
	
	return closestFileIndex

#------------------------------------------------------

def copyFilesWithPrefix(fileList = [],
						folder = "",
						prefix = "",
						message = "Error!",
						tag = ""):
	logList = []
	logList.append([])
	logList.append([message])
	invariablePart = os.path.join(folder, prefix)
	for originalFileName in fileList:
		FNSuffix = originalFileName.split("_")[-1]
		FNDirectory = os.path.dirname(originalFileName)
		newBaseName = tag + "_" + prefix + "_" + FNSuffix
		newFileName = os.path.join(FNDirectory, newBaseName)
		logList.append(["%s\t->\t%s" % (os.path.basename(originalFileName), newBaseName)])
		
		shutil.copyfile(originalFileName, newFileName)
	
	return logList
	
#------------------------------------------------------
	
def printHelp(version = None, advanced = False):

	print """
Anselmo %s is a program made in the Jesus Vazquez Cardiovascular Proteomics
Lab at Centro Nacional de Investigaciones Cardiovasculares, used to identify
the integration which holds the median variance from a set of randomised
SanXoT integrations (i.e., integrations performed using SanXoT's parametre -R).

Anselmo needs at least:

1) the prefix (by using the -f argument) of the set of experiments, i.e. when
the info files of the randomisations are such as:

    heartExperiment1_infoFile.txt
    heartExperiment2_infoFile.txt
    ...
    heartExperimentZ_infoFile.txt

the prefix is considered to be "heartExperiment".

2) the folder where all those info files are (they must be in the same folder),
using the -p argument.

After reading the variances in the set of info files, Anselmo identifies the
info file containing the median of the set of variances, and then it renames
the files using its prefix, i.e. using the previous example, and assuming the
median of the variance is in experiment labelled "9", then it copies the files

    heartExperiment9_infoFile.txt
    heartExperiment9_higherLevel.txt
    heartExperiment9_outStats.txt
    ...

into

    med_heartExperiment_infoFile.txt
    med_heartExperiment_higherLevel.txt
    med_heartExperiment_outStats.txt
    ...
     
Usage: anselmo.py -p[folder] -fyeast_nullHypothesis [OPTIONS]""" % version

	if advanced:
		print """
   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files (for the current
                       version, this only affects the log file).
   -f, --prefix=string Prefix used for the integration of the N randomised
                       experiments.
   -g, --extraprefix=string
                       Additional copy for another set of files produced by
                       an integration, using the same tag as the median
                       calculated via -f.
   -L, --logfile=filename
                       To use a non-default name for the log file.
   -m, --mediantag=string
                       To use a non-default tag for the copied files, which
                       will be used as prefix (default is "med").
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the folder used will be the
                       same as the input folder.
"""
	else:
		print """
Use -H or --advanced-help for more details."""

	return
	
#------------------------------------------------------

def main(argv):
	
	version = "v0.05"
	analysisName = ""
	analysisFolder = ""
	logFile = ""
	
	# in data
	prefix = ""
	extraPrefix = ""
	medianTag = "med"
	
	# default filenames
	defaultInfoFileSuffix = "_infoFile.txt"
	defaultLogFile = "logFile"
	defaultAnalysisName = "medianSelection"
	
	# default extensions
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	
	verbose = True
	logList = [["Anselmo " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:p:f:g:m:L:hH", ["analysis=", "folder=",  "prefix=", "extraprefix=", "mediantag=", "logfile=", "help", "egg", "easteregg"])
	except getopt.GetoptError:
		logList.append(["Error while getting parameters."])
		stats.saveFile(infoFile, logList, "INFO FILE")
		sys.exit(2)

	if len(opts) == 0:
		printHelp(version, True)
		sys.exit()

	for opt, arg in opts:
		if opt in ("-a", "--analysis"):
			analysisName = arg
		elif opt in ("-p", "--place", "--folder"):
			analysisFolder = arg
		elif opt in ("-f", "--prefix"):
			prefix = arg
		elif opt in ("-g", "--extraprefix"):
			extraPrefix = arg
		elif opt in ("-L", "--logfile"):
			logFile = arg
		elif opt in ("-m", "--mediantag"):
			medianTag = arg
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("-H", "--advanced-help"):
			printHelp(version, advanced = True)
			sys.exit()
		elif opt in ("--egg", "--easteregg"):
			easterEgg()
			sys.exit()
	
# REGION: FILE NAMES SETUP
			
	if len(analysisName) == 0:
		analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
	
	# next "if" disables extra copy when extraPrefix is same as prefix
	if len(extraPrefix) > 0 and extraPrefix == prefix:
		extraPrefix = ""
	# input
	
	# output
	
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
	
	##logList.append(["Median variance = " + "poner***"])

# END REGION: FILE NAMES SETUP
	
	# get infoFile list
	infoFileList = glob.glob(os.path.join(analysisFolder, prefix + "*" + defaultInfoFileSuffix))
	
	logList.append([])
	logList.append(["Folder = " + analysisFolder])
	logList.append([])
	logList.append(["Info files with prefix \"%s\"" % prefix])
	
	varList = []
	for varFile in infoFileList:
		variance, varianceOk = stats.extractVarianceFromVarFile(varFile, verbose = False)
		if varianceOk:
			varList.append([varFile, variance])
	
	# get info file with median variance
	
	varList = stats.sortByIndex(varList, 1)
	medianVariance = stats.medianByIndex(varList, 1)
	
	medianIndex = getMedianIndex(varList = varList, variance = medianVariance)
	
	for element in varList:
		if element[0] == varList[medianIndex][0]:
			logList.append(["%s, variance = %f [taken]" % (os.path.basename(element[0]), element[1])])
		else:
			logList.append(["%s, variance = %f" % (os.path.basename(element[0]), element[1])])
	
	# get prefix of median experiment
	
	medianInfoFile = os.path.basename(varList[medianIndex][0])
	randTag = medianInfoFile[len(prefix):len(medianInfoFile) - len(defaultInfoFileSuffix)]
	medianPrefix = prefix + randTag
	extraMedianPrefix = ""
	if len(extraPrefix) > 0: extraMedianPrefix = extraPrefix + randTag
		
	
	# get file list with specific prefix
	medianExperimentFileList = glob.glob(os.path.join(analysisFolder, medianPrefix + "*.*"))
	extraPrefixFileList = []
	if len(extraMedianPrefix) > 0:
		extraPrefixFileList = glob.glob(os.path.join(analysisFolder, extraMedianPrefix + "*.*"))
	
	# copy files including median tag
	extraLogList = copyFilesWithPrefix(fileList = medianExperimentFileList,
				folder = analysisFolder,
				prefix = prefix,
				message = "Renamed files:",
				tag = medianTag)
	logList.extend(extraLogList)
	
	if len(extraPrefixFileList) > 0:
		extraLogList = copyFilesWithPrefix(fileList = extraPrefixFileList,
					folder = analysisFolder,
					prefix = extraPrefix,
					message = "Renamed extra files:",
					tag = medianTag)
		logList.extend(extraLogList)
	
	# save logFile
	
	stats.saveFile(logFile, logList, "INFO FILE")
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])