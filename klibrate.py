import pdb
import sys
import getopt
import stats
import os
import gc
import random
import glob # for the LogMasher
import re # for the LogMasher
from datetime import datetime # for Cardenio
from numpy import *
from pylab import *
from scipy.optimize import leastsq
import matplotlib.pyplot as plt

from time import strftime
from datetime import datetime # for the timer in random seed (SanXoT)
import argparse # to load arguments easily

# libraries for SanXoTViewer
### PANDAS BLOCKED
# import pandas as pd # to load and merge tables
### WX BLOCKED
# import wx # to create the GUI
import re # for regular expressions
# import matplotlib.cbook as cbook # to check an iterable (remove if possible)

# next lines are important
# they are to include the library to the library.zip file
# which is shared with other programs of the same package
# DO NOT REMOVE
from xml.etree import ElementTree
from scipy.stats import norm
import sanxot
import aljamia
import subprocess
import pprint
import math
import sqlite3 # for Mojón
from optparse import OptionParser

#######################################################

def easterEgg():

	print u"""
... pero dígame vuestra merced, señor bachiller: ¿qué hazañas mías son las que
más se ponderan en esa historia?

Don Quixote, Part Two, Chapter III."""

#------------------------------------------------------

def calibrate(inputRawData = None,
					inputRelations = None,
					rawDataFile = "",
					relationsFile = "",
					kSeed = 1,
					varianceSeed = 0.001,
					medianSide = 100,
					maxIterations = 0,
					verbose = False,
					showGraph = False,
					showSumSQ = False,
					forceParameters = False,
					alphaSeed = 1.0,
					showRank = True,
					useCooperativity = False,
					graphFileVRank = "",
					graphFileVValue = "",
					graphDataFile = "",
					graphDPI = None):

	extraLog = []
	extraLog.append([])
	if verbose:
		print
		print "loading input raw data file"
		extraLog.append(["loading input raw data file"])
	
	if inputRawData == None:
		if len(rawDataFile) == 0:
			print "Error: no input raw data"
			extraLog.append(["Error: no input raw data"])
			
		else:
			inputRawData = stats.loadInputDataFile(rawDataFile)
	
	if verbose:
		print "loading relations file"
		extraLog.append(["loading relations file"])
	
	if inputRelations == None:
		if len(relationsFile) == 0:
			if not forceParameters:
				print "Error: no relations file"
				extraLog.append(["Error: no relations file"])
				return None, None, None, None, extraLog
		else:
			inputRelations = stats.loadRelationsFile(relationsFile)
	
	#### calculate k and variance ####
	
	alpha = 1.0
	if not forceParameters:
		if verbose:
			print "calculating K and variance"
			extraLog.append(["calculating K and variance"])

		# *** just to see it
		result = getKandVariance(inputRawData, inputRelations, kSeed = kSeed, varianceSeed = varianceSeed, maxIterations = maxIterations, verbose = True, showSumSQ = True, medianSide = medianSide, alphaSeed = alphaSeed, useCooperativity = useCooperativity)
		
		k = result[0]
		variance = result[1]
		if useCooperativity: alpha = result[2]
	else:
		k = kSeed
		variance = varianceSeed
		alpha = alphaSeed
	
	# save VRank graph
	showGraphTool(inputRawData, inputRelations, k, variance, alpha, medianSide, showRank = True, graphFile = graphFileVRank, graphData = graphDataFile, dpi = graphDPI, showGraph = showGraph)
	# save VValue graph
	showGraphTool(inputRawData, inputRelations, k, variance, alpha, medianSide, showRank = False, graphFile = graphFileVValue, dpi = graphDPI, showGraph = showGraph)
	
	# get calibrated idXV
	
	idXV = idXVcal(inputRawData, k, alpha)
	
	return idXV, variance, k, alpha, extraLog

#------------------------------------------------------

# moved from stats

def getMADDistribution(nextIdX,
						mergedData,
						k,
						variance,
						alpha,
						medianSide = 100,
						showGraph = False,
						verbose = False):
	
	MADconstant = 1.48260221850560 # *** 1 / DISTR.NORM.ESTAND.INV(3 / 4) get exact number
	MADDistribution = []
	distrWeight = []

	# inputSequences = extractColumns(input, 0)
	# outputSequences = extractColumns(output, 0)
	
	newlist = []
	for orow in nextIdX:
		sequence = orow[0]
		# it is important to avoid sorting to keep it fast
		# so in next line do not foget sort = False
		# this should arrive here already sorted
		scanListWithSequence = stats.filterByElement(mergedData, sequence, sort = False)
		
		if len(scanListWithSequence) > 1: # otherwise Xi = Xj --> Xi - Xj = 0 --> does not work
			for scanRow in scanListWithSequence:
				newrow = []
				weight = scanRow[3] # the V
				degreesOfFreedom = len(scanListWithSequence)
				XiXj = scanRow[2] - orow[1]
				newrow.append(sequence) # sequence = 0
				newrow.append(scanRow[1]) # scan number = 1
				newrow.append(XiXj) # Xi - Xj = 2
				newrow.append(weight) # weight = 3
				newrow.append(len(scanListWithSequence)) # degrees of freedom = 4
				newrow.append(fabs(XiXj) * sqrt(float(degreesOfFreedom) / (float(degreesOfFreedom - 1)))) # = 5
				newrow.append(0) # space to save the median = 6
				newrow.append(0) # space to save the MAD formula = 7

				newlist.append(newrow)
	
	newlist = stats.sortByIndex(newlist, 3) # sort by weight
	
	# get median + rank
	nextlist = []
	counter = 0
	
	if len(newlist) < medianSide * 2:
		if verbose:
			print 'Not enough data to perform statistics,'
			print 'len(newlist) = %s, while medianSide = %s' % (str(len(newlist)), str(medianSide))
		sys.exit()
	
	for i in range(len(newlist))[medianSide:len(newlist) - medianSide]:
		window = newlist[i - medianSide:i + medianSide + 1]
		median = stats.medianByIndex(window, 5)
		newlist[i][6] = median

	# fill the borders
	for i in range(len(newlist))[:medianSide]:
		newlist[i][6] = newlist[medianSide + 1][6]
	
	for i in range(len(newlist))[len(newlist) - medianSide:]:
		newlist[i][6] = newlist[len(newlist) - medianSide - 1][6]

	# fill MAD formula
	for i in range(len(newlist)):
		newlist[i][7] = 1 / (MADconstant * newlist[i][6]) ** 2
		MADDistribution.append(newlist[i][7])
		distrWeight.append(newlist[i][3])

	if verbose:
		print 'k = %f, var = %f' % (k, variance)

	return MADDistribution, distrWeight

#------------------------------------------------------
# moved from stats

def getInverseOfFit(mergedData, k, variance, alpha):
	
	inverseOfFit = []
	#input = stats.sortByIndex(input, 2)

	for element in mergedData:
		sequence = element[0]
		# sort = False for speeding
		scanListWithSequence = stats.filterByElement(mergedData, sequence, sort = False)
		if len(scanListWithSequence) > 1:
			weight = element[3]
			inverseOfFit.append(getW_klibrate(weight, k, variance, alpha))

	inverseOfFit = sort(inverseOfFit) # sort by weight
	
	return inverseOfFit

#------------------------------------------------------

# copied to klibrate
def residuals(params, inputRawData, inputRelations, medianSide, verbose = False, showSumSQ = False, useCooperativity = False):

	k = params[0]
	variance = params[1]
	alpha = 1.0
	if useCooperativity: alpha = params[2]

	inputRawData.sort()
	inputRelations.sort()
	
	windowWidth = medianSide * 2 + 1
	if len(inputRawData) < windowWidth:
		print 'Error: window for median is bigger than total input size'
		sys.exit()
	
	# output = makeStats(k, variance, input = input)
	nextIdXData = getNextIdX_klibrate(inputRawData, inputRelations, k, variance, alpha, giveMergedData = True)
	
	nextIdX = nextIdXData[0]
	mergedData = nextIdXData[1]
	
	experimental, weights = asarray(getMADDistribution(nextIdX, mergedData, k, variance, alpha, medianSide, verbose = False))
	theoretical = asarray(getInverseOfFit(mergedData, k, variance, alpha))
	
	experArray = asarray(experimental[medianSide:len(experimental) - medianSide + 1])
	theorArray = asarray(theoretical[medianSide:len(experimental) - medianSide + 1])
	
	if len(experArray) != len(theorArray):
		print 'Error: experimental and theoretical array do not match'
		sys.exit()
	
	if verbose:
		if showSumSQ and len(experArray) == len(theorArray):
			totSumSQ = 0
			for i in range(len(experArray)):
				totSumSQ += (experArray[i] - theorArray[i]) ** 2
			
			if useCooperativity:
				print 'k = %g, var = %g, alpha = %g, sumSQ = %e' % (k, variance, alpha, totSumSQ)
			else:
				print 'k = %g, var = %g, sumSQ = %e' % (k, variance, totSumSQ)
		else:
			if useCooperativity:
				print 'k = ' + str(k) + ', var = ' + str(variance) + ', alpha = ' + str(alpha)
			else:
				print 'k = ' + str(k) + ', var = ' + str(variance)
		
	diff = experArray - theorArray
	return diff

#------------------------------------------------------

def getNextIdX_klibrate(idXVall, relations, k = 1.0, variance = 0.0, alpha = 1.0, giveMergedData = False):
	
	idX = []
	
	# no need to sort: mergeInput will do it anyway
	# idXVall.sort()
	# relations.sort()
	
	idXVWall = addW_klibrate(idXVall, k, variance, alpha)
	
	mergedData = stats.mergeInput(idXVWall, relations)
	
	position = 0
	id2old = ""
	XWlist = []
	
	if len(mergedData) == 0:
		print "Error, merged data list is empty. Please check the provided files do exist and are not corrupt."
		sys.exit()
	
	while position < len(mergedData):
		
		id2 = mergedData[position][0]
		
		if id2 != id2old and len(XWlist) > 0:
			
			x2 = stats.getNextX(XWlist)
			idX.append([id2old, x2])
			XWlist = []
		
		else:
			
			XWspecific = [mergedData[position][2], mergedData[position][4]]
			XWlist.append(XWspecific)
			position += 1
		
		id2old = id2
	
	# the last one has not been added, so...
	
	x2 = stats.getNextX(XWlist)
	idX.append([id2old, x2])
	
	if giveMergedData:
		return [idX, mergedData]
	else:
		return idX

#------------------------------------------------------

def getW_klibrate(v, k = 1.0, variance = 0.0, alpha = 1.0):

	w = 1 / (((k ** alpha) / (v ** alpha)) + variance)
	return w

#------------------------------------------------------

def addW_klibrate(idXVlist, k = 1.0, variance = 0.0, alpha = 1.0):
	
	idXVWlist = []
	
	for row in idXVlist:
		
		id = row[0]
		x = row[1]
		v = row[2]
		w = getW_klibrate(v, k, variance, alpha)
		
		idXVWlist.append([id, x, v, w])
	
	return idXVWlist

#------------------------------------------------------
# copied to klibrate
def getKandVariance(inputRawData,
					inputRelations,
					maxIterations = 0,
					kSeed = 1.0,
					varianceSeed = 0.001,
					medianSide = 100,
					verbose = False,
					showSumSQ = False,
					alphaSeed = 1.0,
					useCooperativity = False):

	if useCooperativity:
		seed = [kSeed, varianceSeed, alphaSeed]
		bestSol, success = leastsq(residuals, seed, args = (inputRawData, inputRelations, medianSide, verbose, showSumSQ, useCooperativity), maxfev = maxIterations)
	else:
		seed = [kSeed, varianceSeed]
		bestSol, success = leastsq(residuals, seed, args = (inputRawData, inputRelations, medianSide, verbose, showSumSQ, useCooperativity), maxfev = maxIterations)
	
	kOut = bestSol[0]
	varianceOut = bestSol[1]
	if useCooperativity: alphaOut = bestSol[2]
	# kOut = k
	# varianceOut = variance
	
	if verbose:
		print
		print "K = " + str(kOut)
		print "Variance = " + str(varianceOut)
		if useCooperativity: print "Alpha = " + str(alphaOut)
		
	if useCooperativity: return [kOut, varianceOut, alphaOut]
	else: return [kOut, varianceOut]
	
#------------------------------------------------------

def showGraphTool(inputRawData,
					inputRelations,
					k,
					variance,
					alpha,
					medianSide,
					verbose = False,
					showRank = False,
					graphFile = None,
					graphData = None,
					dpi = None,
					showGraph = True):
	
	plt.clf()
	inputRawData.sort()
	inputRelations.sort()
	
	windowWidth = medianSide * 2 + 1
	if len(inputRawData) < windowWidth:
		print 'Error: window for median is bigger than total input size'
		sys.exit()
	
	# output = makeStats(k, variance, input = input)
	nextIdXData = getNextIdX_klibrate(inputRawData, inputRelations, k, variance, alpha, giveMergedData = True)
	
	nextIdX = nextIdXData[0]
	mergedData = nextIdXData[1]

	MADdistrOut, weights = getMADDistribution(nextIdX, mergedData, k, variance, alpha, medianSide)
	invOfFitOut = getInverseOfFit(mergedData, k, variance, alpha)

	MADdistrOut = MADdistrOut[medianSide:len(MADdistrOut) - medianSide + 1]
	invOfFitOut = invOfFitOut[medianSide:len(invOfFitOut) - medianSide + 1]
	weights = weights[medianSide:len(weights) - medianSide + 1]
	
	# folderToSave = "D:\\DATUMARO\\trabajo\\programas_repositorio\\BioSistemas SanXoT\\MicroArrays\\intento5 CvsCs usando var robusta por partes\\"
	# stats.saveFile(folderToSave + "MADdistrOut.txt", MADdistrOut)
	# stats.saveFile(folderToSave + "invOfFitOut.txt", invOfFitOut)
	# stats.saveFile(folderToSave + "weights.txt", weights)
	
	if showRank:
		plt.plot(range(len(MADdistrOut)), MADdistrOut, 'g.', range(len(invOfFitOut)), invOfFitOut, 'r', linewidth=1.0, markersize=2.0, markeredgewidth=0.0)
		plt.xlabel('rank($V_s$)')
		plt.ylabel('1 / MSD')
		
		# to save data
		# *** use a better filename
		dataToSave = []
		for i in xrange(len(MADdistrOut)):
			dataToSave.append([i, weights[i], MADdistrOut[i], invOfFitOut[i]])
			
		if graphData:
			stats.saveFile(graphData, dataToSave, "rank(Vs)\tweight\tMAD\t1/fit")
	else:
	
		# uncomment to graph MSD instead of 1 / MSD
		#
		# for i in xrange(len(invOfFitOut)):
			# invOfFitOut[i] = 1 / invOfFitOut[i]
		# for i in xrange(len(MADdistrOut)):
			# MADdistrOut[i] = 1 / MADdistrOut[i]
	
		plt.plot(weights, MADdistrOut, 'g.', weights, invOfFitOut, 'r', linewidth=1.0, markersize=2.0, markeredgewidth=0.0)
		plt.xlabel('($V_s$)')
		plt.ylabel('1 / MSD')
	
	plt.grid(True)
	plt.title('k = %g, $\sigma^2$ = %g, alpha = %g' % (k, variance, alpha))

	if graphFile:
		plt.savefig(graphFile, dpi = dpi)
	
	if showGraph:
		plt.show()
	
#------------------------------------------------------

def extractKFromVarFile(kFile, verbose = True, defaultSeed = 1.0):
	
	resultValue, varianceOk = stats.extractVariableFromInfoFile(varFile, varName = "K", defaultSeed = defaultSeed, verbose = verbose)
	
	return resultValue, varianceOk

#------------------------------------------------------
	
def idXVcal(idXVlist, k = 1.0, alpha = 1.0):
	
	idXVcal = []

	for row in idXVlist:
		
		id = row[0]
		x = row[1]
		v = row[2]
		vcal = getW_klibrate(v, k = k, alpha = alpha)
		
		idXVcal.append([id, x, vcal])
	
	return idXVcal
	
#------------------------------------------------------

def printHelp(version):
	
	# add alpha constant
	
	print """
Klibrate %s is a program made in the Jesus Vazquez Cardiovascular Proteomics
Lab at Centro Nacional de Investigaciones Cardiovasculares, used to perform the
calibration of experimental data, as a first step to integrate these data into
higher levels along with the SanXoT program.

To perform the calibration two parameters have to be calculated: the k (weight
constant), and the variance. They are calculated iteratively using the
Levenberg-Marquardt algorithm, starting from the seeds the user introduces
(it is possible to perform the calculation without the iterative calculation by
forcing both parameters with the -f option). In the integration that follows
the variance can be recalculated.

Klibrate needs two input files:

     * the original data file, containing unique identifiers of each scan, such
     as "RawFile05.raw-scan19289-charge2" or "File05B_scannumber12877_z3", the
     Xi which corresponds to the log2(A/B), and the Vi which corresponds to the
     weight of the measure).

     * the relations file, containing a first column with the higher level
     identifiers (such as the peptide sequence, for example "CGLAGCGLLK", or
     the protein, if you wish to directly integrate scans into proteins, such
     as the Uniprot Accession Numbers "P01308" or KEGG Gene ID "hsa:3630"), and
     the lower level identifiers within the abovementioned original data file
     (such as "RawFile05.raw-scan19289-charge2").

And delivers the output calibrated file:

     * the calibrated data file, containing the same information as the
     original data file, but changing the values of the third column
     (containing the weights) to adapt the information to the calibrated
     weights that can be used as input in the SanXoT program.



Usage: klibrate.py [OPTIONS] -r[relations file] -d[original data file] -o[calibrated output file]

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the data
                       file.
   -b, --no-verbose       Do not print result summary after executing.
   -d, --datafile      Input data file with text identificators in the first
                       column, measured values (x) in the second column, and
                       uncalibrated weights (v) in the third column.
   -D, --outgraphdata=filename
                       To use a non-default name for the data used to create
                       calibration graph files.
   -f, --forceparameters
                       Use the parameters (k and variance) as provided, without
                       using the Levenberg-Marquardt algorithm.
   -g, --no-showgraph  Do not show the rank(V) vs 1 / MSD graph after
                       the calculation.
   -G, --outgraphvvalue=filename
                       To use a non-default name for the graph file which shows
                       the value of V (the weight) versus 1 / MSD.
   -k, --kseed         Seed for the weight constant. Default is k = 1.
   -K, --kfile=filename
                       Get the K value from a text file. It must contain a line
                       (not more than once) with the text "K = [float]". This
                       suits the info file from another integration (see -L).
   -L, --infofile=filename
                       To use a non-default name for the info file.
   -m, --maxiterations Maximum number of iterations performed by the Levenberg-
                       Marquardt algorithm to calculate the variance and the k
                       constant. If unused, the default value of the algorithm
                       is taken.
   -o, --outputfile    To use a non-default output calibrated file name (see
                       above for more information on this file).
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the input folder.
   -r, --relfile, --relationsfile
                       Relations file, with identificators of the higher level
                       in the first column, and identificators of the lower
                       level in the second column.
   -R, --outgraphvrank=filename
                       To use a non-default name for the graph file which shows
                       the rank of V (the weight) versus 1 / MSD.
   -s, --no-showsteps  Do not print result summary and steps of each Levenberg-
                       Marquardt iteration.
   -v, --var, --varianceseed
                       Seed used to start calculating the variance.
                       Default is 0.001.
   -V, --varfile=filename
                       Get the variance value from a text file. It must contain
                       a line (not more than once) with the text
                       "Variance = [double]". This suits the info file from
                       another integration (see -L).
   -w, --window        The amount of weight-ordered lower level elements
                       (scans, usually) that are taken at a time to calculate
                       the median of the weight, which is compared to the fit;
                       default is 200.


examples:

* To calculate the variance and k starting with a seed v = 0.03 and k = 40, printing the steps of the Levenberg-Marquardt algorithm and results, showing the rank(Vs) vs 1 / MSD graph afterwards:

klibrate.py -gbs -v0.03 -k40 -dC:\\temp\\originalDataFile.txt -rC:\\temp\\relationsFile.txt -oC:\\temp\\calibratedWeights.xls

* To get fast results of an integration forcing a variance = 0.02922 and a k = 35.28:

klibrate.py -f -v0.02922 -k35.28 -dC:\\temp\\originalDataFile.txt -rC:\\temp\\relationsFile.txt -oC:\\temp\\calibratedWeights.xls

* To see the graph resulting from a calculation with variance = 0.02922 and a k = 35.28:

klibrate.py -gf -v0.02922 -k35.28 -dC:\\temp\\originalDataFile.txt -rC:\\temp\\relationsFile.txt -oC:\\temp\\calibratedWeights.xls
""" % version

	return

#------------------------------------------------------

def main(argv):
	
	version = "v1.16"
	verbose = True
	showGraph = True
	graphDPI = 100 # default of Matplotlib's savefig method
	showSteps = True
	forceParameters = False
	kSeed = 1.0
	varianceSeed = 0.001
	alphaSeed = 1.0
	useCooperativity = False
	medianSide = 100
	maxIterations = 0
	dataFile = ""
	relationsFile = ""
	outputCalibrated = ""
	infoFile = ""
	kFile = ""
	kSeedProvided = False
	varFile = ""
	varianceSeedProvided = False
	graphFileVRank = ""
	graphFileVValue = ""
	graphDataFile = ""
	showRank = False
	analysisName = ""
	defaultAnalysisName = "klibrate"
	analysisFolder = ""
	logList = [["Klibrate " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]
	defaultDataFile = "data"
	defaultRelationsFile = "rels"
	defaultOutputInfo = "infoFile"
	defaultOutputGraphVRank = "outGraph_VRank"
	defaultOutputGraphVValue = "outGraph_VValue"
	defaultGraphDataFile = "outGraph_Data"
	defaultOutputCalibrated = "calibrated"
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	
	try:
		opts, args = getopt.getopt(argv, "a:p:k:v:c:d:r:o:w:m:L:G:D:R:K:V:bgsfh", ["analysis=", "folder=", "kseed=", "varianceseed=", "alphaseed=", "datafile=", "relfile=", "outputfile=", "window=", "maxiterations=", "infofile=", "outgraphvrank=", "outgraphvvalue=", "outgraphdata=", "kfile=", "varfile=", "no-verbose", "no-showgraph", "no-showsteps", "forceparameters", "showrank", "help", "egg", "easteregg"])
	except getopt.GetoptError:
		message = "Error while getting parameters."
		print message
		logList.append([message])
		# stats.saveFile(infoFile, logList, "INFO FILE")
		sys.exit(2)
		
	if len(opts) == 0:
		printHelp(version)
		sys.exit()
		
	for opt, arg in opts:
		if opt in ("-a", "--analysis"):
			analysisName = arg
		if opt in ("-p", "--place", "--folder"):
			analysisFolder = arg
		if opt in ("-k", "--kseed"):
			kSeed = float(arg)
			kSeedProvided = True
		elif opt in ("-v", "--var", "--varianceseed"):
			varianceSeed = float(arg)
			varianceSeedProvided = True
		elif opt in ("-c", "--alphaseed"):
			useCooperativity = True
			alphaSeed = float(arg)
		elif opt in ("-d", "--datafile"):
			dataFile = arg
		elif opt in ("-r", "--relfile", "--relationsfile"):
			relationsFile = arg
		elif opt in ("-o", "--outputfile"):
			outputCalibrated = arg
		elif opt in ("-w", "--window"):
			windowWidth = round(float(arg))
			if windowWidth % 2 == 0:
				windowWidth += 1
			medianSide = int((windowWidth - 1) / 2)
		elif opt in ("-b", "--no-verbose"):
			verbose = False
		elif opt in ("-g", "--no-showgraph"):
			showGraph = False
		elif opt in ("-s", "--no-showsteps"):
			showSteps = False
		elif opt in ("-m", "--maxiterations"):
			maxIterations = int(arg)
		elif opt in ("-L", "--infofile"):
			infoFile = arg
		elif opt in ("-G", "--outgraphvvalue"):
			graphFileVValue = arg
		elif opt in ("-D", "--outgraphdata"):
			graphDataFile = arg
		elif opt in ("-K", "--kfile"):
			kFile = arg
		elif opt in ("-V", "--varfile"):
			varFile = arg
		elif opt in ("-f", "--forceparameters"):
			forceParameters = True
		elif opt in ("-R", "--outgraphvrank"):
			graphFileVRank = arg
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("--egg", "--easteregg"):
			easterEgg()
			sys.exit()
	
	verbose = verbose or showSteps

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
	
	if len(relationsFile) == 0:
		relationsFile = os.path.join(analysisFolder, analysisName + "_" + defaultRelationsFile + defaultTableExtension)
	
	if len(os.path.dirname(relationsFile)) == 0:
		relationsFile = os.path.join(analysisFolder, relationsFile)
		
	if len(os.path.dirname(varFile)) == 0 and len(os.path.basename(varFile)) > 0:
		varFile = os.path.join(analysisFolder, varFile)
	
	if len(varFile) > 0 and not varianceSeedProvided:
		varianceSeed, varianceOk = stats.extractVarianceFromVarFile(varFile, verbose = verbose, defaultSeed = varianceSeed)
		if not varianceOk:
			logList.append(["Variance not found in text file"])
			stats.saveFile(infoFile, logList, "INFO FILE")
			sys.exit()
			
	if len(os.path.dirname(kFile)) == 0 and len(os.path.basename(kFile)) > 0:
		kFile = os.path.join(analysisFolder, kFile)
	
	if len(kFile) > 0 and not kSeedProvided:
		kSeed, KOk = stats.extractKFromKFile(kFile, verbose = verbose, defaultSeed = kSeed)
		if not KOk:
			logList.append(["K not found in text file."])
			stats.saveFile(infoFile, logList, "INFO FILE")
			sys.exit()
		
	# output
	if len(outputCalibrated) == 0:
		outputCalibrated = os.path.join(analysisFolder, analysisName + "_" + defaultOutputCalibrated + defaultTableExtension)
	else:
		if len(os.path.dirname(outputCalibrated)) == 0:
			outputCalibrated = os.path.join(analysisFolder, outputCalibrated)
	
	if len(graphFileVRank) == 0:
		graphFileVRank = os.path.join(analysisFolder, analysisName + "_" + defaultOutputGraphVRank + defaultGraphExtension)
	
	if len(graphFileVValue) == 0:
		graphFileVValue = os.path.join(analysisFolder, analysisName + "_" + defaultOutputGraphVValue + defaultGraphExtension)
	
	if len(graphDataFile) == 0:
		graphDataFile = os.path.join(analysisFolder, analysisName + "_" + defaultGraphDataFile + defaultTableExtension)
	
	if len(infoFile) == 0:
		infoFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputInfo + defaultTextExtension)
		
	logList.append(["Variance seed = " + str(varianceSeed)])
	logList.append(["K seed = " + str(kSeed)])
	if useCooperativity: logList.append(["Alpha seed = " + str(alphaSeed)])
	logList.append(["Input data file: " + dataFile])
	logList.append(["Input relations file: " + relationsFile])
	logList.append(["Output calibrated file: " + outputCalibrated])
	logList.append(["Output info file: " + infoFile])
	logList.append(["Output V rank graph file: " + graphFileVRank])
	logList.append(["Output V graph file: " + graphFileVValue])
	logList.append(["Output data file for graph: " + graphDataFile])
	logList.append(["Parameters forced: " + str(forceParameters)])
	logList.append(["Max iterations: " + str(maxIterations)])
	
# END REGION: FILE NAMES SETUP
	
	calibratedData, variance, k, alpha, extraLog = calibrate(rawDataFile = dataFile,
		relationsFile = relationsFile, kSeed = kSeed, varianceSeed = varianceSeed,
		medianSide = medianSide, maxIterations = maxIterations, verbose = showSteps,
		showGraph = showGraph, forceParameters = forceParameters, alphaSeed = alphaSeed,
		showRank = showRank, useCooperativity = useCooperativity, graphFileVRank = graphFileVRank, graphFileVValue = graphFileVValue, graphDataFile = graphDataFile, graphDPI = graphDPI)
	
	logList.extend(extraLog)
	
	if not calibratedData:
		if len(infoFile) > 0:
			stats.saveFile(infoFile, logList, "INFO FILE")
		sys.exit()
	
	if len(outputCalibrated) > 0:
		stats.saveFile(outputCalibrated, calibratedData, "id\tX\tVcal")
	
	logList.append([])
	logList.append(["K = " + str(k)])
	logList.append(["Variance = " + str(variance)])
	if useCooperativity: logList.append(["Alpha = " + str(alpha)])
	
	if len(infoFile) > 0:
		stats.saveFile(infoFile, logList, "INFO FILE")
	
	if verbose:
		print
		print "*** results ***"
		print "k = " + str(k)
		print "variance = " + str(variance)
		if useCooperativity: print "alpha = " + str(alpha)
		print
		print "Output calibrated file in: " + outputCalibrated
		print "Graph with rank of V in: " + graphFileVRank
		print "Graph with value of V in: " + graphFileVValue
		print "Info file in: " + infoFile
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])