import pdb
import getopt
import stats
import sanxot
import sys
import os
import gc
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4)

#######################################################

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

def detectRelationWithLeastFDR(statsData, FDRLimit = 0.01, modeUsed = mode.onlyOne):

	# modes
	# mode.onlyOne -> removes the relation with least FDR, if it has FDR < FDRLimit
	# mode.onePerHigher -> removes one relation for each higher level element, if it has FDR < FDRLimit
	#***
	
	relationsToRemove = []

	sortedStats = stats.sortByInstance(statsData, "FDRij", isDescendent = False)[::-1]

	if modeUsed == mode.onlyOne:
		leastFDR = sys.float_info.max
		leastFDRRow = []
		for statsRow in sortedStats:
			if statsRow.FDRij < leastFDR:
				leastFDR = statsRow.FDRij
				leastFDRRow = statsRow
		if leastFDRRow != []:
			if leastFDRRow.FDRij < FDRLimit:
				newRelationToRemove = [leastFDRRow.id2, leastFDRRow.id1]
				relationsToRemove = [newRelationToRemove]
			
	if modeUsed == mode.onePerHigher:
		for statsRow in sortedStats:
			if statsRow.FDRij < FDRLimit:
				higherSelection = stats.filterByElement(relationsToRemove, statsRow.id2)
				if len(higherSelection) == 0:
					# add new outlier relation
					newRelationToRemove = [statsRow.id2, statsRow.id1, statsRow.FDRij, abs(statsRow.Zij)]
					relationsToRemove.append(newRelationToRemove)
				else:
					# warning!! none should have len(higherSelection) > 1
					if len(higherSelection) == 1:
						# check which has the least FDRij, or the biggest |Zij| if FDRij == 0
						if (statsRow.FDRij < higherSelection[0][2] or (statsRow.FDRij == 0 and abs(statsRow.Zij) > higherSelection[0][3])):
							newRelationToRemove = [statsRow.id2, statsRow.id1, statsRow.FDRij, abs(statsRow.Zij)]
							relationsToRemove.remove(higherSelection[0])
							relationsToRemove.append(newRelationToRemove)

		relationsToRemove = stats.extractColumns(relationsToRemove, 0, 1)
	
	return relationsToRemove

#------------------------------------------------------

def detectOutliers(statsData, FDRLimit = 0.01):
	
		
	relationUnderFDR = []
	
	for row in statsData:
		if row.FDRij < FDRLimit:
			relationUnderFDR.append([row.id2, row.id1])

	return relationUnderFDR
	
#------------------------------------------------------

def removeOutliers(relations, relationsToRemove):
	
	# note that here outliers are removed independently of their tags
	# just removing all rows where id1 and id2 coincides
	
	newRelations = relations[:]

	if len(relationsToRemove) > 0:
		for eachRelation in relationsToRemove:
			#
			# while eachRelation in newRelations:
				# newRelations.remove(eachRelation)
			#
			# above previous code was simpler, but was buggy
			# as it was not removing relationsToRemove including tags
			# now, instead of removing eachRelation, it removes newRelations[i]
			# keep this for future reference
			i = 0
			while i < len(newRelations):
				if newRelations[i][0] == eachRelation[0] and newRelations[i][1] == eachRelation[1]:
					newRelations.remove(newRelations[i])
				else:
					i += 1
		
	return newRelations
	
#------------------------------------------------------

def getRelationsWithoutOutliers(data, relations, variance, FDRLimit = 0.01, modeUsed = mode.onlyOne, removeDuplicateUpper = False):

	# this method is included only for backward compatibility
	
	newRelations = relations[:]
	removedRelations = []
	startingLoop = True
	outliers = []
	while len(outliers) > 0 or startingLoop:
		
		startingLoop = False
		
		newRelations = removeOutliers(newRelations, outliers)
		removedRelations.extend(outliers)
		newVariance, dummyHigher, newStats, dummyLower, logResults, success = \
						sanxot.integrate(data = data,
								relations = newRelations,
								varianceSeed = variance,
								forceParameters = True,
								removeDuplicateUpper = removeDuplicateUpper)
		
		totOutliers = detectOutliers(newStats, FDRLimit = FDRLimit)
		outliers = detectRelationWithLeastFDR(newStats, FDRLimit = FDRLimit, modeUsed = modeUsed)
		
		print
		if len(outliers) > 0:
			print "%i outliers found, removing %i of them, and recalculating..." % (len(totOutliers), len(outliers))
		else:
			print "No outliers found at %f FDR." % FDRLimit
			print
		
		dummyHigher = []
		newStats = []
		dummyLower = []
		totOutliers = []
		gc.collect()
			
	return newRelations, removedRelations, logResults

#------------------------------------------------------

def tagRelationsWithoutOutliers(data, relations, variance, FDRLimit = 0.01, modeUsed = mode.onlyOne, removeDuplicateUpper = False, tags = "!out", outlierTag = "out", logicOperatorsAsWords = False):

	newRelations = relations[:]
	
	removedRelations = []
	startingLoop = True
	outliers = []
	while len(outliers) > 0 or startingLoop:
		
		startingLoop = False
		
		newRelations = stats.addTagToRelations(newRelations, outliers, outlierTag)

		removedRelations.extend(outliers)
		newVariance, dummyHigher, newStats, dummyLower, logResults, success = \
						sanxot.integrate(data = data,
								relations = newRelations,
								varianceSeed = variance,
								forceParameters = True,
								removeDuplicateUpper = removeDuplicateUpper,
								tags = tags,
								logicOperatorsAsWords = logicOperatorsAsWords)
		
		totOutliers = detectOutliers(newStats, FDRLimit = FDRLimit)
		outliers = detectRelationWithLeastFDR(newStats, FDRLimit = FDRLimit, modeUsed = modeUsed)
		
		print
		if len(outliers) > 0:
			print "%i outliers found, tagging %i of them as 'out', and recalculating..." % (len(totOutliers), len(outliers))
		else:
			print "No outliers found at %f FDR." % FDRLimit
			print
		
		dummyHigher = []
		newStats = []
		dummyLower = []
		totOutliers = []
		gc.collect()
			
	return newRelations, removedRelations, logResults

#------------------------------------------------------
	
def printHelp(version = None, advanced = False):

	print """
SanXoTSieve %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to
perform automatical removal of lower level outliers in an integration
performed using the SanXoT integrator.

SanXoTSieve needs the two input files of a SanXoT integration
(see SanXoT's help): commands -d and -r, respectively.

And the resulting variance of the integration that has been performed:
commands -V (assigned from the info file of the integration.) or -v.

... and delivers two output files:

     * a new relations file (by default suffixed "_tagged"), which is
     identical to the original relations file, but tagging in the third column
     the relations marked as outlier.
     
     * the log file.
     
Usage: sanxotsieve.py -d[data file] -r[relations file] -V[info file] [OPTIONS]""" % version

	if advanced:
		print """
   -h, --help          Display basic help and exit.
   -H, --advanced-help Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the data
                       file.
   -b, --no-verbose    Do not print result summary after executing.
   -d, --datafile=filename
                       Data file with identificators of the lowel level in the
                       first column, measured values (x) in the second column,
                       and weights (v) in the third column.
   -D, --removeduplicateupper
                       When merging data with relations table, remove duplicate
                       higher level elements (not removed by default).
   -f, --fdrlimit=float
                       Use an FDR limit different than 0.01 (1%).
   -L, --infofile=filename
                       To use a non-default name for the log file.
   -n, --newrelfile=filename
                       To use a non-default name for the relations file
                       containing the tagged outliers.
   -o, --outlierrelfile=filename
                       To use a non-default name for the relations responsible
                       of outliers (note that outlier relations are only saved
                       when the --oldway option is active)
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the folder used will be the
                       same as the input folder.
   -r, --relfile, --relationsfile=filename
                       Relations file, with identificators of the higher level
                       in the first column, and identificators of the lower
                       level in the second column.
   -u, --one-to-one    Remove only one outlier per cycle. This is slightly more
                       accurate than the default mode (where the outermost
                       outlier of each category with outliers is removed in
                       each cycle), but usually exacerbatingly slow.
   -v, --var, --varianceseed=double
                       Variance used in the concerning integration.
                       Default is 0.001.
   -V, --varfile=filename
                       Get the variance value from a text file. It must contain
                       a line (not more than once) with the text
                       "Variance = [double]". This suits the info file from a
                       previous integration (see -L in SanXoT).
   --oldway            Do it the old way: instead of tagging, create two
                       separated relation files, with and without outliers.
   --outliertag=string To select a non-default tag for outliers (default: out)
   --tags=string       To define a tag to distinguish groups to perform the
                       integration. The tag can be used by inclusion, such as
                            --tags="mod"
                       or by exclusion, putting first the "!" symbol, such as
                            --tags="!out"
                       Tags should be included in a third column of the
                       relations file. Note that the tag "!out" for outliers is
                       implicit.
                       Different tags can be combined using logical operators
                       "and" (&), "or" (|), and "not" (!), and parentheses.
                       Some examples:
                            --tags="!out&mod"
                            --tags="!out&(dig0|dig1)"
                            --tags="(!dig0&!dig1)|mod1"
                            --tags="mod1|mod2|mod3"
"""
	else:
		print """
Use -H or --advanced-help for more details."""

	return
	
#------------------------------------------------------

def main(argv):
	
	version = "v0.17"
	analysisName = ""
	analysisFolder = ""
	varianceSeed = 0.001
	FDRLimit = 0.01
	varianceSeedProvided = False
	removeDuplicateUpper = False
	tags = "!out"
	outlierTag = "out"
	logicOperatorsAsWords = False
	dataFile = ""
	relationsFile = ""
	newRelFile = ""
	removedRelFile = ""
	defaultDataFile = "data"
	defaultRelationsFile = "rels"
	defaultTaggedRelFile = "tagged"
	defaultNewRelFile = "cleaned"
	defaultRemovedRelFile = "outliers"
	defaultOutputInfo = "infoFile"
	infoFile = ""
	varFile = ""
	defaultTableExtension = ".tsv"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	verbose = True
	oldWay = False # instead of tagging outliers, separating relations files, the old way
	modeUsed = mode.onePerHigher
	logList = [["SanXoTSieve " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:p:v:d:r:n:L:V:f:ubDhH", ["analysis=", "folder=", "varianceseed=", "datafile=", "relfile=", "newrelfile=", "outlierrelfile=", "infofile=", "varfile=", "fdrlimit=", "one-to-one", "no-verbose", "randomise", "removeduplicateupper", "help", "advanced-help", "tags=", "outliertag=", "oldway", "word-operators"])
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
		if opt in ("-v", "--var", "--varianceseed"):
			varianceSeed = float(arg)
			varianceSeedProvided = True
		elif opt in ("-d", "--datafile"):
			dataFile = arg
		elif opt in ("-r", "--relfile", "--relationsfile"):
			relationsFile = arg
		elif opt in ("-n", "--newrelfile"):
			removedRelFile = arg
		elif opt in ("-L", "--infofile"):
			infoFile = arg
		elif opt in ("-V", "--varfile"):
			varFile = arg
		elif opt in ("-u", "--one-to-one"):
			modeUsed = mode.onlyOne
		elif opt in ("-b", "--no-verbose"):
			verbose = False
		elif opt in ("--oldway"):
			oldWay = True
		elif opt in ("-f", "--fdrlimit"):
			FDRLimit = float(arg)
		elif opt in ("-D", "--removeduplicateupper"):
			removeDuplicateUpper = True
		elif opt in ("--tags"):
			if arg.strip().lower() != "!out":
				tags = "!out&(" + arg + ")"
		elif opt in ("--word-operators"):
			logicOperatorsAsWords = True
		elif opt in ("--outliertag"):
			outlierTag = "out"
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("-H", "--advanced-help"):
			printHelp(version, advanced = True)
			sys.exit()
	
# REGION: FILE NAMES SETUP
			
	if len(analysisName) == 0:
		if len(dataFile) > 0:
			analysisName = os.path.splitext(os.path.basename(dataFile))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	if len(dataFile) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(dataFile)) > 0:
			analysisFolder = os.path.dirname(dataFile)

	# input
	if len(dataFile) == 0:
		dataFile = os.path.join(analysisFolder, analysisName + "_" + defaultDataFile + defaultTableExtension)
		
	if len(os.path.dirname(dataFile)) == 0 and len(analysisFolder) > 0:
		dataFile = os.path.join(analysisFolder, dataFile)
	
	if len(os.path.dirname(varFile)) == 0 and len(os.path.basename(varFile)) > 0:
		varFile = os.path.join(analysisFolder, varFile)
		
	if len(varFile) > 0 and not varianceSeedProvided:
		varianceSeed, varianceOk = stats.extractVarianceFromVarFile(varFile, verbose = verbose, defaultSeed = varianceSeed)
		if not varianceOk:
			logList.append(["Variance not found in text file."])
			stats.saveFile(infoFile, logList, "INFO FILE")
			sys.exit()
	
	if len(relationsFile) == 0:
		relationsFile = os.path.join(analysisFolder, analysisName + "_" + defaultRelationsFile + defaultTableExtension)
	
	if len(os.path.dirname(relationsFile)) == 0:
		relationsFile = os.path.join(analysisFolder, relationsFile)
	
	# output
	if len(newRelFile) == 0:
		if oldWay: # suffix: "cleaned"
			newRelFile = os.path.join(analysisFolder, analysisName + "_" + defaultNewRelFile + defaultTableExtension)
		else: # suffix: "tagged"
			newRelFile = os.path.join(analysisFolder, analysisName + "_" + defaultTaggedRelFile + defaultTableExtension)
	
	if len(removedRelFile) == 0:
		removedRelFile = os.path.join(analysisFolder, analysisName + "_" + defaultRemovedRelFile + defaultTableExtension)
	
	if len(os.path.dirname(newRelFile)) == 0:
		newRelFile = os.path.join(analysisFolder, newRelFile)
		
	if len(os.path.dirname(removedRelFile)) == 0:
		removedRelFile = os.path.join(analysisFolder, removedRelFile)
	
	if len(infoFile) == 0:
		infoFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputInfo + defaultTextExtension)
	
	logList.append(["Variance seed = " + str(varianceSeed)])
	logList.append(["Input data file: " + dataFile])
	logList.append(["Input relations file: " + relationsFile])
	if oldWay:
		logList.append(["Output relations file without outliers: " + newRelFile])
		logList.append(["Output relations file with outliers only: " + removedRelFile])
		logList.append(["Removing duplicate higher level elements: " + str(removeDuplicateUpper)])
		logList.append(["OldWay option activated: outliers are removed instead of tagged"])
	else:
		logList.append(["Relations file tagging outliers: " + newRelFile])
		logList.append(["Tags to filter relations: " + tags])
		logList.append(["Tag used for outliers: " + outlierTag])

	# pp.pprint(logList)
	# sys.exit()

# END REGION: FILE NAMES SETUP
	
	relations = stats.loadRelationsFile(relationsFile)
	data = stats.loadInputDataFile(dataFile)
	
	if oldWay:
		# only for backward compatibility. Note that tags are not supported
		newRelations, removedRelations, logResults = \
								getRelationsWithoutOutliers(data,
										relations,
										varianceSeed,
										FDRLimit = FDRLimit,
										modeUsed = modeUsed,
										removeDuplicateUpper = removeDuplicateUpper)
	else:
		newRelations, removedRelations, logResults = \
								tagRelationsWithoutOutliers(data,
										relations,
										varianceSeed,
										FDRLimit = FDRLimit,
										modeUsed = modeUsed,
										removeDuplicateUpper = removeDuplicateUpper,
										tags = tags,
										outlierTag = outlierTag,
										logicOperatorsAsWords = logicOperatorsAsWords)
		
	if oldWay:
		stats.saveFile(newRelFile, newRelations, "idsup\tidinf")
	else:
		stats.saveFile(newRelFile, newRelations, "idsup\tidinf\ttags")
		
	stats.saveFile(infoFile, logList, "INFO FILE")
	
	if oldWay:
		stats.saveFile(removedRelFile, removedRelations, "idsup\tidinf")
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])