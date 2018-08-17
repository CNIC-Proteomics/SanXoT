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
... apeándose de Rocinante, fue sobre el de los Espejos, y, quitándole las
lazadas del yelmo para ver si era muerto y para que le diese el aire si acaso
estaba vivo; y vio... ¿Quién podrá decir lo que vio, sin causar admiración,
maravilla y espanto a los que lo oyeren? Vio, dice la historia, el rostro
mesmo, la misma figura, el mesmo aspecto, la misma fisonomía, la mesma
efigie, la pespetiva mesma del bachiller Sansón Carrasco.

Don Quixote, Part Two, Chapter XIV."""

#------------------------------------------------------

class higherResult:
	def __init__(self, id2 = None, Xj = None, Vj = None):
		self.id2 = id2
		self.Xj = Xj
		self.Vj = Vj

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

def scalarProduct(vectorA, vectorB):

	# returns the percent of elements of A
	# that are contained in B
	# where 1 means all the elements of A are present in B
	# and 0 means A and B are orthogonal
	
	# next is just to speed up a bit the program

	if len(vectorA) < len(vectorB):
		vectorShort = vectorA
		vectorLong = vectorB
	else:
		vectorShort = vectorB
		vectorLong = vectorA
	
	product = 0
	for element in vectorShort:
		first = stats.firstIndex(vectorLong, element)
		if first == -1: pass
		else: product += 1
	
	return product
										
#------------------------------------------------------

def createSimNodes(nodeList = None,
					extraData = None,
					minFontSize = 10.0,
					maxFontSize = 70.0,
					normalFontSize = 14.0,
					subData = None,
					graphLimits = 6.0,
					lineFeed = "&#10;",
					altMax = 5,
					defaultNodeColour = "#ffff80",
					errorNodeColour = "#8080ff",
					minColour = "#00ff00",
					middleColour = "#ffffff",
					maxColour = "#ff0000",
					bgColour = "#ffffd8",
					defaultNodeTextColour = "#000000",
					nonParetoOpacity = 0.5,
					paretoInfo = None):
	
	# WARNING! nodeList and extraData must be in the same order
	nodesText = ""
	
	averageN = 40
	
	# start of NMax and NMin calculation --> put into a different method ***
	
	NMax = averageN
	NMin = averageN
	
	if extraData:
		
		for i in xrange(len(extraData)):
			NValue = -1
			try:
			
				NValue = int(extraData[i][1])
				
			except:
				
				if subData:
			
					for i in xrange(len(subData)):
						NValue = -1
						try:
							NValue = len(subData[0][i + 2][1])
							if NValue > 0:
								if NValue > NMax: NMax = NValue
								if NValue < NMin: NMin = NValue
						except:
							pass
					break
				
			if NValue > 0:
				if NValue > NMax: NMax = NValue
				if NValue < NMin: NMin = NValue
				
	# end of NMax and NMin calculation
				
	for i in xrange(len(nodeList)):
		node = nodeList[i]
		
		NText = ""
		
		nodeColour, NValue, altText, nodeFontColour = stats.getNodeColourList(node,
											elementNumber = i,
											subData = subData,
											extraData = extraData,
											ZLimit = graphLimits,
											maxAltTextLinesPerSide = altMax,
											defaultNodeColour = defaultNodeColour,
											errorNodeColour = errorNodeColour,
											minColour = minColour,
											middleColour = middleColour,
											maxColour = maxColour,
											defaultNodeTextColour = defaultNodeTextColour,
											nonParetoOpacity = nonParetoOpacity,
											paretoInfo = paretoInfo,
											bgColour = bgColour)
		if extraData and NValue == -1:
			try:
				NValue = int(extraData[i][1])
			except:
				pass

		if NValue > 0:
			NText = lineFeed + "(n = %i)" % NValue
			
		nodeFontSize = stats.getNodeFontSize(NValue = NValue,
										NMax = NMax,
										NMin = NMin,
										normalFontSize = normalFontSize,
										minFontSize = minFontSize,
										maxFontSize = maxFontSize)
										
		# pdb.set_trace()
		nodesText += """\t%s [label = "%s", tooltip = "%s", style = "rounded, filled, striped", penwidth = "0", fillcolor = "%s", fontsize = "%f", fontcolor = "%s", shape = "box"];\n""" % (stats.fixNodeName(node), stats.fixNodeNameLength(node) + NText, altText, nodeColour, nodeFontSize, nodeFontColour)
		
	return nodesText

#------------------------------------------------------

def getSimArrowList(simMatrix = None, simLimit = 1.0, NMatrix = None):

	arrowList = []
	
	for i in xrange(len(simMatrix[0])):
		for j in xrange(len(simMatrix[0])):
			if j > 0 and i > 0:
				if i != j:
					if simMatrix[i][j] >= simLimit:
						nodeParent = simMatrix[0][j]
						nodeChild = simMatrix[0][i]
						if NMatrix: arrowList.append([nodeParent, nodeChild, simMatrix[i][j], NMatrix[i][j]])
						else: arrowList.append([nodeParent, nodeChild, simMatrix[i][j]])
	
	return arrowList

#------------------------------------------------------

def createSimLinks(arrowList = None, nodeDefaultColour = "#303030", minArrowWidth = 1.0, maxArrowWidth = 15.0):

	linksText = ""
	
	for arrow in arrowList:
		nodeParent = arrow[0]
		nodeChild = arrow[1]
		
		arrowWidth = minArrowWidth
		arrowColour = nodeDefaultColour
		arrowLabelText = ""
		
		if len(arrow) > 2:
			arrowWidth = float(arrow[2]) * (maxArrowWidth - minArrowWidth)  + minArrowWidth
			arrowColour = stats.extrapolateColour(arrow[2], minColour = "#ffffd8", middleColour = "#979784", maxColour = "#303030")
			if len(arrow) > 3:
				# then the NMatrix has been calculated, and N is included
				arrowLabelText = str(arrow[3])
			else:
				# NMatrix not calculated, similarity number included
				arrowLabelText = "%.2f" % round(arrow[2], 2)
		
		linksText += """\t%s -> %s [penwidth = %f, color = "%s", label = "%s", labelfontsize = 20.0];\n""" % (stats.fixNodeName(nodeParent), stats.fixNodeName(nodeChild), arrowWidth, arrowColour, arrowLabelText)
	
	return linksText

#------------------------------------------------------

def createGVFileText(simMatrix = None,
					simLimit = 1.0,
					extraData = None,
					subData = None,
					bgColour = "#ffffd8",
					NMatrix = None,
					graphLimits = 6.0,
					altMax = 5,
					defaultNodeColour = "#ffff80",
					errorNodeColour = "#8080ff",
					minColour = "#00ff00",
					middleColour = "#ffffff",
					maxColour = "#ff0000",
					defaultNodeTextColour = "#000000",
					nonParetoOpacity = 0.5,
					paretoInfo = None,
					minFontSize = 10.0,
					maxFontSize = 70.0):
	
	nodeList = simMatrix[0][1:]
	nodesText = createSimNodes(nodeList,
							extraData = extraData,
							subData = subData,
							graphLimits = graphLimits,
							altMax = altMax,
							defaultNodeColour = defaultNodeColour,
							errorNodeColour = errorNodeColour,
							minColour = minColour,
							middleColour = middleColour,
							maxColour = maxColour,
							defaultNodeTextColour = defaultNodeTextColour,
							nonParetoOpacity = nonParetoOpacity,
							paretoInfo = paretoInfo,
							bgColour = bgColour,
							minFontSize = minFontSize,
							maxFontSize = maxFontSize)
	
	arrowList = getSimArrowList(simMatrix, simLimit, NMatrix = NMatrix)
	linksText = createSimLinks(arrowList)
	
	GVFileText = """digraph similarityGraph {\n\tbgcolor = "%s";\n\n%s\n%s}""" % (bgColour, nodesText, linksText)
	
	return GVFileText

#------------------------------------------------------

def createDOTGraph(simMatrix = None,
					simLimit = 1.0,
					DOTProgramLocation = r"%ProgramFiles%\Graphviz2.30\bin",
					outputGVFile = "",
					simGraphFile = "",
					extraData = None,
					subData = None,
					NMatrix = None,
					graphLimits = 6.0,
					graphFileFormat = "png",
					altMax = 5,
					defaultNodeColour = "#ffff80",
					errorNodeColour = "#8080ff",
					minColour = "#00ff00",
					middleColour = "#ffffff",
					maxColour = "#ff0000",
					defaultNodeTextColour = "#000000",
					nonParetoOpacity = 0.5,
					paretoInfo = None,
					minFontSize = 10.0,
					maxFontSize = 70.0,
					graphDPI = 96.0,
					graphRatio = 0.0):
	
	paretoInfoIncluded = False
	for paretoElement in paretoInfo:
		if paretoElement[1]:
			paretoInfoIncluded = True
			break

	if not paretoInfoIncluded:
			# no Pareto information included, so it's better to show all categories
			nonParetoOpacity = 1.0
			print """
Warning: no information included for Pareto front calculation.
"""
	DOTProgram = "dot"
	if "win" in sys.platform:
		DOTIniPath = stats.joinLocationAndFile(os.path.dirname(os.path.realpath(sys.argv[0])), "dot.ini")
		DOTProgramLocationCheck = stats.getFromIni(DOTIniPath, "dotlocation")
		
		if len(DOTProgramLocationCheck) > 0: DOTProgramLocation = DOTProgramLocationCheck
		DOTProgram = stats.joinLocationAndFile(DOTProgramLocation, "dot.exe")
	
	GVFileText = createGVFileText(simMatrix = simMatrix,
									simLimit = simLimit,
									extraData = extraData,
									subData = subData,
									NMatrix = NMatrix,
									graphLimits = graphLimits,
									altMax = altMax,
									defaultNodeColour = defaultNodeColour,
									errorNodeColour = errorNodeColour,
									minColour = minColour,
									middleColour = middleColour,
									maxColour = maxColour,
									defaultNodeTextColour = defaultNodeTextColour,
									nonParetoOpacity = nonParetoOpacity,
									paretoInfo = paretoInfo,
									minFontSize = minFontSize,
									maxFontSize = maxFontSize)
	
	stats.saveTextFile(outputGVFile, GVFileText)
	
	if "win" in sys.platform:
		DOTCommandLine = """"%s" -Gdpi=%f -Gratio=%f -T%s "%s" -o"%s\"""" % (DOTProgram, graphDPI, graphRatio, graphFileFormat, outputGVFile, simGraphFile)
	else:
		DOTCommandLine = "%s -Gdpi=%f -Gratio=%f -T%s %s -o%s" % (DOTProgram, graphDPI, graphRatio, graphFileFormat, outputGVFile, simGraphFile)
	print DOTCommandLine
	
	try:
		if "win" in sys.platform:
			subprocess.call(DOTCommandLine)
		else:
			subprocess.call(DOTCommandLine, shell=True)
	except:
		if "win" in sys.platform:
			print """
	*** ERROR ***
	The graph could not be generated, because the dot.exe program could not be
	found. Please, check:

	   1) that you have installed Graphviz,
		  which is freely available at http://www.graphviz.org/
	   2) that you have included the path of the program folder in the dot.ini
		  file (which should be in the same folder as this program)
	"""
		else:
			print """
	*** ERROR ***
	The graph could not be generated, because the dot program could not be
	found. Please, check:

	   1) that you have installed Graphviz,
		  which is freely available at http://www.graphviz.org/
	   2) that the dot program is available from the shell.
	"""
	
	return
	
#------------------------------------------------------

def SMatrix(data = None):
	
	N = len(data)
	theMatrix = []
	NMatrix = []
	noneTypeError = "\nError: category '%s' doesn't seem to have any proteins.\nPlease, check the input files."
	
	for j in xrange(N + 1):

		if j == 0: # add first row
			
			currentRow = []
			currentRowN = []
			for i in xrange(N + 1):
				if i == 0:
					currentRow.append("")
					currentRowN.append("")
				else:
					currentRow.append(data[i - 1][0])
					currentRowN.append(data[i - 1][0])
			theMatrix.append(currentRow)
			NMatrix.append(currentRowN)
		
		else:
			
			print "analysing element #%i: %s" % ((j - 1), str(data[j - 1][0]))
			currentRow = []
			currentRowN = []
			for i in xrange(N + 1):
				if i == 0:
					currentRow.append(data[j - 1][0])
					currentRowN.append(data[j - 1][0])
				else:
					if data[j - 1][1] is None:
						print noneTypeError % data[j - 1][0]
						sys.exit()
					if data[i - 1][1] is None:
						print noneTypeError % data[i - 1][0]
						sys.exit()
					dotProduct = scalarProduct(data[j - 1][1], (data[i - 1][1]))
					currentRow.append(float(dotProduct) / float(len(data[j - 1][1])))
					currentRowN.append(dotProduct)
			theMatrix.append(currentRow)
			NMatrix.append(currentRowN)


	return theMatrix, NMatrix

#------------------------------------------------------

def splitMatrixWithHeaders(originalMatrix):

	if len(originalMatrix) > 1:
		boolMatrix = stats.zeroMatrix(len(originalMatrix) - 1)
	else:
		return None, None, "Matrix must be larger than 1x1"

	elementListColumns = []
	for i in xrange(len(originalMatrix)):
		if len(originalMatrix) != len(originalMatrix[i]):
			# must be a square matrix
			return None, "Non square matrix!"

		if i == 0:
			elementList = originalMatrix[i][1:]
		else:
			
			for j in xrange(len(originalMatrix[i])):
				
				if j == 0:
					elementListColumns.append(originalMatrix[i][0])
				else:
					boolMatrix[i - 1][j - 1] = originalMatrix[i][j]

	# for the moment, it will only work with symmetrical matrices
	if elementListColumns != elementList: return None, None, "Rows and columns do not match!"
	
	for i in xrange(len(boolMatrix)):
		if boolMatrix[i][i] != 1: return None, None, "Main diagonal different than unity!"
		
	# end of matrix arrangements
	
	return boolMatrix, elementList, "Ok"
	
#------------------------------------------------------

def getClusters(originalMatrix):
	
	# sample for debugging
	# m = [[None, "a", "b", "c", "d", "e"], ["a", 1, 1, 0, 0, 0], ["b", 1, 1, 0, 0, 0], ["c", 0, 1, 1, 0, 0], ["d", 0, 0, 0, 1, 0], ["e", 1, 0, 0, 0, 1]]
	# clusterList should be [['a', 'b', 'c', 'e'], ['d']]
	
	# clex = [['regulation of cell-matrix adhesion', 'positive regulation of angiogenesis', 'regulation of cell morphogenesis involved in differentiation'], ['regulation of actin filament polymerization', 'regulation of actin cytoskeleton organization', 'regulation of protein complex assembly'], ['negative regulation of NF-kappaB transcription factor activity'], ['regulation of mitochondrial membrane potential', 'regulation of fibroblast proliferation', 'regulation of homeostatic process'], ['positive regulation of reactive oxygen species metabolic process'], ['neuromuscular processcontrolling balance', 'neuromuscular process'], ['retina development in camera-type eye', 'axon guidance'], ['regulation of ion homeostasis', 'regulation of homeostatic process'], ['heart development', 'muscle cell development'], ['actin filament-based movement']]
	
	boolMatrix, headers, message = splitMatrixWithHeaders(originalMatrix)
	
	clusterList = [[]]
	
	for i in xrange(len(boolMatrix)):

		parentAdded = False
		parent = headers[i]

		for j in xrange(len(boolMatrix[i])):
			
			if i != j:
				if int(boolMatrix[i][j]) == 1:
					child = headers[j]
					
					# if neither parent nor child are present, create new cluster
					# if they both are present, do nothing
					# if only one of them is present, add the other

					createNewCluster = True
					for c in clusterList:

						if parent in c and child in c:
							createNewCluster = False
							parentAdded = True
							break
						if parent in c and not child in c:
							c.append(child)
							createNewCluster = False
							parentAdded = True
							break
						if child in c and not parent in c:
							c.append(parent)
							createNewCluster = False
							parentAdded = True
							break
					
					if createNewCluster:
						clusterList.append([parent, child])
						parentAdded = True
		
		if not parentAdded:
			for c in clusterList:
				if parent in c: parentAdded = True

		if not parentAdded:
			clusterList.append([headers[i]])
	
	clusterList = clusterList[1:] # removing the initial void cluster

	# sometimes as clusters "grow" independently,
	# it is seen that two clusters are different parts of the same
	# cluster; the next lines are provided to merge these two parts
	# that can occur occasionally
	initialCheck = True
	clustersToMerge = None
	while clustersToMerge or initialCheck:
		initialCheck = False
		clustersToMerge = detectClustersToMerge(clusterList)
		if clustersToMerge:
			clusterList = mergeClusters(clusterList, clustersToMerge[0], clustersToMerge[1])
	
	return clusterList, message

#------------------------------------------------------

def mergeClusters(clusterList, i, j):
	
	newCluster = clusterList[i][:]
	for clusterElement in clusterList[j]:
		if not clusterElement in newCluster: newCluster.append(clusterElement)
	
	newClusterList = []
	for k in xrange(len(clusterList)):
		if k != i and k != j:
			newClusterList.append(clusterList[k])
	
	newClusterList.append(newCluster)
	
	return newClusterList
			
#------------------------------------------------------

def detectClustersToMerge(clusterList):

	# as soon as a couple is detected,
	# this method provides those two clusters
	
	for i in xrange(len(clusterList)):
		for clusterElement1 in clusterList[i]:
			for j in xrange(len(clusterList)):
				if i != j:
					for clusterElement2 in clusterList[j]:
						if clusterElement1 == clusterElement2:
							return [i, j]
	
	return None

#------------------------------------------------------

def associateElements(inStats = "", uFile = "", relFile = ""):
	
	results = []
	
	relations = stats.loadRelationsFile(relFile)
	relations = stats.sortByIndex(relations, 0)
	
	statsData = stats.loadStatsDataFile(inStats)
	
	ZijList = []
	for element in statsData:
		ZijList.append([element[3], element[7]])
	
	theorList = []
	experList = []
	N = len(ZijList)
	for i in xrange(N):
		theorList.append([ZijList[i][0], ZijList[i][1], norm.cdf(float(ZijList[i][1]))])
		experList.append([ZijList[i][0], ZijList[i][1], (float(i) + 0.5) / float(N)])
	
	higherElements = stats.load2stringList(uFile, removeCommas = True)
	
	# WARNING! higherElements must be a list of lists
	# with each sublist being id, n, Z, FDR, X
	
	elementList = []
	if higherElements[0] == ['id', 'Z', 'n']:
		# this means the list comes from SanXoTSqueezer
		# so the header and the extra columns have to be removed
		for element in higherElements[1:]:
			# switch to id, n, Z, FDR
			elementList.append([element[0], element[2], element[1], float("nan"), float("nan")])
	
	if higherElements[0] == ['id', 'n', 'Z', 'FDR']:
		# this means it does not contain X, so a nan is put on its place
		for element in higherElements[1:]:
			elementList.append([element[0], element[1], element[2], element[3], float("nan")])
		
	if higherElements[0] == ['id', 'n', 'Z', 'FDR', 'X']:
		for element in higherElements[1:]:
			elementList.append([element[0], element[1], element[2], element[3], element[4]])
	
	# otherwise
	if higherElements[0] != ['id', 'Z', 'n'] and higherElements[0] != ['id', 'n', 'Z', 'FDR'] and higherElements[0] != ['id', 'n', 'Z', 'FDR', 'X']:
		for element in higherElements:
			elementList.append([element[0], float("nan"), float("nan"), float("nan"), float("nan")])
		
	statsData = stats.sortByIndex(statsData, 7)
	
	relationsFirstColumn = stats.extractColumns(relations, 0)
	relationsSecondColumn = stats.extractColumns(relations, 1)
	experListFirstColumn = stats.extractColumns(experList, 0)
	
	for uElement in elementList:
		lowerElementList = []
		first = stats.firstIndex(relationsFirstColumn, uElement[0])
		
		if first > -1: # -1 means it is not in the list
			notInList = 0
			last = stats.lastIndex(relationsFirstColumn, uElement[0])
			lowerElements = relationsSecondColumn[first:last + 1] # "+1" is to include the last one
			for element in lowerElements:
				lowerIndex = stats.firstIndex(experListFirstColumn, element)
				
				if lowerIndex > -1: # -1 means it is not in the list
					lowerElementList.append(element)
				else:
					notInList += 1
				
			lowerElementList = stats.sortByIndex(lowerElementList, 0)
			
			results.append([uElement[0], lowerElementList])
			
		else:
			if len(uElement[0].strip()) > 0:
				results.append([uElement[0], None])

	return results, elementList, ""

#------------------------------------------------------

def clustersWithElements(cluster, NElements):

	counter = 0
	for i in xrange(len(cluster)):
		if len(cluster[i]) >= NElements: counter += 1
	
	return counter

#------------------------------------------------------

def getBestFNumber(similarityMatrix,
					stepFNumber = 0.1,
					initialFNumber = 0.0,
					finalFNumber = 1.0,
					verbose = False):

	if initialFNumber < 0.0: initialFNumber = 0.0
	if finalFNumber > 1.0: finalFNumber = 1.0
	if stepFNumber <= 0.0: stepFNumber = 0.1

	frange = stats.forstep(initialFNumber, finalFNumber, stepFNumber)

	FNumberArray = []
	
	bestCNumber = 0
	bestFNumber = 1.0
	bestBooleanSimMatrix = []
	bestClusterVector = []
		
	for FNumber in frange:

		booleanSimMatrix = stats.booleaniseMatrix(similarityMatrix, threshold = FNumber)
		clusterVector, message = getClusters(booleanSimMatrix)
		CNumber = getCNumber(clusterVector)
		
		if CNumber > bestCNumber:
			bestCNumber = CNumber
			bestFNumber = FNumber
			FNumberArray = [FNumber]
		else:
			if CNumber == bestCNumber:
				FNumberArray.append(FNumber)
				
		if verbose: print "FNumber = %f: there are at least %i clusters with %i elements." % (FNumber, CNumber, CNumber)

		FNumberArray.sort()
	
	medianFNumber = FNumberArray[(len(FNumberArray) - 1) / 2]
	booleanSimMatrix = stats.booleaniseMatrix(similarityMatrix, threshold = medianFNumber)
	bestClusterVector, message = getClusters(booleanSimMatrix)
	
	return medianFNumber, bestBooleanSimMatrix, bestClusterVector, bestCNumber

#------------------------------------------------------

def getCNumber(cluster):

	# cl = [["a", "b", "c"], ["d", "e"], ["f", "g"]]
	# for debugging, output is 2
	# cl = [["a", "b", "c"], ["d", "e"], ["f", "g"], ["h", "i", "j"], ["k", "l", "m", "n"]]
	# for debugging, output is 3
	
	tentativeCNumber = len(cluster)
		
	CNumber = 0
	while tentativeCNumber > 0:
		if clustersWithElements(cluster, tentativeCNumber) >= tentativeCNumber:
			CNumber = tentativeCNumber
			break
		tentativeCNumber -= 1
	
	return CNumber

#------------------------------------------------------

def getParetoInfo(clusterVector = None, extraData = None):

	paretoInfo = []
	extraDataWithClusters = extraData[:]
	
	if clusterVector and extraData:
		for i in xrange(len(clusterVector)):
		
			clusterProvisionalList = []
			dataList = []
			clusterName = "Cluster #%i" % i
			
			for clusterElement in clusterVector[i]:
				nValue = float("nan")
				extraDataIndex = stats.firstIndex(stats.extractColumns(extraDataWithClusters, 0), clusterElement)
				
				if str(extraData[extraDataIndex][1]).lower() != "nan":
					nValue = int(extraData[extraDataIndex][1])
					
				clusterProvisionalList.append([extraDataIndex,
											nValue, # n
											float(extraData[extraDataIndex][4]), #X
											extraData[extraDataIndex][0]]) # id
				dataList.append([nValue,
								abs(float(extraData[extraDataIndex][4]))])
								
			for clusterElement in clusterProvisionalList:
				dataPoint = [clusterElement[1], abs(clusterElement[2])] # {n, X}
				extraDataWithClusters[clusterElement[0]].extend([clusterName, stats.isParetoFront(dataPoint, dataList)])
				paretoInfo.append([extraDataWithClusters[clusterElement[0]][0], extraDataWithClusters[clusterElement[0]][6]])
	
	return paretoInfo, extraDataWithClusters

#------------------------------------------------------
	
def printHelp(version = None):

	print """
Sanson %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to
generate the similarity graph of a set of categories.

A similarity graph is a graph that shows the relationship between a set of
categories by taking into account how many proteins they share. This is
measured with a variable f such that for categories c1 and c2, we get:

   f(c1, c2) = (#proteins shared by c1 and c2) / (#proteins of c1)
   
for instance:
  * if c1 == c2, we get f(c1, c2) = f(c2, c1) = 1;
  * if c1 and c2 do not share any proteins, we get f(c1, c2) = f(c2, c1) = 0;
  * if c2 is contained in c1, we get f(c1, c2) <= 1, f(c2, c1) = 1, etc

If no f number is given with the parametres (-e), then the program
automatically calculates the best f number, by maximising both the number of
category clusters and the number categories within each cluster.

Sanson needs three input files:

     * a stats file, the outStats file from SanXoT (using the -z command)
     * a higher level list to graph (using the -c command)
     * a relations file (using -r command)

And delivers five output files:

     * the graph in PNG format (default suffix: "_simGraph.png")
     * the DOT language text file used to generate the graph (default suffix:
           "_simGraph.gv")
     * a table showing the clusters generated (default suffix: "_outClusters")
     * the similarity matrix used to generate the graph (default suffix:
           "_outSimilarities")
     * a log file (default suffix: "_logFile")

Usage: sanson.py -z[stats file] -r[relations file] -c[higher level list file] [OPTIONS]

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the
                       stats file.
   -b, --nosubstats    To avoid colouring the boxes according to the proteins
                       that are in the concerning category (in this case, the
                       box is coloured using the Zij of the category, when this
                       information is available in the higher level list to
                       graph, see -c command).
   -c, --list=filename The text file containing the higher level elements whose
                       categories we want to relate. If the first element is
                       not taken, it might help saving the file with ANSI
                       format. If a header is used, then it must be in the form
                       "id>n>Z>FDR" or "id>Z>n" (where ">" means "tab").
   -d, --dotfile=filename
                       To use a non-default name for the text file in DOT
                       language, which is used to generate the graph.
   -e, --similarity=float
                       To override the calculation of the optimal f number (see
                       above for more details).
   -g, --graphformat=string
                       File format for the similarity graph (default is "png").
   -G, --outgraph=filename
                       To use a non-default name for the graph file.
   -l, --graphlimits=integer
                       To set the +- limits of the most intense red/green
                       colours in the graph (default is 6).
   -L, --logfile=filename
                       To use a non-default name for the log file.
   -m, --simfile=string
                       To use a non-default name for the similarity matrix
                       file.
   -N, --altmax=integer
                       Maximum number of lower level elements that the alt text
                       of the higher level node will show per side. For
                       instance, for N = 3, alt text will show all the elements
                       up to six; beyond this, only the first and last three
                       will be shown. (Default is N = 5.) (Note that this will
                       have effect if the SVG format is used.)
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the stats file folder.
   -r, --relfile, --relationsfile=filename
                       Relations file, with identificators of the higher level
                       in the first column, and identificators of the lower
                       level in the second column.
   -s, --outcluster=filename
                       To use a non-default name for the file containg the
                       list of clusters.
   -z, --outstats=filename
                       The outStats file from a SanXoT integration.
                       
   --graphdpi=float    To define the resolution (in DPI, dots per inch) for the
                       output graph. (Default is 96.0)
   --graphratio=float  To define the height/width ratio in the output graph.
                       (Default is 0.0, which means the ratio is not adjusted,
                       si the ratio is automatically set by graphviz)
   --minfontsize=float To define the minimum font size in nodes. If larger than
                       maxfontsize, the maxfontsize will be used (so
                       minfontsize = maxfontsize). (Default is 10.0)
   --maxfontsize=float To define the maximum font size in nodes.
                       (Default is 70.0)
   --nonparetoopacity=float
                       To "downlight" nodes not part of the Pareto front.
                       (default = 0.5, 0.0 means node color = background,
                       1.0 means no difference between Pareto front and
                       non-Pareto font)
                       
   --selectednodecolor=#rrggbb, --selectednodecolour=#rrggbb
   --defaultnodecolor=#rrggbb, --defaultnodecolour=#rrggbb
   --defaultnodetextcolor=#rrggbb, --defaultnodetextcolour=#rrggbb
   --errornodecolor=#rrggbb, --errornodecolour=#rrggbb
   --middlecolor=#rrggbb, --middlecolour=#rrggbb
   --mincolor=#rrggbb, --mincolour=#rrggbb
   --maxcolor=#rrggbb, --maxcolour=#rrggbb
   
""" % version

	return

#------------------------------------------------------

def main(argv):

	version = "v1.13"
	verbose = False
	similarityLimit = -1.0 # if remain as -1, it will be calculated
	graphLimits = 6.0
	analysisName = ""
	useSubStats = True
	defaultAnalysisName = "sanxot"
	analysisFolder = ""
	# input files
	inStats = ""
	defaultStatsFile = "stats"
	defaultRelationsFile = "rels"
	defaultTableExtension = ".tsv"
	defaultTextExtension = ".txt"
	defaultDOTExtension = ".gv"
	relationsFile = ""
	upperLevelToGraphFile = ""
	# output files
	defaultUpperLevelToGraphFile = "ulst"
	defaultOutputGraph = "simGraph"
	defaultLogFile = "logFile"
	defaultSimilarityMatrixFile = "outSimilarities"
	defaultOutputGVFileName = "simGraph"
	defaultOutputClusterFileName = "outClusters"
	logFile = ""
	graphFile = ""
	dotFile = ""
	outCluster = ""
	similarityMatrixFile = ""
	graphFileFormat = "png"
	altMax = 5
	
	selectedNodeColour = "#ff9090"
	defaultNodeColour = "#ffff80"
	errorNodeColour = "#8080ff"
	minColour = "#00ff00"
	middleColour = "#ffffff"
	maxColour = "#ff0000"
	defaultNodeTextColour = "#000000"
	nonParetoOpacity = 0.5
	
	minFontSize = 10.0
	maxFontSize = 70.0
	graphDPI = 96.0
	graphRatio = 0.0
	
	logList = [["Sanson " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:p:z:r:c:L:G:m:l:d:e:s:d:g:N:bhk", ["analysis=", "folder=", "place=", "statsfile=", "relfile=", "relationsfile=", "list=", "logfile=", "graphfile=", "simfile=", "graphlimits=", "similarity=", "dotfile=", "outcluster=", "graphformat=", "altmax=", "selectednodecolour=", "selectednodecolor=", "defaultnodecolour=", "defaultnodecolor=", "defaultnodetextcolour=", "defaultnodetextcolor=", "errornodecolour=", "errornodecolor=", "mincolour=", "mincolor=", "middlecolour=", "middlecolor=", "maxcolour=", "maxcolor=","nonparetoopacity=", "minfontsize=", "maxfontsize=", "graphdpi=", "graphratio=", "nosubstats", "help", "egg", "easteregg"])
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
		elif opt in ("-z", "--statsfile"):
			inStats = arg
		elif opt in ("-r", "--relfile", "--relationsfile"):
			relationsFile = arg
		elif opt in ("-c", "--list"):
			upperLevelToGraphFile = arg
		elif opt in ("-L", "--logfile"):
			logFile = arg
		elif opt in ("-G", "--graphfile"):
			graphFile = arg
		elif opt in ("-m", "--simfile"):
			similarityMatrixFile = arg
		elif opt in ("-l", "--graphlimits"):
			graphLimits = float(arg)
		elif opt in ("-e", "--similarity"):
			similarityLimit = float(arg)
		elif opt in ("-d", "--dotfile"):
			dotFile = float(arg)
		elif opt in ("-s", "--outcluster"):
			outCluster = float(arg)
		elif opt in ("-b", "--nosubstats"):
			useSubStats = False
		elif opt in ("--nonparetoopacity"):
			nonParetoOpacity = float(arg)
		elif opt in ("-N", "--altmax"):
			altMax = int(arg)
		elif opt in ("-g", "--graphformat"):
			graphFileFormat = arg.lower().strip()
			if graphFileFormat == "jpeg": graphFileFormat = "jpg"
			if graphFileFormat != "png" and \
				graphFileFormat != "svg" and \
				graphFileFormat != "jpg" and \
				graphFileFormat != "tif" and \
				graphFileFormat != "tiff" and \
				graphFileFormat != "pdf" and \
				graphFileFormat != "bmp" and \
				graphFileFormat != "gif":
				print
				print "Warning: graph format \"%s\" is not supported,\npng will be used instead." % graphFileFormat
				print
				graphFileFormat = "png"
		
		elif opt in("--selectednodecolour", "--selectednodecolor"):
			selectedNodeColour = arg
		elif opt in("--defaultnodecolour", "--defaultnodecolor"):
			defaultNodeColour = arg
		elif opt in("--defaultnodetextcolour", "--defaultnodetextcolor"):
			defaultNodeTextColour = arg
		elif opt in("--errornodecolour", "--errornodecolor"):
			errorNodeColour = arg
		elif opt in("--mincolour", "--mincolor"):
			minColour = arg
		elif opt in("--middlecolour", "--middlecolor"):
			middleColour = arg
		elif opt in("--maxcolour", "--maxcolor"):
			maxColour = arg
		elif opt in("--minfontsize"):
			minFontSize = float(arg)
		elif opt in("--maxfontsize"):
			maxFontSize = float(arg)
		elif opt in("--graphdpi"):
			graphDPI = float(arg)
		elif opt in("--graphratio"):
			graphRatio = float(arg)
		
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("--egg", "--easteregg"):
			easterEgg()
			sys.exit()

# REGION: FILE NAMES SETUP

	if minFontSize > maxFontSize: minFontSize = maxFontSize
	defaultGraphExtension = "." + graphFileFormat
	
	if len(analysisName) == 0:
		if len(inStats) > 0:
			analysisName = os.path.splitext(os.path.basename(inStats))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	if len(inStats) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(inStats)) > 0:
			analysisFolder = os.path.dirname(inStats)

	# input
	if len(inStats) == 0:
		inStats = os.path.join(analysisFolder, analysisName + "_" + defaultStatsFile + defaultTableExtension)
		
	if len(os.path.dirname(inStats)) == 0 and len(analysisFolder) > 0:
		inStats = os.path.join(analysisFolder, inStats)

	if len(relationsFile) == 0:
		relationsFile = os.path.join(analysisFolder, analysisName + "_" + defaultRelationsFile + defaultTableExtension)
		
	if len(upperLevelToGraphFile) == 0:
		upperLevelToGraphFile = os.path.join(analysisFolder, analysisName + "_" + defaultUpperLevelToGraphFile + defaultTextExtension)
	
	if len(os.path.dirname(relationsFile)) == 0 and len(os.path.basename(relationsFile)) > 0:
		relationsFile = os.path.join(analysisFolder, relationsFile)

	if len(os.path.dirname(upperLevelToGraphFile)) == 0 and len(os.path.basename(upperLevelToGraphFile)) > 0:
		upperLevelToGraphFile = os.path.join(analysisFolder, upperLevelToGraphFile)
		
	# output
	if len(dotFile) == 0:
		dotFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputGVFileName + defaultDOTExtension)
	
	if len(outCluster) == 0:
		outCluster = os.path.join(analysisFolder, analysisName + "_" + defaultOutputClusterFileName + defaultTableExtension)
	
	if len(similarityMatrixFile) == 0:
		similarityMatrixFile = os.path.join(analysisFolder, analysisName + "_" + defaultSimilarityMatrixFile + defaultTextExtension)
		
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
		
	if len(graphFile) == 0:
		graphFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputGraph + defaultGraphExtension)

	if len(os.path.dirname(dotFile)) == 0 and len(os.path.basename(dotFile)) > 0:
		dotFile = os.path.join(analysisFolder, dotFile)

	if len(os.path.dirname(outCluster)) == 0 and len(os.path.basename(outCluster)) > 0:
		outCluster = os.path.join(analysisFolder, outCluster)
		
	if len(os.path.dirname(similarityMatrixFile)) == 0 and len(os.path.basename(similarityMatrixFile)) > 0:
		similarityMatrixFile = os.path.join(analysisFolder, similarityMatrixFile)
		
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)
		
	if len(os.path.dirname(graphFile)) == 0 and len(os.path.basename(graphFile)) > 0:
		graphFile = os.path.join(analysisFolder, graphFile)
		
	logList.append([""])
	logList.append(["Input stats file: " + inStats])
	logList.append(["Relations file: " + relationsFile])
	logList.append(["File with sigmoids to depict: " + upperLevelToGraphFile])
	logList.append(["Output similarity matrix table: " + similarityMatrixFile])
	logList.append(["Output log file: " + logFile])
	logList.append(["Output graph file: " + graphFile])
	logList.append([""])
	if useSubStats: logList.append(["Filling nodes with Z from lower elemenets"])
	else: logList.append(["Filling nodes with Z from upper elements"])
	logList.append([""])

	# pp.pprint(logList)
	# sys.exit()

# END REGION: FILE NAMES SETUP			
	
	try:
		data, extraData, logListExtraInfo = associateElements(inStats = inStats, uFile = upperLevelToGraphFile, relFile = relationsFile)
		logList.append(logListExtraInfo)
		logList.append(["Data files correctly loaded."])
	except getopt.GetoptError:
		logList.append(["Error while getting data files."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	if len(data) == 0:
		logList.append([""])
		errorMessage = "No data were retrieved to create the similarity graph."
		print errorMessage
		print "Exiting..."
		logList.append([errorMessage])
	else:
		
		similarityMatrix, NMatrix = SMatrix(data)
		
		stats.saveFile(similarityMatrixFile, similarityMatrix)
		
		if useSubStats:
			# añadir salida para log ***
			subData = stats.arrangeSubData(inStats = inStats,
							uFile = upperLevelToGraphFile,
							relFile = relationsFile,
							ignoreNaNsInFDR = True)
		else:
			subData = None
		
		if similarityLimit < 0.0 or similarityLimit > 1.0:
			# means it has to be calculated
			# this includes the default value = -1
			FNumber, bestBooleanSimMatrix, bestClusterVector, CNumber = \
				getBestFNumber(similarityMatrix,
					verbose = True,
					stepFNumber = 0.01,
					initialFNumber = 0.0,
					finalFNumber = 1.0)
			
			logList.append([""])
			logList.append(["Creating DOT graph for the best FNumber = %f." % FNumber])
			logList.append(["At least %i graphs contain %i nodes." % (CNumber, CNumber)])
		else:
			FNumber, bestBooleanSimMatrix, bestClusterVector, CNumber = \
				getBestFNumber(similarityMatrix,
					verbose = True,
					stepFNumber = 0.0,
					initialFNumber = similarityLimit,
					finalFNumber = similarityLimit)
					
			logList.append([""])
			logList.append(["Creating DOT graph for the given FNumber = %f." % FNumber])
			
		print "Best FNumber: %f" % FNumber
		
		paretoInfo, extraDataWithClusters = getParetoInfo(clusterVector = bestClusterVector,
						extraData = extraData)
						
		# stats.saveFile(outCluster, bestClusterVector, "CLUSTERS IDENTIFIED")
		stats.saveFile(outCluster, extraDataWithClusters, "id\tn\tZ\tFDR\tX\tcluster id\tPareto front?")
		
		createDOTGraph(similarityMatrix,
						simLimit = FNumber,
						outputGVFile = dotFile,
						simGraphFile = graphFile,
						extraData = extraData,
						subData = subData,
						NMatrix = NMatrix,
						graphLimits = graphLimits,
						graphFileFormat = graphFileFormat,
						altMax = altMax,
						defaultNodeColour = defaultNodeColour,
						errorNodeColour = errorNodeColour,
						minColour = minColour,
						middleColour = middleColour,
						maxColour = maxColour,
						defaultNodeTextColour = defaultNodeTextColour,
						nonParetoOpacity = nonParetoOpacity,
						paretoInfo = paretoInfo,
						minFontSize = minFontSize,
						maxFontSize = maxFontSize,
						graphDPI = graphDPI,
						graphRatio = graphRatio)
	
	stats.saveFile(logFile, logList, "LOG FILE")
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])
