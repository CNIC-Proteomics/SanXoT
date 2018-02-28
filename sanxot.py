import pdb
import sys
import getopt
import stats
import operator
import os
import random
from scipy.stats import norm
from numpy import *
from scipy.optimize import leastsq
from time import strftime
from datetime import datetime

import pprint
pp = pprint.PrettyPrinter(indent=4)

#######################################################

class higherResult:
	def __init__(self, id2 = None, Xj = None, Vj = None):
		self.id2 = id2
		self.Xj = Xj
		self.Vj = Vj
		
#------------------------------------------------------

class lowerResult:
	def __init__(self, id1 = None, XiXj = None, Wij = None, Vi = None):
		self.id1 = id1
		self.XiXj = XiXj
		self.Wij = Wij
		self.Vi = Vi
		
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
	def __init__(self, id2 = None, Xj = None, Vj = None, id1 = None, Xi = None, Vi = None, Wij = None, nij = None, Zij = None, FDRij = None, tags = ""):
		self.id2 = id2
		self.Xj = Xj
		self.Vj = Vj
		self.id1 = id1
		self.Xi = Xi
		self.Vi = Vi
		self.Wij = Wij
		self.nij = nij
		self.Zij = Zij
		self.absZij = None # used only for sorting
		self.FDRij = FDRij
		self.tags = tags

#------------------------------------------------------

def varDiff(params,
			inputRawData,
			inputRelations,
			verbose = False,
			forHtml = False,
			logResults = None,
			acceptedError = 0.001,
			removeDuplicateUpper = False):

	MADconstant = 1.48260221850560 # *** 1 / DISTR.NORM.ESTAND.INV(3 / 4) get exact number
	
	varianceSeed = params[0]
	
	inputRawData.sort()
	inputRelations.sort()
	
	nextIdXData = getNextIdX_sanxot(inputRawData, inputRelations, variance = varianceSeed, giveMergedData = True, removeDuplicateUpper = removeDuplicateUpper)
	
	nextIdX = nextIdXData[0]
	mergedData = nextIdXData[1]
	
	newlist = []
	for orow in nextIdX:
		sequence = orow[0]
		# if sequence == "R.VNQAIALLTIGAR.E":
		# it is important to avoid sorting to keep it fast
		# so in next line do not foget sort = False
		# this should be sorted in the beginnig
		scanListWithSequence = stats.filterByElement(mergedData, sequence, sort = False)

		if len(scanListWithSequence) > 1: # otherwise Xi = Xj --> Xi - Xj = 0 --> does not work
			for scanRow in scanListWithSequence:
				newrow = []
				weight = scanRow[4] # the W (weight taking into account the variance)
				degreesOfFreedom = len(scanListWithSequence)
				gs = float(degreesOfFreedom) / (float(degreesOfFreedom) - 1.0)
				XiXj = scanRow[2] - orow[1]
				Fi = gs * weight * (XiXj ** 2)
				newrow.append(sequence) # sequence --> 0
				newrow.append(scanRow[1]) # scan number --> 1
				newrow.append(XiXj) # Xi - Xj --> 2
				newrow.append(weight) # weight --> 3
				newrow.append(len(scanListWithSequence)) # degrees of freedom --> 4
				newrow.append(Fi) # Fi distribution --> 5
				
				newlist.append(newrow)

	variance = (MADconstant ** 2) * stats.medianByIndex(newlist, index = 5)

	printLine = "seed = " + str(varianceSeed) + ", sigma2 = " + str(variance)
	logResults.append([printLine])
	
	if verbose:
		print printLine
	
	if forHtml: print "</br>"
	
	return asarray([fabs(variance - 1.0)])

#------------------------------------------------------

def integrate(data = None,
				relations = None,
				dataFile = "",
				relationsFile = "",
				varianceSeed = 0.001,
				maxIterations = 0,
				verbose = False,
				showGraph = False,
				forceParameters = False,
				forceEvenNegativeVariance = False,
				giveAllResults = True,
				forHtml = False,
				randomiseRelfile = False,
				confluenceRelfile = False,
				randomisedFileName = "",
				confluencedFileName = "",
				acceptedError = 0.001,
				minVarianceSeed = 1e-3,
				removeDuplicateUpper = False,
				forceEmergencyVariance = False,
				emergencySweep = False,
				sweepDecimals = 3,
				includeOrphans = False,
				tags = ""):

	logResults = []
	outStats = []
	outStatsExcluded = []
	lowerNormExcluded = []
	higherOrphanList = []
	
	filteredRelations = None
	relationsExcluded = None
	varianceSeedOriginal = varianceSeed
	
	if data == None:
		if len(dataFile) == 0:
			print "Error: no input data"
			if forHtml: print "</br>"
			sys.exit()
		else:
			data = stats.loadInputDataFile(dataFile)
	
	if relations == None:
		if len(relationsFile) == 0:
			if not confluenceRelfile:
				print "Error: no relations file"
				if forHtml: print "</br>"
				sys.exit()
			else: # then means a confluence is made from the data file, getting ids from column 0 (first)
				idsForConfluence = stats.extractColumns(data, 0)
				relations = stats.getConfluenceList(idsForConfluence, deleteDuplicates = True)
				if len(confluencedFileName) > 0:
					stats.saveFile(confluencedFileName, relations, "idsup\tidinf")
		else:
			relations = stats.loadRelationsFile(relationsFile)
			if confluenceRelfile: # this means a confluence is made from the relations file, getting ids from column 1 (second)
				idsForConfluence = stats.extractColumns(relations, 1)
				relations = stats.getConfluenceList(idsForConfluence, deleteDuplicates = True)
				if len(confluencedFileName) > 0:
					stats.saveFile(confluencedFileName, relations, "idsup\tidinf")
	
	if len(tags) > 0:
		filteredRelations, relationsExcluded = stats.filterRelations(relations, tags)
	else:
		filteredRelations = relations
		relationsExcluded = []
	
	if randomiseRelfile:
		filteredRelations = stats.getRandomList(filteredRelations)
		if len(randomisedFileName) > 0:
			stats.saveFile(randomisedFileName, filteredRelations, "idsup\tidinf")

	if filteredRelations == None and len(filteredRelations) == 0:
		print "Error: no relations data"
		if forHtml: print "</br>"
		sys.exit()
	
	success = True
	if forceParameters:
		if varianceSeed < 0 and not forceEvenNegativeVariance:
			# informing the used about forced negative variance being corrected to zero
			message = "Since variance is negative, it will be reset to zero.\nOriginal forced variance was %s." % str(varianceSeed)
			logResults.extend([[], [message], []])
			print
			if forHtml: print "</br>"
			print message
			if forHtml: print "</br>"
			print
			if forHtml: print "</br>"
			varianceSeed = 0
			
		variance = varianceSeed
	else:
		success = False
		stopAnyway = False
		iterationCounter = 0
		tries = 0
		
		while not (success or stopAnyway):
			tries += 1
			bestSol, cov, infodict, mesg, ier = leastsq(varDiff, varianceSeed, args = (data, filteredRelations, verbose, forHtml, logResults, acceptedError, removeDuplicateUpper), maxfev = maxIterations, full_output = True)
			variance = bestSol[0]
		
			LMError = fabs(infodict["fvec"][0])
			numberOfCalls = infodict["nfev"]
			iterationCounter += numberOfCalls
			
			if LMError < acceptedError:
				success = True
			else:
			
				if maxIterations > 0 and iterationCounter >= maxIterations and not success:
					stopAnyway = True
					message = "After %i iterations, the Levenberg-Marquardt algorithm was unable to find a solution" % iterationCounter
					logResults.extend([[], [message], []])
					print
					if forHtml: print "</br>"
					print message
					if forHtml: print "</br>"
					print
					if forHtml: print "</br>"
				
				if not stopAnyway:
					firstCalc = True
					while firstCalc or varianceSeed < -0.03:
						# -0.03 is a value that has proven not to give problems when seed is above it
						# seed below (about) -0.03 have shown to make the LM algorithm collapse,
						# giving values incrementally big in each iteration, instead of approaching the solution
						# it has to be tested further, anyway
						
						firstCalc = False
						if abs(varianceSeed) <= minVarianceSeed or str(varianceSeed) == "nan":
							varianceSeed = random.random() - 0.5
						else:
							varianceSeed = varianceSeed * 4 * (random.random() - 0.5)
					
					
					message = "Solution did not converge, retrying with variance seed = %f" % varianceSeed
					logResults.extend([[], [message], []])
					print
					if forHtml: print "</br>"
					print message
					if forHtml: print "</br>"
					print
					if forHtml: print "</br>"
				
		if success:
			message = "Solution found with variance seed = %f, after %i iterations and %i tries" % (varianceSeed, iterationCounter, tries)
			logResults.extend([[], [message], []])
			print
			if forHtml: print "</br>"
			print message
			if forHtml: print "</br>"
			print
			if forHtml: print "</br>"
		else:
			message = "SOLUTION *NOT* FOUND, after %i iterations and %i tries" % (iterationCounter, tries)
			logResults.extend([[], [message], []])
			print
			if forHtml: print "</br>"
			print message
			if forHtml: print "</br>"
			print
			if forHtml: print "</br>"
			
			if emergencySweep:
				stepsTakenEachSide = 10
				bestVariance = 0.0
				leastDif = sys.float_info.max
				
				message = "Performing sweep to get best variance upto %i decimals" % sweepDecimals
				logResults.extend([[], [message], []])
				print
				print message
				print
				
				for decimal in range(sweepDecimals + 1):
					startVariance = bestVariance
					for sweepTry in range(stepsTakenEachSide * 2):
						varianceTry = startVariance + (sweepTry - stepsTakenEachSide) * 10.0**(-decimal)
						params = [varianceTry]
						
						varianceDifference = varDiff(params, data, filteredRelations, verbose = False, logResults = logResults)
						message = "Variance difference when sweeping with variance %f -> %f." % (varianceTry, varianceDifference)
						logResults.extend([[message]])
						if verbose:
							print message
						
						if varianceDifference < leastDif:
							leastDif = varianceDifference
							bestVariance = varianceTry
				
				variance = bestVariance
				message = "After sweeping, the best variance found was: %f.\nForcing this variance, as requested by user." % variance
				logResults.extend([[], [message], []])
				print
				print message
				print
				
				success = True

			if forceEmergencyVariance and not emergencySweep:
				message = "Forcing seed variance %f as emergency variance, as requested by user" % varianceSeed
				logResults.extend([[], [message], []])
				print
				print message
				print
				
				variance = varianceSeedOriginal
				success = True
				
		if success and not forceEvenNegativeVariance and variance < 0:
			message = "Calculated variance was %s.\nSince variance is negative, it will be reset to zero." % str(variance)
			logResults.extend([[], [message], []])
			print message
			print
			
			variance = 0
			
	if giveAllResults:
		mergedData = stats.getIdXW(data, filteredRelations, variance, giveMergedData = True, removeDuplicateUpper = removeDuplicateUpper)[1]
		higherLevel, outStats, lowerNorm = makeStats(variance = variance, input = mergedData)
		
		if len(relationsExcluded) > 0:
			outStatsExcluded, lowerNormExcluded, higherOrphanList = calculateExcluded(relationsExcluded, outStats, data, variance, includeOrphans)
			message = "Total elements excluded using tags: %i (of %i)" % (len(relationsExcluded), len(relationsExcluded) + len(outStats))
			logResults.extend([[message], []])

		outStats += outStatsExcluded
		lowerNorm += lowerNormExcluded
		higherLevel += higherOrphanList
		
		return variance, higherLevel, outStats, lowerNorm, logResults, success
	
	else:
		
		return variance, logResults, success

#------------------------------------------------------

# def sortByZij(list):
	
	# newList = []
	
	# for element in list:
		# if str(element.Zij).lower() == "nan":
			# # trick used, because the sort method has a bug with nans
			# element.FDRij = sys.float_info.max
		# else:
			# element.FDRij = fabs(element.Zij)

	# outputStats = stats.sortByInstance(outputStats, "FDRij")
	
	# for element in list:
		# if 

	# return newList
#------------------------------------------------------

def calculateExcluded(relsExcludedOriginal,
						statsOriginal,
						dataOriginal,
						variance,
						includeOrphans = False,
						orphanTag = "orphan"):

	outStatsExcluded = []
	lowerNormExcluded = []
	statsIncluded = statsOriginal[:]
	relsExcluded = relsExcludedOriginal[:]
	txtExcluded = "excluded"
	txtPending = "pending"
	
	statsIncluded = stats.sortByInstance(statsIncluded, "id2")
	dataOriginal = stats.sortByIndex(dataOriginal, 0)[:]
	relsExcluded = stats.sortByIndex(relsExcluded, 0, 1)[:]
	
	relIdSup = ""
	selectionStats = []
	higherOrphanList = []
	higherOrphanAdded = False
	
	for relExcluded in relsExcluded:
		selectionData = stats.filterByElement(dataOriginal, relExcluded[1], sort = False)
		if len(selectionData) > 0:
			
			if relExcluded[0] != relIdSup:
				relIdSup = relExcluded[0]
				selectionStats = [x for x in statsIncluded if x.id2 == relIdSup]
				higherOrphan = []
				higherOrphanAdded = False
				
			if len(selectionStats) == 0:
			# whole inferior level of a superior element excluded using tags

				if not includeOrphans:
					relInOutStats = statsResult(
								id2 = relExcluded[0], # idsup
								Xj = txtExcluded, # Xsup
								Vj = txtExcluded, # Vsup
								id1 = relExcluded[1], # idinf
								Xi = selectionData[0][1], # Xinf
								Vi = selectionData[0][2], # Vinf
								nij = 0, # n
								Zij = txtExcluded, # Z calculation few lines below
								FDRij = txtExcluded) # FDR not calculable
								
					relInLowerNorm = lowerResult(
								id1 = relExcluded[1], # idinf
								XiXj = txtExcluded, # X'inf = Xinf - Xsup
								Vi = relInOutStats.Vi, # Vinf
								Wij = txtExcluded) # Winf
				else:
					# include orphans
					
					# then, the stats are not taken from included data (statsIncluded),
					# but from anything pointing to the higher level element (relsExcluded)
					
					relExcluded = stats.addTagToRelations([relExcluded], [relExcluded], orphanTag)[0]
					relsOrphan = [x for x in relsExcluded if x[0] == relIdSup]
					
					# integrate dataOriginal using relsOrphan
					if not higherOrphan and not higherOrphanAdded:
						mergedOrphans = stats.getIdXW(dataOriginal, relsOrphan, variance, giveMergedData = True, removeDuplicateUpper = True)[1]
						higherOrphan, outStatsOrphan, lowerNormOrphan = makeStats(variance = variance, input = mergedOrphans)
					
					relInOutStats = statsResult(
								id2 = relExcluded[0], # idsup
								Xj = higherOrphan[0].Xj, # Xsup
								Vj = higherOrphan[0].Vj, # Vsup
								id1 = relExcluded[1], # idinf
								Xi = selectionData[0][1], # Xinf
								Vi = selectionData[0][2], # Vinf
								nij = 0, # n
								Zij = txtExcluded, # Z calculation few lines below
								FDRij = txtExcluded) # FDR not calculable
								
					relInLowerNorm = lowerResult(
								id1 = relExcluded[1], # idinf
								XiXj = relInOutStats.Xi - relInOutStats.Xj, # X'inf = Xinf - Xsup
								Vi = relInOutStats.Vi, # Vinf
								Wij = getW_sanxot(relInOutStats.Vi, variance)) # Winf
								
					higherOrphanForList = higherResult(
								id2 = higherOrphan[0].id2, # idsup
								Xj = higherOrphan[0].Xj, # Xsup
								Vj = higherOrphan[0].Vj) #Vsup

			else:
				relInOutStats = statsResult(
							id2 = relExcluded[0], # idsup
							Xj = selectionStats[0].Xj, # Xsup
							Vj = selectionStats[0].Vj, # Vsup
							id1 = relExcluded[1], # idinf
							Xi = selectionData[0][1], # Xinf
							Vi = selectionData[0][2], # Vinf
							nij = selectionStats[0].nij, # n
							Zij = txtPending, # Z calculation few lines below
							FDRij = txtExcluded) # FDR not calculable
							
				relInLowerNorm = lowerResult(
							id1 = relExcluded[1], # idinf
							XiXj = relInOutStats.Xi - relInOutStats.Xj, # X'inf = Xinf - Xsup
							Vi = relInOutStats.Vi, # Vinf
							Wij = getW_sanxot(relInOutStats.Vi, variance)) # Winf
				
				relInOutStats.Zij = getZ(relInLowerNorm.XiXj, relInLowerNorm.Wij, relInOutStats.nij)
				
			if len(relExcluded) > 2:
				relInOutStats.tags = relExcluded[2] # tags, otherwise, tags = ""
			
			outStatsExcluded.append(relInOutStats)
			lowerNormExcluded.append(relInLowerNorm)
			if higherOrphan and not higherOrphanAdded:
				higherOrphanList.append(higherOrphanForList)
				higherOrphanAdded = True
				
	return outStatsExcluded, lowerNormExcluded, higherOrphanList


#------------------------------------------------------

def printErrorFileMissing(file = "file", argument = None):

	print
	print "Error: file name for " + file + " is missing."
	if argument != None:
		print "Use " + argument + " for this parameter (using the short path)."
	print "Use -h for help."
	sys.exit()

#------------------------------------------------------

def getNextIdX_sanxot(idXVall, relations, variance = 0.0, giveMergedData = False, removeDuplicateUpper = False):
	
	idX = []
	
	# no need to sort: mergeInput will do it anyway
	# idXVall.sort()
	# relations.sort()

	idXVWall = addW_sanxot(idXVall, variance)
	
	mergedData = stats.mergeInput(idXVWall, relations, removeDuplicateUpper = removeDuplicateUpper)
	
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

def makeStats(variance = 0.0, inputFile = "", input = None):

	# input here is in the format id2-id1-XV
	outputHigher = []
	outputLower = []
	outputStats = []
	element = []
	# pdb.set_trace()
	# ***
	if not input:
		if len(inputFile) == 0:
			print 'Error: no input file'
			sys.exit()
		
		input = loadFile(inputFile)
	
	for row in input:
		id2 = row[0]
		if len(element) == 0 or id2 == list(element[0])[0]:
			# while the id2 is the same, the id1's keep adding up to element
			element.append(row)
		else:
			# when the list of id1's within an id2 is complete, then...
			statsResults, higherResult, lowerResults = getAverage(element, variance)

			for i in xrange(len(statsResults)):
				statsResults[i].nij = len(element) # degrees of freedom
				statsResults[i].Zij = getZ(lowerResults[i].XiXj, lowerResults[i].Wij, statsResults[i].nij)
						
			outputHigher.append(higherResult)
			outputLower.extend(lowerResults)
			outputStats.extend(statsResults)
			element = []
			element.append(row)

	####################
	# calculate the last row after exiting the for
	
	statsResults, higherResult, lowerResults = getAverage(element, variance)

	for i in xrange(len(statsResults)):
		statsResults[i].nij = len(element) # degrees of freedom
		statsResults[i].Zij = getZ(lowerResults[i].XiXj, lowerResults[i].Wij, statsResults[i].nij)

	####################
	
	outputHigher.append(higherResult)
	outputLower.extend(lowerResults)
	outputStats.extend(statsResults)
	outputStats = addFDR(outputStats)
	
	# outputHigher.sort()
	sorted(outputHigher, key=lambda higherResult: higherResult.id2)
	# outputHigher.sort(key=operator.attrgetter('id2'))
	
	return outputHigher, outputStats, outputLower

#------------------------------------------------------

def addFDR(statsList):

	# calculate FDRij
	# order by abs(Zij)
		
	for row in statsList:
		if str(row.Zij).lower() == "nan":
			# trick used, because the sort method has a bug with nans
			row.absZij = None
		else:
			row.absZij = fabs(row.Zij)
	statsList = stats.sortByInstance(statsList, "absZij", isDescendent = True)


	totN = 0
	for statsResult in statsList:
		if statsResult.absZij != None: totN += 1
		
	rank = 1
	for i in [x for x in xrange(len(statsList))]:
			
		if statsList[i].absZij != None:
			statsList[i].FDRij = 2 * (1 - norm.cdf(statsList[i].absZij)) / (float(rank) / float(totN))
			rank += 1
		else:
			statsList[i].FDRij = float("nan")
		# if statsList[i].id2 == "C@ASQVGMTAPGTR": pdb.set_trace()
			
	return statsList

#------------------------------------------------------

def getAverage(chunk, variance1 = 0.0):
	
	# chunk should be in the form id2-id1-XV
	
	statsResults = []
	lowerResults = []
	id2 = chunk[0][0]
	
	higherElement = higherResult(id2 = id2)
	sumXW = 0
	sumW = 0
	
	# higherElement.append(chunk[0][0]) # 0
	# this copies the unificating field,
	# for example, the sequences, if we are integrating
	# spectra into peptides
	for bit in chunk:
		statsElement = statsResult(id2 = id2, id1 = bit[1])
		lowerElement = lowerResult(id1 = bit[1])
		
		x1 = bit[2]
		v1 = bit[3]
		w1 = getW_sanxot(v1, variance1)
		sumXW = sumXW + x1 * w1
		sumW = sumW + w1

		statsElement.Xi = x1
		statsElement.Vi = v1
		if len(bit) > 4: statsElement.tags = bit[4]
		lowerElement.Wij = w1
		lowerElement.XiXj = x1 # fixed a few lines ahead
		lowerElement.Vi = v1
		statsResults.append(statsElement)
		lowerResults.append(lowerElement)
	
	x2 = sumXW / sumW
	totW = sumW
	
	v2 = totW
	
	higherElement.Xj = x2 # 1
	higherElement.Vj = v2 # 2
	
	for statsRes in statsResults:
		statsRes.Xj = higherElement.Xj
		statsRes.Vj = higherElement.Vj
		
	for element in lowerResults:
		element.XiXj -= higherElement.Xj # I told you it was going to be fixed

	return statsResults, higherElement, lowerResults
	
#------------------------------------------------------

def addW_sanxot(idXVlist, variance = 0.0):
	
	idXVWlist = []
	
	for row in idXVlist:
		
		id = row[0]
		x = row[1]
		v = row[2]
		w = getW_sanxot(v, variance)
		
		idXVWlist.append([id, x, v, w])
	
	return idXVWlist

#------------------------------------------------------

def getW_sanxot(v, variance):

	w = 1 / ((1 / v) + variance)
	return w

#------------------------------------------------------

def getZ(x, w, n):

	if n > 1:
		gs = float(n) / (float(n - 1.0))
		z = x * sqrt(w * gs)
	else:
		z = float("nan")
	
	return z
	
#------------------------------------------------------

def randomData(data = None, variance = 0):
	
	newData = []
	for row in data:
		id = row[0]
		v = row[2]
		w = 1 / (variance + 1 / v)
		localVariance = 1 / math.sqrt(w)
		newX = localVariance * norm.ppf(random.random())
		newData.append([id, newX, v])
	
	return newData

#------------------------------------------------------

def getVarConf(variance,
				dataFile,
				relationsFile,
				totSimulations,
				varConfLimit = 0.05,
				verbose = False,
				minVarianceSeed = 1e-3,
				maxIterations = 0,
				removeDuplicateUpper = False,
				acceptedError = 0.001,
				tags = ""):

	# fix this, so it is loaded once only
	data = stats.loadInputDataFile(dataFile)
	relations = stats.loadRelationsFile(relationsFile)
	
	indexUpper = int(min(math.ceil(totSimulations * (1 - varConfLimit)) - 1, totSimulations - 1))
	indexLower = int(max(math.floor(totSimulations * varConfLimit) - 1, 0))
	
	# use norm.ppf or similar
	
	# fix next
	varianceArray = []
	for simulation in xrange(totSimulations):
		
		print "Generating simulation #%i..." % simulation
		dataRnd = randomData(data, variance)

		print "Calculating variance for simulation #%i..." % simulation
		newVariance, higherLevel, outStats, lowerNorm, logResults, success = \
					integrate(data = dataRnd,
								relations = relations,
								varianceSeed = variance,
								maxIterations = maxIterations,
								verbose = verbose,
								forceParameters = False,
								acceptedError = acceptedError,
								minVarianceSeed = minVarianceSeed,
								removeDuplicateUpper = removeDuplicateUpper,
								tags = tags)
		print "New variance: %f" % newVariance
		print
		
		varianceArray.append(newVariance)
	
	varianceArray.sort()
	varMedian = stats.median(varianceArray)
	varUpper = varianceArray[indexUpper]
	varLower = varianceArray[indexLower]
	
	return varMedian, varLower, varUpper

#------------------------------------------------------
	
def printHelp(version = None, advanced = False):

	print """
SanXoT %s is a program made in the Jesus Vazquez Cardiovascular Proteomics
Lab at Centro Nacional de Investigaciones Cardiovasculares, used to perform
integration of experimental data to a higher level (such as integration from
peptide data to protein data), while determining the variance between them.

SanXoT needs two input files:

     * the lower level input data file, a tab separated text file containing
     three columns: the first one with the unique identifiers of each lower
     level element (such as "RawFile05.raw-scan19289-charge2" for a scan, or
     "CGLAGCGLLK" for a peptide sequence, or "P01308" for the Uniprot accession
     number of a protein), the Xi which corresponds to the log2(A/B), and the
     Vi which corresponds to the weight of the measure). This data have to be
     pre-calibrated with a certain weight (see help of the Klibrate program).

     * the relations file, a tab separated text file containing a first column
     with the higher level identifiers (such as the peptide sequence, a Uniprot
     accession number, or a Gene Ontology category) and the lower level
     identifiers within the abovementioned input data file.
     
     NOTE: you must include a first line header in all your files.

And delivers six output file:

     * the output data file for the higher level, which has the same format as
     the lower level data file, but containing the ids of the higher level in
     the first column, the ratio Xj in the second column, and the weight Vj in
     the third column. By default, this file is suffixed as "_higherLevel".
     
     * two lower level output files, containing three columns each: in both,
     the first column contains with the identifiers of the lower level, the
     second column contains the Xinf - Xsup (i.e. the ratios of the lower
     level, but centered for each element they belong to), and the third column
     is either the new weight Winf (contanining the variance of the
     integration) or the former untouched Vinf weight. For example, integrating
     from scan to peptide, these files would contain firstly the scan
     identifiers, secondly the Xscan - Xpep (the ratios of each scan compared
     to the peptide they are identifying) and either Wscan (the weight of the
     scan, taking into account the variance of the scan distribution) or Vscan.
     By default, these files are suffixed "_lowerNormW" and "_lowerNormV".
     
     * a file useful for statistics, containing all the relations of the higher
     and lower level element present in the data file, with a copy of their
     ratios X and weights V, followed by the number of lower elements contained
     in the upper element (for example, the number of scans that identify the
     same peptide), the Z (which is the distance in sigmas of the lower level
     ratio X to the higher level weighted average), and the FDR (the false
     discovery rate, important to keep track of changes or outliers). By
     default, this file is suffixed "_outStats".
     
     * an info file, containing a log of the performed integrations. Its last
     line is always in the form of "Variance = [double]". This file can be used
     as input in place of the variance (see -v and -V arguments). By default,
     this file is suffixed "_infoFile".
     
     * a graph file, depicting the sigmoid of the Z column which appears in the
     stats file, compared to the theoretical normal distribution. By default,
     this file is suffixed "_outGraph".
     
Usage: sanxot.py -d[data file] -r[relations file] [OPTIONS]""" % version

	if advanced:
		print """
   -h, --help          Display basic help and exit.
   -H, --advanced-help Display this help and exit.
   -A, --outrandom=filename
                       To use a non-default name for the randomised relations
                       file (only applicable when -R is in use).
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the data
                       file.
   -b, --no-verbose    Do not print result summary after executing.
   -C, --confluence    A modified version of the relations file is used, where
                       all the destination higher level elements are "1". If no
                       relations file is provided, the program gets the lower
                       level elements from the first column of the data file.
   -d, --datafile=filename
                       Data file with identificators of the lowel level in the
                       first column, measured values (x) in the second column,
                       and weights (v) in the third column.
   -D, --removeduplicateupper
                       When merging data with relations table, remove duplicate
                       higher level elements (not removed by default).
   -f, --forceparameters
                       Use the parameters as provided, without using the
                       Levenberg-Marquardt algorithm. Negative variances will
                       be reset to zero (see -F if you do not wish this).
   -F, --forcenegativevariance
                       Though the indirect calculation of variance may lead to
                       a negative value, this has no mathematical meaning and
                       may cause a number of artefacts; hence, by default,
                       negative variances are automatically reset to zero.
                       However, for some analyses, it might be important seeing
                       the effect of original variance; for these cases, use
                       this option to override resetting negative variances to
                       zero.
   -g, --no-graph      Do not show the Zij vs rank / N graph.
   -G, --outgraph=filename
                       To use a non-default name for the graph file.
   -J, --includeorphans
                       In the case all the lower elements pointing to a higher
                       level element are excluded, the default behaviour is
                       removing the higher level element altogether. Adding
                       this option, the lower level elements will be integrated
                       in any case.
   -l, --graphlimits=integer
                       To set the +- limits of the Zij graph (default is 6). If
                       you want the limits to be between the minimum and
                       maximum values, you can use -l.
   -L, --infofile=filename
                       To use a non-default name for the info file.
   -m, --maxiterations=integer
                       Maximum number of iterations performed by the Levenberg-
                       Marquardt algorithm to calculate the variance. If
                       unused, then the default value of the algorithm is
                       taken.
   -M, --minseed=float To use a non-default minimum seed. Default is 1e-3.
   -o, --higherlevel=filename
                       To use a non-default higher level output file name.
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the input folder.
   -r, --relfile, --relationsfile=filename
                       Relations file, with identificators of the higher level
                       in the first column, and identificators of the lower
                       level in the second column.
   -R, --randomise, --randomize
                       A modified version of the relations file is used, where
                       the higher level elements (first column) are replaced by
                       numbers and randomly written in the first column. The
                       numbers range from 1 to the total number of elements.
                       The second column (containing the lowel level elements)
                       remains unchanged.
   -s, --no-steps      Do not print result summary and the steps of every
                       Levenberg-Marquardt iteration.
   -t, --graphtitle=string
                       The graph title (default is
                       "Zij graph for sigma^2 = [variance]").
   -T, --minimalgraphticks
                       It will only show the x secondary line for x = 0, and
                       none for the Y axis (useful for publishing).
   -u, --lowernormw=filename
                       To use a non-default lower level output file name,
                       setting W as weight (default suffix is _lowerNormW).
   -U, --lowernormv=filename
                       To use a non-default lower level output file name,
                       setting V as weight (default suffix is _lowerNormV).
   -v, --var, --varianceseed=double
                       Seed used to start calculating the variance.
                       Default is 0.001.
   -V, --varfile=filename
                       Get the variance value from a text file. It must contain
                       a line (not more than once) with the text
                       "Variance = [double]". This suits the info file from
                       another integration (see -L).
   -W, --graphlinewidth=float
                       Use a non-default value for the sigmoid line width.
                       Default is 1.0.
   -w, --varconf=integer
                       Get the confidence limits of the variance using n
                       by performimg n simultaions.
   -y, --varconfpercent=float
                       Get the higher and lower limits to calculate the limits
                       of the variance (see -w). Default is 0.05.
   -z, --outstats=filename
                       To use a non-default stats file name.
   --emergencysweep    Use a sweep method instead of the Levenberg-Marquardt
                       algorithm if the number of tries (see -m) is reached.
                       Default number of decimals is 3, for different precision
                       use --sweepdecimals.
   --emergencyvariance In the case the maximum iterations are reached (see -m),
                       force the seed variance as emergency variance.
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
   --randomseed=float  The seed to be used in case the variance calculation
                       requires a random seed to be calculated (default is 0;
                       see also -m and --randomtimer).
   --randomtimer       When this is included, the hash of the current time is
                       used as seed in the case the variance requires a random
                       seed to be recalculated (see -m). If omitted, the seed
                       used is 0. Note --randomtimer overrides --randomseed.
                       For reproducibility, the hash of the time used is
                       included in the infoFile, so using --randomseed with
                       that value should give the exact same results.
   --sweepdecimals=float
                       The number of decimals up to which the variance will be
                       calculated if the maximum number of tries of the
                       Levenberg-Marquardt algorithm is reached (option -m),
                       and the --emergencysweep option is on. Default is 3.
   --xlabel=string     Use the selected string for the X label. Default is
                       "Zij". To remove the label, use --xlabel=" ".
   --ylabel=string     Use the selected string for the Y label. Default is
                       "Rank/N". To remove the label, use --ylabel=" ".

examples (use "sanxot.py" if you are not using the standalone version):

* To calculate the variance starting with a seed = 0.02, using a datafile.txt
and a relationsfile.txt, both in C:\\temp:

sanxot -dC:\\temp\\datafile.txt -rrelationsfile.txt -v0.02

* To get fast results of an integration forcing a variance = 0.02922:

sanxot -dC:\\temp\\datafile.txt -rrelationsfile.txt -f -v0.02922

* To get an integration forcing the variance reported in the info file at
C:\\data\\infofile.txt, and saving the resulting graph in C:\\data\\ instead
of C:\\temp\\:

sanxot -dC:\\temp\\datafile.txt -rrelationsfile.txt -f -VC:\\data\\infofile.txt -GC:\\data\\graphFile.png
"""
	else:
		print """
Use -H or --advanced-help for more details."""

	return

#------------------------------------------------------

def main(argv):

	# general
	version = "v2.13"
	
	# filename options
	analysisName = ""
	analysisFolder = ""
	dataFile = ""
	relationsFile = ""
	infoFile = ""
	outputLowerW = ""
	outputLowerV = ""
	outputHigher = ""
	outputStats = ""
	graphFile = ""
	varFile = ""
	outputRandomisedFile = ""
	outputConfluencedFile = ""
	
	# filename options - default filenames
	defaultAnalysisName = "sanxot"
	defaultDataFile = "data"
	defaultRelationsFile = "rels"
	defaultOutputHigher = "higherLevel"
	defaultOutputLowerW = "lowerNormW"
	defaultOutputLowerV = "lowerNormV"
	defaultOutputStats = "outStats"
	defaultOutputInfo = "infoFile"
	defaultOutputGraph = "outGraph"
	defaultOutputRandomisedFile = "outRandomRels"
	defaultOutputConfluencedFile = "outConfluRels"
	
	# filename options - file extensions
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	
	# console options
	verbose = True
	showSteps = True
	
	# graph options
	graphTitle = ""
	showGraph = True
	graphLimits = 6.0
	labelFontSize = 12
	graphLineWidth = 1.0
	xLabel = "Zij"
	yLabel = "Rank/N"
	minimalGraphTicks = False
	
	# variance calculation options
	varianceSeed = 0.001
	minVarianceSeed = 1e-3
	forceParameters = False
	forceEvenNegativeVariance = False
	forceEmergencyVariance = False
	emergencySweep = False
	sweepDecimals = 3
	varianceSeedProvided = False
	maxIterations = 0
	randomTimer = False
	randomSeed = 0
	
	# variance calculation options - confidence limits
	totSimulations = 0
	varConfLimit = 0.05
	
	# integration options
	tags = ""
	removeDuplicateUpper = False
	idXW = []
	randomiseRelfile = False
	confluenceRelfile = False
	includeOrphans = False
	
	# logfile variables
	logList = [["SanXoT " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]
	
	try:
		opts, args = getopt.getopt(argv, "a:p:v:d:r:o:u:z:m:M:l:L:G:V:A:B:w:y:t:W:Z:bgsfFRCDTJhH", ["analysis=", "folder=", "varianceseed=", "datafile=", "relfile=", "higherlevel=", "lowernormw=", "lowernormv=", "outstats=", "maxiterations=", "minseed=", "graphlimits=", "infofile=", "outgraph=", "outrandom=", "outconfluence=", "varconf=", "varconfpercent=", "graphtitle=", "graphlinewidth=", "labelfontsize=", "varfile=", "no-verbose", "no-graph", "no-steps", "forceparameters", "forcenegativevariance", "emergencyvariance", "emergencysweep", "sweepdecimals=", "randomise", "confluence", "removeduplicateupper", "help", "advanced-help", "minimalgraphticks", "includeorphans" , "randomtimer", "randomseed=", "xlabel=", "ylabel=", "tags="])
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
		elif opt in ("-o", "--higherlevel"):
			outputHigher = arg
		elif opt in ("-u", "--lowernormw"):
			outputLowerW = arg
		elif opt in ("-U", "--lowernormv"):
			outputLowerV = arg
		elif opt in ("-z", "--outstats"):
			outputStats = arg
		elif opt in ("-l", "--graphlimits"):
			graphLimits = float(arg)
		elif opt in ("-L", "--infofile"):
			infoFile = arg
		elif opt in ("-G", "--outgraph"):
			graphFile = arg
		elif opt in ("-A", "--outrandom"):
			outputRandomisedFile = arg
		elif opt in ("-B", "--outconfluence"):
			outputConfluencedFile = arg
		elif opt in ("-w", "--varconf"):
			totSimulations = int(arg)
		elif opt in ("-y", "--varconfpercent"):
			varConfLimit = float(arg)
		elif opt in ("-t", "--graphtitle"):
			graphTitle = arg
		elif opt in ("-V", "--varfile"):
			varFile = arg
		elif opt in ("-b", "--no-verbose"):
			verbose = False
		elif opt in ("-g", "--no-graph"):
			showGraph = False
		elif opt in ("-s", "--no-steps"):
			showSteps = False
		elif opt in ("-m", "--maxiterations"):
			maxIterations = int(arg)
		elif opt in ("-M", "--minseed"):
			minVarianceSeed = abs(float(arg))
		elif opt in ("-f", "--forceparameters"):
			forceParameters = True
		elif opt in ("--emergencyvariance"):
			forceEmergencyVariance = True
		elif opt in ("--emergencysweep"):
			emergencySweep = True
		elif opt in ("--sweepdecimals"):
			sweepDecimals = int(arg)
		elif opt in ("-F", "--forcenegativevariance"):
			forceParameters = True
			forceEvenNegativeVariance = True
		elif opt in ("-R", "--randomise", "--randomize"):
			randomiseRelfile = True
		elif opt in ("-W", "--graphlinewidth"):
			graphLineWidth = float(arg)
		elif opt in ("-Z", "--labelfontsize"):
			labelFontSize = float(arg)
		elif opt in ("-C", "--confluence"):
			confluenceRelfile = True
		elif opt in ("-D", "--removeduplicateupper"):
			removeDuplicateUpper = True
		elif opt in ("-T", "--minimalgraphticks"):
			minimalGraphTicks = True
		elif opt in ("-J", "--includeorphans"):
			includeOrphans = True
		elif opt in ("--randomtimer"):
			randomTimer = True
		elif opt in ("--randomseed"):
			randomSeed = float(arg)
		elif opt in ("--xlabel"):
			xLabel = arg
		elif opt in ("--ylabel"):
			yLabel = arg
		elif opt in ("--tags"):
			tags = arg
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("-H", "--advanced-help"):
			printHelp(version, advanced = True)
			sys.exit()

	# no randomising and confluencing at the same time
	if confluenceRelfile and randomiseRelfile:
		randomiseRelfile = False
	
	if not randomiseRelfile:
		outputRandomisedFile = ""
	
	if not confluenceRelfile:
		outputConfluencedFile = ""

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
	
	if len(relationsFile) == 0 and not confluenceRelfile:
		relationsFile = os.path.join(analysisFolder, analysisName + "_" + defaultRelationsFile + defaultTableExtension)
	
	if len(os.path.dirname(varFile)) == 0 and len(os.path.basename(varFile)) > 0:
		varFile = os.path.join(analysisFolder, varFile)
	
	if len(varFile) > 0 and not varianceSeedProvided:
		varianceSeed, varianceOk = stats.extractVarianceFromVarFile(varFile, verbose, varianceSeed)
		if not varianceOk:
			logList.append(["Variance not found in text file."])
			stats.saveFile(infoFile, logList, "INFO FILE")
			sys.exit()
			
	# output
	if len(outputHigher) == 0:
		outputHigher = os.path.join(analysisFolder, analysisName + "_" + defaultOutputHigher + defaultTableExtension)
	else:
		if len(os.path.dirname(outputHigher)) == 0:
			outputHigher = os.path.join(analysisFolder, outputHigher)
	
	if len(outputLowerW) == 0:
		outputLowerW = os.path.join(analysisFolder, analysisName + "_" + defaultOutputLowerW + defaultTableExtension)
	
	if len(outputLowerV) == 0:
		outputLowerV = os.path.join(analysisFolder, analysisName + "_" + defaultOutputLowerV + defaultTableExtension)
		
	if len(outputStats) == 0:
		outputStats = os.path.join(analysisFolder, analysisName + "_" + defaultOutputStats + defaultTableExtension)
		
	if len(infoFile) == 0:
		infoFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputInfo + defaultTextExtension)
		
	if len(graphFile) == 0:
		graphFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputGraph + defaultGraphExtension)
	else:
		if len(os.path.dirname(graphFile)) == 0:
			graphFile = os.path.join(analysisFolder, graphFile)
	
	if len(outputRandomisedFile) == 0 and randomiseRelfile:
		outputRandomisedFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputRandomisedFile + defaultTableExtension)

	if len(outputConfluencedFile) == 0 and confluenceRelfile:
		outputConfluencedFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputConfluencedFile + defaultTableExtension)

	if len(os.path.dirname(relationsFile)) == 0 and not confluenceRelfile:
		relationsFile = os.path.join(analysisFolder, relationsFile)

	if len(os.path.dirname(outputStats)) == 0 and not confluenceRelfile:
		outputStats = os.path.join(analysisFolder, outputStats)
	
	if randomTimer: randomSeed = datetime.now()
	randomSeedUsed = abs(hash(randomSeed))
	random.seed(randomSeedUsed)
	
	logList.append(["Variance seed = " + str(varianceSeed)])
	logList.append(["Input data file: " + dataFile])
	logList.append(["Input relations file: " + relationsFile])
	logList.append(["Output higher file: " + outputHigher])
	logList.append(["Output lower file (with W weight): " + outputLowerW])
	logList.append(["Output lower file (with V weight): " + outputLowerV])
	logList.append(["Output stats file: " + outputStats])
	logList.append(["Output info file: " + infoFile])
	logList.append(["Output graph file: " + graphFile])
	logList.append(["Parameters forced: " + str(forceParameters)])
	logList.append(["Max iterations: " + str(maxIterations)])
	logList.append(["Removing duplicate higher level elements: " + str(removeDuplicateUpper)])
	logList.append(["Tags to filter relations: " + tags])
	logList.append(["Include orphans: " + str(includeOrphans)])
	logList.append(["Random seed using timer: " + str(randomTimer)])
	logList.append(["Random seed used (abs(hash(randomseed))): " + str(randomSeedUsed)])
	
	# pp.pprint(logList)
	# sys.exit()

# END REGION: FILE NAMES SETUP
	
	sweepDecimals = min(50, max(1, sweepDecimals))
	
	if varConfLimit > 0.5: varConfLimit = 0.5
	if varConfLimit < 0: varConfLimit = 0
	
	if confluenceRelfile:
		logList.append(["Relations converted into confluence."])
		logList.append(["Output confluenced file: " + outputConfluencedFile])
	
	if randomiseRelfile:
		logList.append(["Relations randomised."])
		logList.append(["Output randomised file: " + outputRandomisedFile])
	
	verbose = verbose or showSteps

	logList.append([])

	if not forceParameters: logList.append(["Starting Levenberg-Marquardt, showing steps:"])
	else: logList.append(["Variance forced, no Levenberg-Marquardt optimisation performed."])
	variance, higherLevel, outStats, lowerNorm, logResults, success = \
				integrate(dataFile = dataFile,
							relationsFile = relationsFile,
							varianceSeed = varianceSeed,
							maxIterations = maxIterations,
							verbose = showSteps,
							forceParameters = forceParameters,
							forceEvenNegativeVariance = forceEvenNegativeVariance,
							forceEmergencyVariance = forceEmergencyVariance,
							randomiseRelfile = randomiseRelfile,
							confluenceRelfile = confluenceRelfile,
							randomisedFileName = outputRandomisedFile,
							confluencedFileName = outputConfluencedFile,
							acceptedError = 0.001,
							minVarianceSeed = minVarianceSeed,
							removeDuplicateUpper = removeDuplicateUpper,
							emergencySweep = emergencySweep,
							sweepDecimals = sweepDecimals,
							includeOrphans = includeOrphans,
							tags = tags)
	if logResults: logList.extend(logResults)

	higherTable = []
	for element in higherLevel:
		higherTable.append([element.id2, element.Xj, element.Vj])
	higherTableNoDuplicates = stats.removeDuplicates(higherTable[:])
	
	statsTable = []
	for element in outStats:
		statsTable.append([element.id2, element.Xj, element.Vj, element.id1, element.Xi, element.Vi, element.nij, element.Zij, element.FDRij, element.tags])
		
	lowerWTable = []
	lowerVTable = []
	for element in lowerNorm:
		lowerWTable.append([element.id1, element.XiXj, element.Wij])
		lowerVTable.append([element.id1, element.XiXj, element.Vi])
		
	if len(outputHigher) > 0:
		stats.saveFile(outputHigher, higherTableNoDuplicates, "idsup\tXsup\tVsup")
	
	if len(outputStats) > 0:
		stats.saveFile(outputStats, statsTable, "idsup\tXsup\tVsup\tidinf\tXinf\tVinf\tn\tZ\tFDR\ttags")
		
	if len(outputLowerW) > 0:
		stats.saveFile(outputLowerW, lowerWTable, "idinf\tX'inf\tWinf")
		
	if len(outputLowerV) > 0:
		stats.saveFile(outputLowerV, lowerVTable, "idinf\tX'inf\tVinf")
	
	if verbose:
		print
		print "*** results ***"
		if success:
			print "variance = " + str(variance)
		else:
			print "variance not found"
		
		print
		print "Higher file in: " + outputHigher
		print "Lower file in: " + outputLowerW
		print "Stats file in: " + outputStats
		print "Graph in: " + graphFile
		print "Info file in: " + infoFile
	
	if success:
		logList.append(["Variance = " + str(variance)])
	else:
		logList.append(["Variance not found"])
	
	if totSimulations > 0:
		if verbose:
			print
			print "Calculating confidence limits of variance..."
			
		varMedian, varLower, varUpper = getVarConf(variance, dataFile, relationsFile, totSimulations, varConfLimit, tags = tags)
		# very important, do not include the word "Variance" here
		# as this would compromise the -V parametre of other programs
		
		logList.append([])
		logList.append(["Confidence limits of variance, using %i simulations at %s%%" % (totSimulations, varConfLimit * 100)])
		logList.append(["VarLower = " + str(varLower)])
		logList.append(["VarMedian = " + str(varMedian)])
		logList.append(["VarUpper = " + str(varUpper)])
		
	
	if len(infoFile) > 0:
		stats.saveFile(infoFile, logList, "INFO FILE")
	
	if showGraph or graphFile:
		ZijList = []
		for element in outStats:
			ZijList.append(element.Zij)
		
		# this is a trick to remove "not a number" element fast
		for i in xrange(len(ZijList)):
			if str(ZijList[i]).lower() == "nan" or str(ZijList[i]).lower() == "excluded":
				ZijList[i] = sys.float_info.max
				
		ZijList = sorted(ZijList)

		try:
			NaNindex = stats.firstIndex(ZijList, sys.float_info.max)
			ZijList = ZijList[0:NaNindex - 1]
		except:
			pass
		
		newZijList = []
		N = len(ZijList)
		for i in xrange(N):
			newZijList.append([ZijList[i], float(i) / float(N)])
		
		if len(graphTitle) == 0:
			graphTitle = "Zij graph for $\sigma^2$ = " + str(variance)
		
		stats.graphZij(newZijList, graphLimits = graphLimits, graphTitle = graphTitle, graphFile = graphFile, showGraph = showGraph, showLegend = False, lineWidth = graphLineWidth, labelFontSize = labelFontSize, minimalGraphTicks = minimalGraphTicks, xLabel = xLabel, yLabel = yLabel)
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])