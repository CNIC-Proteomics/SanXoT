import pdb
import sys
import getopt
import operator
import pprint
import os
# begin: jmrc
import matplotlib
matplotlib.use("agg")
#end: jmrc
from numpy import *
from pylab import *
from scipy.stats import norm
import matplotlib.pyplot as plt
import random
import math
#import time

#######################################################

def version():
	return "v0.58"

#------------------------------------------------------

# Function to calculate FDR
def fdr_calculator(full_list):
	Rank_dic = {}
	count = 1
	mainlist = []
	FDR = 0
	
	## create a dic for the z value with rank =0
	for line in full_list:
		if str(line[7]).lower() != "nan":
			Rank_dic[line[7]] = 0
	Rkey = Rank_dic.keys()
	Rkey.sort()
	
	## assign rank
	for r in Rkey:
		Rank_dic[r] = count
		count += 1
	for line1 in full_list:
		if str(line1[7]).lower() == "nan":
			FDR = "nan"
		else:
			Zval = abs(line1[7])
			FDR = 2 * (((1 - norm.cdf(Zval)) * float(len(Rank_dic))) / float(Rank_dic[line1[7]]))
		line1.append(FDR)
		mainlist.append(line1)
		
	return mainlist

#------------------------------------------------------

def graphZij(ZijList,
				graphTitle = '',
				xLabel = "Zij",
				yLabel = "Rank/N",
				showGrid = True,
				graphLimits = 0,
				graphFile = None,
				showGraph = True,
				dpi = None,
				manySigmoids = False,
				showLegend = True,
				graphFontSize = 8,
				lineWidth = 1.0,
				labelFontSize = 12,
				minimalGraphTicks = False):

	# next line is important to prevent SanXoTGauss from printing squares
	# instead of Unicode characters, such as Greek letters
	matplotlib.rc('font', **{'sans-serif' : 'Arial', 'family' : 'sans-serif'})
	graphTitle = graphTitle.strip()
	if len(ZijList) < 2: return
	
	if not manySigmoids:
		Zij = []
		RankN = []
		normalDistribution = []
		
		for element in ZijList:
			Zij.append(float(element[0]))
			RankN.append(element[1])
			normalDistribution.append(norm.ppf(element[1]))
		
		plt.plot(Zij, RankN, 'b.', markersize = lineWidth * 2, markeredgewidth = 0.0, label = 'Experimental')
		plt.plot(normalDistribution, RankN, 'r', linewidth = lineWidth, markeredgewidth = 0.0, label = 'Theoretical', alpha = 0.8)
	
	else:
		
		# upto 55 colours
		# after that, they are all black
		defaultColour = "#000000"
		plotStyle = ["#FF0000", "#0000FF", "#00FF00", "#FF00FF", "#00FFFF", "#FFFF00", "#800000", "#008000", "#000080", "#808000", "#800080", "#008080", "#808080", "#C00000", "#00C000", "#0000C0", "#C0C000", "#C000C0", "#00C0C0", "#C0C0C0", "#400000", "#004000", "#000040", "#404000", "#400040", "#004040", "#404040", "#200000", "#002000", "#000020", "#202000", "#200020", "#002020", "#202020", "#600000", "#006000", "#000060", "#606000", "#600060", "#006060", "#606060", "#A00000", "#00A000", "#0000A0", "#A0A000", "#A000A0", "#00A0A0", "#A0A0A0", "#E00000", "#00E000", "#0000E0", "#E0E000", "#E000E0", "#00E0E0", "#E0E0E0"]

		for j in xrange(len(ZijList)):
			i = len(ZijList) - (j + 1)
			if i > 0:
				graph = ZijList[i]
				labelName = splitLabel(graph[0], maxLine = 50)
				graphData = graph[1]
				if type(graphData) == type([]):
					graphX = extractColumns(graphData, 1)
					graphY = extractColumns(graphData, 2)
					
					if i < len(plotStyle):
						colour = plotStyle[i]
					else:
						# after max, just keep the last one
						colour = plotStyle[-1]
					
					# the .decode(...) is important to avoid problems when text is in Unicode
					plt.plot(graphX, graphY, colour,
						linewidth = lineWidth, markersize = 2.0, markeredgewidth = 0.0, label = labelName.decode(encoding='UTF-8'))
			else:
				# theoretical is slightly bolder
				graph = ZijList[0]
				labelName = splitLabel(graph[0], maxLine = 50)
				graphData = graph[1]
				graphX = extractColumns(graphData, 1)
				graphY = extractColumns(graphData, 2)
				bolderLineWidth = 3 * lineWidth
				plt.plot(graphX, graphY, plotStyle[0],
					linewidth = bolderLineWidth, markersize = 2.0, markeredgewidth = 0.0, label = labelName.decode(encoding='UTF-8'), alpha = 0.8)

	
	plt.xlabel(xLabel, fontsize = labelFontSize)
	plt.ylabel(yLabel, fontsize = labelFontSize)
	
	if minimalGraphTicks:
		plt.xticks([-graphLimits, 0, graphLimits])
		plt.yticks([0, 1])
		plt.tick_params(axis = "both", which = "major", labelsize = labelFontSize)
	
	if len(graphTitle) > 0:
		plt.title(graphTitle, fontsize = labelFontSize)
		
	plt.grid(showGrid)
	
	if showLegend: plt.legend(loc = 'lower right', prop={'size':graphFontSize})
	
	if graphLimits > 0:
		plt.axis([-graphLimits, graphLimits, 0, 1])
	
	plt.tight_layout()

	if graphFile:
		plt.savefig(graphFile, dpi = dpi)
	
	if showGraph: show()
	
	return

#------------------------------------------------------

def splitLabel(labelName, maxLine = 25, maxLength = 250):

	for i in range(maxLength / maxLine)[1:]:
		cutLength = (maxLine + 1) * i - 1
		if len(labelName) > cutLength:
			labelName = labelName[0:cutLength] + "\n" + labelName[cutLength:]
	
	return labelName
	
#------------------------------------------------------

def joinLocationAndFile(location, file):

	location = location.replace("%ProgramFiles%", os.getenv("ProgramFiles"))
	location = location.replace("%AppData%", os.getenv("AppData"))
	# ... other shortcuts can be added here if needed

	if location.startswith("\"") and \
		location.endswith("\"") and \
		len(location) - len(location.replace("\"", "")):
		location = location[1:-1]
	
	if not os.path.isdir(location):
		location = os.path.dirname(location)
		
	locationAndFile = os.path.join(location, file)
	
	return locationAndFile
	
#------------------------------------------------------

def removeDuplicates(inputList):

	outputList = inputList[:]
	outputList.sort()
	
	i = 0

	while i < len(outputList) - 1:

		if outputList[i] == outputList[i + 1]:
			del outputList[i + 1]
		else: i += 1
	
	return outputList

#------------------------------------------------------

def zeroMatrix(x, y = -1, defaultValue = 0.0):

	if y == -1: y = x # so, absence of y provides a square matrix
	zMatrix = []
	for i in xrange(x):
		zRow = []
		for j in xrange(y):
			zRow.append(defaultValue)
		zMatrix.append(zRow)
	
	return zMatrix

#------------------------------------------------------
	
def booleaniseMatrix(myMatrix, threshold = 0):

	booleanMatrix = zeroMatrix(len(myMatrix))
	
	for i in xrange(len(myMatrix)):
		for j in xrange(len(myMatrix)):

			if type(myMatrix[i][j]) == type(0) or type(myMatrix[i][j]) == type(0.0):
			
				if myMatrix[i][j] >= threshold: booleanMatrix[i][j] = 1
				else: booleanMatrix[i][j] = 0
			else: booleanMatrix[i][j] = myMatrix[i][j]
	
	return booleanMatrix
#------------------------------------------------------
	
def booleaniseMatrix2(myMatrix, threshold = 0):

	print "booleanising matrix"
	for i in xrange(len(myMatrix)):
		if i % 500 == 0: print "Booleanising row #%i of %i" % (i, len(myMatrix))
		for j in xrange(len(myMatrix)):

			if type(myMatrix[i][j]) == type(0) or type(myMatrix[i][j]) == type(0.0):
			
				if myMatrix[i][j] >= threshold: myMatrix[i][j] = 1
				else: myMatrix[i][j] = 0
	
	return myMatrix
		
#------------------------------------------------------

def getConfluenceList(inputList, deleteDuplicates = False):
	
	#header = inputList.pop(0)
		
	newList = inputList[:]
	outputList = []
	
	for element in newList:
		newElement = ['1', element]
		outputList.append(newElement)
	
	if deleteDuplicates:
		outputList = removeDuplicates(outputList)
	
	#outputList.insert(0, header)
	
	return outputList
	
#------------------------------------------------------

def fixNodeNameLength(originalName, fixingCharacter = " ", maxLength = 12, lineFeed = "&#10;"):
	# important for DOT language graphs
	nameParts = originalName.split(fixingCharacter)
	fixedName = ""

	newPart = ""
	for part in nameParts:
		if len(newPart) < maxLength:
			newPart += part + fixingCharacter
		else:
			fixedName += newPart[:len(newPart) - 1] + lineFeed
			newPart = part + fixingCharacter
	
	fixedName += newPart[:len(newPart) - 1]
	
	return fixedName

#------------------------------------------------------

def fixNodeName(originalName):
	# important for DOT language graphs
	
	# uppercases should not be a problem, as GVEdit seems to be
	# case sensitive
	fixedName = "NODE_"
	
	for character in originalName:
		if (ord(character) >= ord("a") and ord(character) <= ord("z")) \
			or (ord(character) >= ord("A") and ord(character) <= ord("Z")) \
			or (ord(character) >= ord("0") and ord(character) <= ord("9")):
			fixedName += character
		else:
			if ord(character) == ord(" "):
				fixedName += "_"
			else:
				fixedName += "_ASCII%i_" % ord(character)
	
	return fixedName

#------------------------------------------------------

def extractVariableFromInfoFile(infoFile, varName = "Variance", defaultSeed = float("nan"), verbose = True):
	
	fileContents = load2stringList(infoFile)
	variableOk = True
	varName = varName.strip()

	for line in fileContents[::-1]: # [::-1] is to search from the end of the file
		if varName + " not found" in line[0]:
			if verbose: print varName + " not found in previous integration"
			variableOk = False
			return defaultSeed, variableOk
		if varName + " = " in line[0]:
			return (double)(line[0].split("=")[1].strip()), variableOk
	
	if verbose: print """the file does not contain any "%s = [float]" line; the default seed will be used.""" % varName
	
	return defaultSeed, variableOk
	
#------------------------------------------------------

def extractVarianceFromVarFile(varFile, verbose = True, defaultSeed = 0.001):
	
	resultValue, varianceOk = extractVariableFromInfoFile(varFile, varName = "Variance", defaultSeed = defaultSeed, verbose = verbose)
	
	return resultValue, varianceOk
	
#------------------------------------------------------

def extractKFromKFile(kFile, verbose = True, defaultSeed = 1.0):
	
	resultValue, KOk = extractVariableFromInfoFile(kFile, varName = "K", defaultSeed = defaultSeed, verbose = verbose)
	
	return resultValue, KOk

#------------------------------------------------------
	
def refillDuplicates(inputList):

	changed = False
	
	outputList = inputList[:]
	outputList.sort()
	
	i = 0
	
	while i < len(outputList) - 1:

		if outputList[i] == outputList[i + 1]:
			randomNumber = random.randint(0, len(inputList) - 1)
			outputList[i][0] = inputList[randomNumber][0]
			changed = True
		else: i += 1
	
	return outputList, changed
	
#------------------------------------------------------

def getRandomList(inputList):
	
	outputList = [-1] * len(inputList) # filling all with -1
	lowerList = list(set(extractColumns(inputList, 1)))
	listWithId = []
	
	# generating conversionTable
	conversionTable = []
	i = 0
	
	for i in xrange(len(lowerList)):
		conversionTable.append([i, random.random()])

	conversionTable = sortByIndex(conversionTable, 1)
	conversionTable = extractColumns(conversionTable, 0)
	
	# older conversionTable generator
	# while i < len(lowerList):
		# randomNumber = random.randint(0, len(lowerList) - 1)
		# if not randomNumber in conversionTable:
			# conversionTable.append(randomNumber)
			# i += 1

	# assigning new relations according to conversion table
	for i in xrange(len(outputList)):
		
		# switching lower elements
		# while keeping structure (distribution of lower elements per higher element)
		lowerElement = inputList[i][1]
		# improved method, much faster!!
		index, listWithId = firstIndex(list = lowerList, listWithId = listWithId, element = lowerElement, method = "binsearch")
		indexOfNewElement = conversionTable[index]
		newElement = lowerList[indexOfNewElement]
		
		outputList[i] = [inputList[i][0], newElement]
			
	if -1 in outputList:
		print "Error while generating the randomised relations table"
		sys.exit()
	
	return outputList
	
#------------------------------------------------------

def getNodeColourList(node,
						elementNumber,
						ZLimit = 6.0,
						subData = None,
						extraData = None,
						maxAltTextLinesPerSide = 5,
						lineFeed = "&#10;",
						defaultNodeColour = "#ffff80",
						errorNodeColour = "#8080ff",  # default is white
						minColour = "#00ff00",
						middleColour = "#ffffff",
						maxColour = "#ff0000",
						bgColour = "#ffffd8",
						defaultNodeTextColour = "#000000",
						nonParetoOpacity = 0.5,
						errorNodeTextColour = "#0000ff",
						paretoInfo = None):

	altText = ""
	NValue = -1
	nodeColour = defaultNodeColour
	nodeFontColour = defaultNodeTextColour
	nonParetoNodeTextColour = averageColour(normalisedValue = nonParetoOpacity,
													colour1 = bgColour,
													colour2 = defaultNodeTextColour)

	nodeIsParetoFront = True
			
	try:
		if paretoInfo:
			# if node == "DAVID_SP_PIR_KEYWORDS_blood coagulation":
				# pdb.set_trace()
			nodeIsParetoFront = True
			if filterByElement(paretoInfo, node)[0][1]:
				nodeFontColour = defaultNodeTextColour
			else:
				nodeIsParetoFront = False
				nodeFontColour = nonParetoNodeTextColour
	except:
		nodeFontColour = errorNodeTextColour
	
	
	i = elementNumber + 2
	
	try:

		if subData:
			subDataHigher = subData[0][i][0]
			if subDataHigher == node:
				nodeColour = ""
				NValue = len(subData[0][i][1])
				lowerNodeElementRatio = 1.0 / float(NValue)
				counter = 0
				for lowerElement in subData[0][i][1]:
					counter += 1
					lowerNodeElementZ = lowerElement[1]
					lowerNodeElementColour = extrapolateColour(lowerNodeElementZ,
												minValue = -ZLimit,
												middleValue = 0.0,
												maxValue = ZLimit,
												maxColour = maxColour,
												middleColour = middleColour,
												minColour = minColour)
					if not nodeIsParetoFront:
						lowerNodeElementColour = averageColour(normalisedValue = nonParetoOpacity,
													colour1 = bgColour,
													colour2 = lowerNodeElementColour)
					lowerNodeElementResult = "%s;%f:" % (lowerNodeElementColour, lowerNodeElementRatio)
					nodeColour += lowerNodeElementResult
					
					if maxAltTextLinesPerSide > 0:
						lowerNodeElementName = str(lowerElement[0])
						lowerElementAltText = "%i) Z = %f, NAME = &#34;%s&#34;" % (counter, lowerNodeElementZ, lowerNodeElementName)
						if len(altText) == 0:
							altText = lowerElementAltText
						else:
							if counter > maxAltTextLinesPerSide and counter < NValue - maxAltTextLinesPerSide + 1:
								if counter == maxAltTextLinesPerSide + 1: altText += "&#10;"
								altText += "."
							else:
								altText += lineFeed + lowerElementAltText
				
				if len(nodeColour) > 0:
					nodeColour = nodeColour[:-1] # to remove final ":"
				else:
					nodeColour = errorNodeColour # blue denotes an error occurred
			else:
				# in this case, the names do not match
				# should search for it, as the list might be in a different order if
				# the code has been touched,
				# but for the moment it will just paint it in blue ***
				nodeColour = errorNodeColour
		else:
			ZIndex = 2
			nodeColour = getNodeColour(node,
								extraData = extraData,
								colouringVariableIndex = ZIndex,
								minValue = -ZLimit,
								middleValue = 0,
								maxValue = ZLimit,
								maxColour = maxColour,
								middleColour = middleColour,
								minColour = minColour)
		
		if len(nodeColour) > 2**14: nodeColour = nodeColourReduced(nodeColour)
		# should give an error when nodeColour is > 2**14 even after nodeColourReduced
		# could make shorter numbers in that case
		
	except:
	
		return errorNodeColour, NValue

	return nodeColour, NValue, altText, nodeFontColour

#------------------------------------------------------

def extrapolateColour(value = 0.0,
					minValue = 0.0,
					middleValue = 1.0,
					maxValue = 1.0,
					minColour = "#00ff00",
					middleColour = "#ffffff",
					maxColour = "#ff0000"):
					
	resultingColour = middleColour
	
	if value <= minValue:
		resultingColour = minColour
		
	if value > minValue and value < middleValue:
		if minValue == middleValue:
			resultingColour = minColour
		else:
			normalisedValue = (value - minValue) / (middleValue - minValue)
			resultingColour = averageColour(normalisedValue, minColour, middleColour)
		
	if value > middleValue and value < maxValue: # value = middleColour is default already
		if middleValue == maxValue:
			resultingColour = maxColour
		else:
			normalisedValue = (value - middleValue) / (maxValue - middleValue)
			resultingColour = averageColour(normalisedValue, middleColour, maxColour)
		
	if value >= maxValue:
		resultingColour = maxColour
		
	return resultingColour

#------------------------------------------------------

def averageColour(normalisedValue = 0.5, colour1 = "#000000", colour2 = "#ffffff"):
	
	if normalisedValue < 0: normalisedValue = 0
	if normalisedValue > 1: normalisedValue = 1
	
	red1, green1, blue1 = divideColour(colour1)
	red2, green2, blue2 = divideColour(colour2)
	
	newRed = middleValue(normalisedValue, [0.0, red1], [1.0, red2])
	newGreen = middleValue(normalisedValue, [0.0, green1], [1.0, green2])
	newBlue = middleValue(normalisedValue, [0.0, blue1], [1.0, blue2])
	
	newColour = hexRGBFromDecimal(newRed, newGreen, newBlue)
	
	return newColour
	
#------------------------------------------------------

def hexRGBFromDecimal(decRed, decGreen, decBlue):

	intRed = int(round(decRed))
	intGreen = int(round(decGreen))
	intBlue = int(round(decBlue))
	
	if intRed > 255: intRed = 255
	if intGreen > 255: intGreen = 255
	if intBlue > 255: intBlue = 255
	
	if intRed < 0: intRed = 0
	if intGreen < 0: intGreen = 0
	if intBlue < 0: intBlue = 0
	
	hexRed = dec2hex(intRed)
	hexGreen = dec2hex(intGreen)
	hexBlue = dec2hex(intBlue)
	
	hexRGB = "#" + hexRed + hexGreen + hexBlue
	
	return hexRGB

#------------------------------------------------------

def dec2hex(decValue):
	
	# only for values between 2 and 255!!
	# decValue must be an integer
	
	hexValue = hex(decValue).split('x')[1]
	if len(hexValue) == 1:
		hexValue = "0" + hexValue
	
	return hexValue

#------------------------------------------------------

def divideColour(hexColour):
	
	hexRed = hexColour[1:3]
	hexGreen = hexColour[3:5]
	hexBlue = hexColour[5:7]
	
	decRed = float(int(hexRed, 16))
	decGreen = float(int(hexGreen, 16))
	decBlue = float(int(hexBlue, 16))
	
	return decRed, decGreen, decBlue

#------------------------------------------------------

def nodeColourReduced(colourList):
	
	splitColours = colourList.split(":")
	
	i = 0
	while i < len(splitColours) - 1:
	
		currentColour = splitColours[i].split(";")[0]
		nextColour = splitColours[i + 1].split(";")[0]
		if currentColour == nextColour:
		
			sizeColour = float(splitColours[i].split(";")[1]) + float(splitColours[i + 1].split(";")[1])
			newColour = "%s;%f" % (currentColour, sizeColour)
			del splitColours[i]
			splitColours[i] = newColour
			
		else: i += 1
	
	newColourList = ""
	for i in xrange(len(splitColours)):
		newColourList += splitColours[i] + ":"
	
	newColourList = newColourList[:-1]
	
	return newColourList

#------------------------------------------------------

def getNodeColour(node,
					defaultColour = "#FFFFFF",
					extraData = None,
					colouringVariableIndex = 1.0,
					minValue = 0.0,
					middleValue = 0.5,
					maxValue = 1.0,
					minColour = "#00ff00",
					middleColour = "#ffffff",
					maxColour = "#ff0000"):

	nodeColour = defaultColour
	
	if extraData:
		# this needs to be implemented ****
		nodeIndex = -1
		for i in xrange(len(extraData)):
			if node == extraData[i][0]:
				nodeIndex = i
				break
				
		if nodeIndex > -1:

			nodeColour = extrapolateColour(float(extraData[nodeIndex][colouringVariableIndex]),
					minValue = minValue,
					middleValue = middleValue,
					maxValue = maxValue,
					minColour = minColour,
					middleColour = middleColour,
					maxColour = maxColour)

	return nodeColour
	
#------------------------------------------------------
	
def getFromIni(iniFile, variableName):
	
	result = ""
	if os.path.exists(iniFile):
		iniText = load2stringList(iniFile)
		for line in iniText:
			element = line[0]
			if len(element) > 0 and "=" in element and element.strip()[0] != "#":
				parts = element.split("=")
				if parts[0].strip().lower() == variableName.strip().lower():
					result = parts[1].strip()
					break
					
	return result

#------------------------------------------------------

def getNodeFontSize(NValue,
					NMax = 1000,
					NMin = 2,
					normalFontSize = 14.0,
					maxFontSize = 50.0,
					minFontSize = 10.0):
	
	if NMax == NMin: return normalFontSize
	if NValue <= 0: return normalFontSize
	
	point1 = [math.log(NMin), minFontSize]
	point2 = [math.log(NMax), maxFontSize]
	
	fontSize = middleValue(math.log(NValue), point1, point2)
	
	if fontSize <= minFontSize: return minFontSize
	if fontSize >= maxFontSize: return maxFontSize
	
	return fontSize
	
#------------------------------------------------------

def removeHeader(myList):

	if len(myList) > 0:
		myList.remove(myList[0])
	
	return myList

#------------------------------------------------------
def load2dictionary(fileName, keyNum, n1, n2 = -1, n3 = -1, n4=-1, n5=-1, splitter = "\t", lineFeed = "\n"):
	
	dic = {}
	with open(fileName) as file:
		next(file)
		for line in file:
			if line != lineFeed:
				splits=line.split(splitter)
				keyField = splits[keyNum].strip()
				if n5 >=0 and n4 >=0 and n3>=0 and n2>=0:
					dic[keyField]=[splits[n1].strip(), splits[n2].strip(), splits[n3].strip(), splits[n4].strip(), splits[n5].strip()]
				else:
					if n4 >=0 and n3>=0 and n2>=0:
						dic[keyField]=[splits[n1].strip(), splits[n2].strip(), splits[n3].strip(), splits[n4].strip()]
					else:
						if n3 >= 0 and n2 >=0:
							dic[keyField]=[splits[n1].strip(), splits[n2].strip(), splits[n3].strip()]
						else:
							if n2 >=0:
								dic[keyField]=[splits[n1].strip(),splits[n2].strip()]
							else:
								dic[keyField]=[splits[n1].strip()]
	return dic
#------------------------------------------------------

# load any _tab separated values_ file
def load2stringList(fileName, removeCommas = False, splitChar = "\t"):
	
	reader = open(fileName, "r")
	fullList = []
	
	for myRow in reader:
	
		myRowStrip = myRow.strip()
		
		if len(myRowStrip) > 0:
			thisRow = myRowStrip.split(splitChar)
			
			for i in xrange(len(thisRow)):
				thisRow[i] = thisRow[i].strip()
				
			if removeCommas:
				for i in xrange(len(thisRow)):
					if thisRow[i].endswith('"') and thisRow[i].startswith('"'):
						thisRow[i] = thisRow[i][1:len(thisRow[i]) - 1]
			
			fullList.append(thisRow)

	return fullList

#------------------------------------------------------

def arrangeSubData(inStats = "",
					uFile = "",
					relFile = "",
					higherElements = None,
					relations = None,
					ignoreNaNsInFDR = False):
	
	results = []
	
	if not relations:
		relations = loadRelationsFile(relFile)
		
	relations = sortByIndex(relations, 0)
	
	statsData = loadStatsDataFile(inStats, FDRasText = ignoreNaNsInFDR)
	
	if not higherElements:
		higherElements = load2stringList(uFile, removeCommas = True)
	
		if higherElements[0] == ['id', 'Z', 'n'] \
			or higherElements[0] == ['id', 'n', 'Z', 'FDR'] \
			or higherElements[0] == ['id', 'n', 'Z', 'FDR', 'X']:
			# this means the list comes from SanXoTSqueezer
			# so the header and the extra columns have to be removed
			higherElements = extractColumns(higherElements[1:], 0)
		else:
			# only removing extra columns and converting list into text
			higherElements = extractColumns(higherElements, 0)
		
	statsData = sortByIndex(statsData, 7)
	
	ZijList = []
	for element in statsData:
		ZijList.append([element[3], element[7]])
	
	# to be implemented to avoid not a numbers
	# # this is a trick to remove "not a number" element fast
	# for i in xrange(len(ZijList)):
		# if str(ZijList[i][1]).lower() == "nan":
			# ZijList[i][1] = sys.float_info.max
			
	# ZijList = sortByIndex(ZijList, 2)
	
	# try:
		# NaNindex = stats.firstIndex(ZijList, sys.float_info.max)
		# ZijList = ZijList[0:NaNindex - 1]
	# except:
		# pass
	
	theorList = []
	experList = []
	N = len(ZijList)
	for i in xrange(N):
		theorList.append([ZijList[i][0], ZijList[i][1], norm.cdf(float(ZijList[i][1]))])
		experList.append([ZijList[i][0], ZijList[i][1], (float(i) + 0.5) / float(N)])
	
	results.append(['Theoretical', theorList])
	results.append(['Experimental', experList])
	
	relationsFirstColumn = extractColumns(relations, 0)
	relationsSecondColumn = extractColumns(relations, 1)
	experListFirstColumn = extractColumns(experList, 0)
	
	for uElement in higherElements:
		lowerElementList = []
		first = firstIndex(relationsFirstColumn, uElement)
		
		if first > -1: # -1 means it is not in the list
			notInList = 0
			last = lastIndex(relationsFirstColumn, uElement)
			lowerElements = relationsSecondColumn[first:last + 1] # "+1" is to include the last one
			for element in lowerElements:
				lowerIndex = firstIndex(experListFirstColumn, element)
				if lowerIndex > -1: # -1 means it is not in the list
					Zlower = experList[lowerIndex][1]
					lowerElementList.append([element, Zlower])
				else:
					notInList += 1
				
			lowerElementList = sortByIndex(lowerElementList, 1)
			
			# now we add the rank/N
			# N = len(lowerElementList) [it should coincide]
			N = last - first + 1 - notInList
			rank = 0.5
			for element in lowerElementList:
				rankNlower = rank / float(N)
				element.append(rankNlower)
				rank += 1
				
			results.append([uElement, lowerElementList])
			
		else:
			results.append([uElement, None])
	
	return results, ""

#------------------------------------------------------

def createBigTable(data = None):
	
	# used by SanXoTGauss and Sanson
	
	bigTable = []
	extraTable = []
	header1 = ""
	header2 = ""
	
	# data[j][0] contains the name of the category
	# each data[j][1][i] contains a list with [id, Zij, rank/N]
	for j in xrange(len(data)):
		if j == 0:
			header1 += str(data[0][0]) + "\t\t\t"
			header2 += "id\tZ\tp\t"
			for subData in data[0][1]:
				bigTable.append(subData)
		else:
			header1 += str(data[j][0]) + "\t\t\t"
			header2 += "id\tZ\trank/N\t"
			for i in xrange(len(bigTable)):
				if type(data[j][1]) == type([]):
				
					if i < len(data[j][1]):
					
						bigTable[i].extend(data[j][1][i])
						
						if j > 1:
							newRow = []
							newRow.append(data[j][0])
							newRow.extend(data[j][1][i])
							extraTable.append(newRow)
							
					if i >= len(data[j][1]):
						bigTable[i].extend(['','',''])
				else: # NoneType -> this means the uLevel was not present
					bigTable[i].extend(['','',''])
	
	header = header1 + "\n" + header2
	extraHeader = "idsup\tidinf\tZ\trank/N"
	
	return bigTable, header, extraTable, extraHeader
	
#------------------------------------------------------
	
def stringList2inputDataFile_old(input):
	
	result = []
	
	for myRow in input:
		# if it is an inputRawDataFile, it should be str - float - float
		resultRow = []
		resultRow.append(myRow[0]) # identificator, such as raw-scannumber-charge string
		
		# *** next line should be general to avoid any text
		if myRow[1].lower() != "neun" and myRow[2].lower != "neun" and myRow[1].lower() != "nan" and myRow[2].lower() != "nan":
			resultRow.append(float(myRow[1])) # Xi
			resultRow.append(float(myRow[2])) # Vs
			
			result.append(resultRow)
	
	return result
	
#------------------------------------------------------
	
def stringList2inputDataFile(input, format = ['s', 'f', 'f'], fillEmptyPositions = False, emptyFiller = ""):
	
	result = []
	
	counter = 0
	for myRow in input:
		# if it is an inputRawDataFile, it should be str - float - float
		if fillEmptyPositions or len(myRow) >= len(format):
			resultRow = []
			
			if len(format) > 0:
				for i in xrange(len(format)):
					if i > len(myRow) - 1:
						resultRow.append(emptyFiller)
					else:
						stringy = myRow[i].strip()
						if format[i] == 's':
							resultRow.append(stringy)
						elif format[i] == 'f' or format[i] == 'i':
							if len(stringy) > 0 and \
								((stringy[0] >= '0' and stringy[0] <= '9') or \
								(stringy[0] == '-' and (stringy[1] >= '0' and stringy[1] <= '9'))):
								if format[i] == 'f': resultRow.append(float(stringy))
								if format[i] == 'i': resultRow.append(int(stringy))
							else:
								# if a row that is supposed to contain a float or an int
								# is empty, or there is an error while reading it,
								# the row is not read but the program keeps going
								resultRow = []
								break
			
			if len(resultRow) > 0:
				result.append(resultRow)
	
	return result

#------------------------------------------------------
	
def loadInputDataFile(fileName):
	
	result = load2stringList(fileName, removeCommas = True)
	result = removeHeader(result)
	dataInput = stringList2inputDataFile(result)
	
	return dataInput

#------------------------------------------------------

def loadStatsDataFile(fileName, FDRasText = False, ZasText = False, includeTags = False):
	
	fillEmptyPositions = False
	FDRformat = "f"
	Zformat = "f"
	
	if FDRasText: FDRformat = "s"
	if ZasText: Zformat = "s"
	
	result = load2stringList(fileName, removeCommas = True)
	result = removeHeader(result)
	formatToUse = ['s', 'f', 'f', 's', 'f', 'f', 'i', Zformat, FDRformat]
	if includeTags:
		formatToUse = ['s', 'f', 'f', 's', 'f', 'f', 'i', Zformat, FDRformat, 's']
		fillEmptyPositions = True # so if there are no tags, an empty string is added
	
	# FDRasText and ZasText solves the problem occurring when FDR contains NaNs
	# which makes the program skip the concerning line
	dataInput = stringList2inputDataFile(result, format = formatToUse, fillEmptyPositions = fillEmptyPositions)
	
	return dataInput
	
#------------------------------------------------------
	
def loadRelationsFile(fileName):
	
	result = load2stringList(fileName, removeCommas = True)
	result = removeHeader(result)
	
	return result

#------------------------------------------------------

class Relation: # currently unused
		
	def __init__(self, rel):
		self.id1 = rel[1]
		self.id2 = rel[0]

#------------------------------------------------------

def removeRedundantUpper(mergedList):

	# mergedList should arrive here ordered. Otherwise, a line for sorting should be inserted here
	relationsClone = mergedList[:]
	
	# generate higherList
	# higherList is just a list of categories containing
		# 1) name of higher level element (category)
		# 2) number of lower level elements (proteins) associated to it
		# 3) boolean (initialisated as "False")
		# 4) the list of lower elements (proteins)

	currHigher = relationsClone[0][0]
	higherList = []
	lowerList = [relationsClone[0][1]]
	for i in xrange(len(relationsClone)):
		if i >= 0:
			if relationsClone[i][0] != currHigher:
				lowerList.sort()
				higherElement = [currHigher, len(lowerList), False, lowerList]
				higherList.append(higherElement)
				currHigher = relationsClone[i][0]
				lowerList = [relationsClone[i][1]]
			else:
				lowerList.append(relationsClone[i][1])
				
	# then add the last element for the higherList
	lowerList.sort()
	higherElement = [currHigher, len(lowerList), False, lowerList]
	higherList.append(higherElement)
	
	# create list of removed (duplicated) higher level elements
	newList = []
	maxLower = max(extractColumns(higherList, 1))
	for i in xrange(maxLower):
		shortList = filterByElement(higherList, i + 1, 1)
		for j in xrange(len(shortList)):
			for k in xrange(len(shortList)):
				if k > j and shortList[k][2] == False:
					if shortList[j][3] == shortList[k][3]:
						shortList[k][2] = True
						newList.append(shortList[k][0])
	
	newMergedList = []
	for i in xrange(len(relationsClone)):
		if not relationsClone[i][0] in newList:
			newMergedList.append(relationsClone[i])
	
	return newMergedList

#------------------------------------------------------

def mergeInput(inputData, inputRelations, hideWarnings = True, removeDuplicateUpper = False):
	
	# inputData must be in the form
	#	[[id1, X1, V1, other things], ...]
	# inputRelations must be in the form
	#	[[id2, id1], ...]
	# also IMPORTANT: all the id1 in inputRelations should be within inputData
	# (but the opposite is not needed: there can be data without a relation,
	# it just will not appear in the resulting list)
	
	inputData.sort()
	inputRelations.sort(key = lambda x: str(x[1]))
	#sorted(inputRelations, key = lambda inputRelations: inputRelations[1])
	
	result = []
	counter = 0
	
	for row in inputData:
		
		rowUsed = False
		tags = ""
		id1 = row[0]
		
		# move counter to next id1
		while inputRelations[counter][1] < id1:
			counter += 1
			
			if counter >= len(inputRelations):
				break
		
		if counter >= len(inputRelations):
				break
		
		while inputRelations[counter][1] == id1:
			
			rowUsed = True
			id2 = inputRelations[counter][0]
			
			if len(inputRelations[counter]) > 2: tags = inputRelations[counter][2]
			# next three lines are a fast way to insert a column on first position
			newRow = row[::-1]
			newRow.append(id2)
			newRow = newRow[::-1]
			newRow.append(tags)
			
			result.append(newRow)
			
			counter += 1
			
			if counter >= len(inputRelations):
				break
		
		if not hideWarnings and not rowUsed:
			print "Warning: some input data element(s) have not been used,"
			print "such as: " + id1
			hideWarnings = True
		
		if counter >= len(inputRelations):
			break
	
	result.sort()
	
	removedList = None
	if removeDuplicateUpper:
		result = removeRedundantUpper(result)

	return result

#------------------------------------------------------

def addTagToRelations(relations, relationsToTag, tagToAdd = "unspecifiedTag"):

	newRelations = relations[:]
	
	if len(relationsToTag) > 0:
		for eachRelation in relationsToTag:
			for i in xrange(len(newRelations)):
				if newRelations[i][0] == eachRelation[0] and newRelations[i][1] == eachRelation[1]:
					if len(newRelations[i]) > 2:
						if not tagIsPresent(newRelations[i][2], tagToAdd):
							newRelations[i][2] += ", " + tagToAdd
					else:
						newRelations[i].append(tagToAdd)
	
	return newRelations
	
#------------------------------------------------------

def tagIsPresent(tagString, tagToCheck, caseSensitive = True, tagSeparator = ","):
	
	tagList = tagString.split(tagSeparator)
	
	for tagElement in tagList:
		if tagElement.strip() == tagToCheck:
			return True
		else:
			if not caseSensitive:
				if tagElement.strip().lower() == tagToCheck.lower():
					return True
			
	return False

#------------------------------------------------------
	
def mergeInput_old(inputData, inputRelations):
	
	# inputData must be in the form
	#	[[id1, X1, V1, other things], ...]
	# inputRelations must be in the form
	#	[[id2, id1], ...]
	
	inputData.sort()
	inputRelations.sort()
	input = []
	relations2 = []
	
	for element in inputRelations:
		relations2.append(element[1])
	
	for element in inputData:
	
		id1 = element[0]
		try:
			id1index = relations2.index(id1)
		except:
			id1index = -1
		
		if id1index > -1:
			id2 = inputRelations[id1index][0]
			relations2[id1index] = None
			element.insert(0, id2)
			input.append(element)
	
	input.sort()
	
	return input	
	
#------------------------------------------------------

# deprecated, to be removed ***
def loadFile(fileName):

	reader = open(fileName, "r")
	myList = []

	for myRow in reader:
		provList = []
		newProvList = []
		provList.append(myRow.split("\t"))
		if provList[0][2] <> "NeuN" and provList[0][3] <> "NeuN":
			newProvList.append(provList[0][0])
			newProvList.append(provList[0][1])
			newProvList.append(float(provList[0][2]))
			newProvList.append(float(provList[0][3]))
			myList.append(newProvList)

	reader.close()

	myList.sort()
	
	return myList

#------------------------------------------------------

def saveRow(writer, rowList):

	line = ""
	for element in rowList:
		line += str(element) + "\t"
		
	line = line[:-1] # to remove last \t
	line += "\n"
	writer.write(line)
	
	return

#------------------------------------------------------

def saveFile(fileName, list, header = ""):

	writer = open(fileName, "w")
	if len(header) > 0:
		writer.write(header + "\n")
	
	for row in list: saveRow(writer, row)
	
	writer.close()
	
	return

#------------------------------------------------------	

def saveTextFile(fileName, textToSave):

	writer = open(fileName, "w")
	writer.write(textToSave)
	writer.close()
	
	return
	
#------------------------------------------------------

def getNextX(XWchunk):
	
	# XWchunk is in the form
	# [[x1, w1], [x2, w2], ...]
	
	sumXW = 0
	sumW = 0
	
	for bit in XWchunk:
		
		x1 = bit[0]
		w1 = bit[1]
		sumXW = sumXW + x1 * w1
		sumW = sumW + w1

	x2 = sumXW / sumW
	
	return x2
	
#------------------------------------------------------

def filterByElement(list, id, index = 0, firstElement = 0, sort = True, method = 'binsearch'):

	if list == []: return []
	
	method = method.lower()
	if sort: list = sortByIndex(list, index)

	# *** extract columns is not needed now
	# change and remove firstIndex
	
	if method == 'old':
		idList = extractColumns(list, index)
		
		firstElement = firstIndex(idList, id, starting = firstElement)
		lastElement = lastIndex(idList, id)
		
	if method == 'fast':
		# list should be already sorted when we get here
		#
		# and should be list[firstElement][index] == id
		# otherwise it returns []

		lastElement = firstElement
		selection = []
		
		for element in list[firstElement:]:
			if element[index] == id:
				lastElement += 1
			else:
				break
		
		lastElement -= 1
	
	if method == 'binsearch' or method == 'binarysearch': # binary search
		# list should be ordered here
		# li = [['f',3,4.5],['d',65,3.3],['r',1.2,4.5],['d',65,3]]
		# stats.filterByElement(li, 2, index = 1, method = 'binsearch')

		epsilon = 0.01
		delta = float(len(list)) / 2
		alef = delta
		while delta > epsilon:
			delta = delta / 2
			if list[int(alef)][index] == id:
				break
			elif list[int(alef)][index] < id:
				alef += delta
			elif list[int(alef)][index] > id:
				alef -= delta
		
		firstElement = int(alef)
		lastElement = int(alef)
		
		firstChanged = False
		while list[firstElement][index] == id:
			firstChanged = True
			firstElement -= 1
			if firstElement < 0: break
		
		if firstChanged:
			firstElement += 1
		
		lastChanged = False
		while list[lastElement][index] == id:
			lastChanged = True
			lastElement += 1
			if lastElement >= len(list): break
		
		if lastChanged:
			lastElement -= 1
	
	selection = list[firstElement:lastElement + 1]
	
	if len(selection) == 1:
		if(selection[0][index] != id):
			selection = []
	
	return selection

#------------------------------------------------------

def getNextXW(XWchunk, variance):
	
	# XWchunk is in the form
	# [[x1, w1], [x2, w2], ...]
	
	sumXW = 0
	sumW = 0
	
	for bit in XWchunk:
	
		x1 = bit[0]
		w1 = bit[1]
		sumXW = sumXW + x1 * w1
		sumW = sumW + w1
	
	x2 = sumXW / sumW
	w2 = 1 / ((1 / sumW) + variance)
	
	return [x2, w2]

#------------------------------------------------------

def lastIndex(list, element):
	return len(list) - 1 - list[::-1].index(element)

#------------------------------------------------------

def firstIndex(list = [],
				element = "",
				index = 0,
				starting = 0,
				method = 'simple',
				listWithId = []):

	if len(str(element)) == 0:
		result = -1
	else:
		if method == 'simple':
			try:
				if len(list) == 0 and len(listWithId) > 0:
					list = extractColumns(listWithId, 0)
					
				result = list[starting:].index(element)
			except:
				result = -1
			
		if method == 'binsearch': # binary search
			try:
				newList = []
				if len(listWithId) == 0:
					for i in xrange(len(list)):
						newList.append([list[i], i])
					newList = sortByIndex(newList, 0)
					listWithId = newList[:]
					
				filteredIndexes = filterByElement(listWithId,
													id = element,
													index = 0,
													firstElement = starting,
													sort = False,
													method = 'binsearch')
				indexColumn = extractColumns(filteredIndexes, 1)
				indexColumn.sort()
				result = indexColumn[0]
			except:
				result = -1

	if len(listWithId) > 0:
		return result, listWithId
	else:
		return result

#------------------------------------------------------

def middleValue(value, point1, point2):
	
	x1 = point1[0]
	y1 = point1[1]
	x2 = point2[0]
	y2 = point2[1]
	
	if x2 != x1:
	
		slope = (y2 - y1) / (x2 - x1)
		intercept = y1 - slope * x1
		
		result = slope * value + intercept
		
	else:
	
		result = (y2 + y1) / 2.0
	
	return result
	
#------------------------------------------------------

def insertText(original, new, pos):
  '''Inserts new inside original at pos.'''
  # from http://twigstechtips.blogspot.com/2010/02/python-insert-string-into-another.html
  return original[:pos] + new + original[pos:] 
  
#------------------------------------------------------

def sortByIndex(list, index, index2 = -1):
	if index2 == -1:
		return sorted(list, key=lambda list: list[index])
	else:
		return sorted(sortByIndex(list, index2), key=lambda list: list[index])

#------------------------------------------------------

def sortByInstance(list, instanceName, isDescendent = False):	

	list.sort(key = operator.attrgetter(instanceName), reverse = isDescendent)
	
	return list
	
#------------------------------------------------------

def removeRows(myList, element, index = 0):
	
	newList = myList[:]
	for row in newList:
		if row[index] == element:
			newList.remove(row)
			
	return newList
	
#------------------------------------------------------

def median(list): # for lists of lists use medianByIndex
	list.sort()
	if len(list) % 2 == 0:
		med = (list[len(list) / 2 - 1] + list[len(list) / 2]) / 2
	else:
		med = list[(len(list) - 1) / 2]
	
	return med

#------------------------------------------------------
	
def medianByIndex(list, index = 0):
	list = sortByIndex(list, index)
	
	if len(list) % 2 == 0:
		med = (list[len(list) / 2 - 1][index] + list[len(list) / 2][index]) / 2
	else:
		med = list[(len(list) - 1) / 2][index]
	
	return med

#------------------------------------------------------

# deprecated, use extractColumns instead
def extractFromList(list, index):
	newlist = []
	for item in list:
		newlist.append(item[index])
	
	return newlist
	
#------------------------------------------------------

def forstep(start, stop, step):
	r = start
	
	if start != stop:
		while r < stop:
			yield r
			r += step
	else:
		yield r
	
	
#------------------------------------------------------

def isParetoFront(xy = [0, 0], dataList = []):

	# {x0, y0} is in the pareto front if it has, for the list, either
	#	the highest Y for all the X >= x0, or
	#	the highest X for all the Y >= y0
	
	# warning: when number of proteins in category is not included
	#   (case of custom lists), the Pareto front cannot be calculated,
	#   as it gets a NaN (not a number)
	if str(xy[0]).lower() == "nan":
		return False
	
	if len(dataList) == 0 or len(xy) != 2:
		return False
	
	for xyList in dataList:
		if xyList[0] > xy[0] and xyList[1] > xy[1]:
			return False
	
	return True
	
#------------------------------------------------------
def extractColumns(list, n1, n2 = -1, n3 = -1, n4 = -1):
	
	newlist = []
	
	if n2 < 0:
		for element in list:
			newlist.append(element[n1])
	elif n3 < 0:
		for element in list:
			newlist.append([element[n1], element[n2]])
	elif n4 < 0:
		for element in list:
			newlist.append([element[n1], element[n2], element[n3]])
	else:
		for element in list:
			newlist.append([element[n1], element[n2], element[n3], element[n4]])
			
	return newlist

#------------------------------------------------------

def filterRelations(relations = [], tags = "", logicOperatorsAsWords = False):
	
	relationsAccepted = []
	relationsExcluded = []
	
	tags = tags.strip()
	
	for relation in relations:
		# fix this to include more tags and conditions
		# fix to make it faster by sorting first
		tagsInFile = ""
		if len(relation) > 2: tagsInFile = relation[2].strip()
		if tagFound(tags, tagsInFile, logicOperatorsAsWords = logicOperatorsAsWords):
			relationsAccepted.append(relation)
		else:
			relationsExcluded.append(relation)

	return relationsAccepted, relationsExcluded

#------------------------------------------------------

def splitTags(tags = "", separator = ","):
	
	tagList = tags.split(separator)
	newList = []
	
	for tag in tagList:
		tag = tag.strip()
		if len(tag) > 0: newList.append(tag)
		
	return newList

#------------------------------------------------------

def tagFound_old(tagCondition = "", tagInRow = ""):
	
	# for comparisons, to be removed
	tagFoundResult = False
	tagInRow = tagInRow.strip() # just in case
	
	if tagCondition.startswith("!"):
		restOfCondition = tagCondition[1:].strip()
		tagFoundResult = not tagFound(restOfCondition, tagInRow)
	else:
		tagFoundResult = (tagCondition == tagInRow)
	
	return tagFoundResult

#------------------------------------------------------

def tagFound(tagCondition = "", tagInRow = "", tagList = [], logicOperatorsAsWords = False):

	tagCondition = tagCondition.strip()
	tagInRow = tagInRow.strip()
	
	alternativeAnd = "*and*"
	alternativeOr = "*or*"
	
	if tagCondition == "False": return False
	if tagCondition == "True": return True
	
	tagFoundResult = False
	if len(tagList) == 0 and len(tagInRow) > 0:
		tagList = splitTags(tagInRow)
			
	if "(" in tagCondition and not ")" in tagCondition:
			print "Wrong parentheses"
			return False
			
	if ")" in tagCondition:
		endPos = tagCondition.find(")")
		subConditionFirst = tagCondition[:endPos]
		if "(" in subConditionFirst:
			startPos = len(subConditionFirst) - subConditionFirst[::-1].find("(")
			subCondition = tagCondition[startPos:endPos]
			newTagCondition = tagCondition[:startPos-1].strip() + str(tagFound(subCondition, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords)) + tagCondition[endPos+1:].strip()
			return tagFound(newTagCondition, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords)
		else:
			print "Wrong parentheses"
			return False
			
	if "&" in tagCondition:
		andPos = tagCondition.find("&")
		firstPart = tagCondition[:andPos]
		lastPart = tagCondition[andPos + 1:]
		return tagFound(firstPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords) and tagFound(lastPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords)
			
	if logicOperatorsAsWords and alternativeAnd in tagCondition:
		andPos = tagCondition.find(alternativeAnd)
		firstPart = tagCondition[:andPos]
		lastPart = tagCondition[andPos + len(alternativeAnd):]
		return tagFound(firstPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords) and tagFound(lastPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords)
	
	if "|" in tagCondition:
		orPos = tagCondition.find("|")
		firstPart = tagCondition[:orPos]
		lastPart = tagCondition[orPos + 1:]
		return tagFound(firstPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords) or tagFound(lastPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords)
	
	if logicOperatorsAsWords and alternativeOr in tagCondition:
		orPos = tagCondition.find(alternativeOr)
		firstPart = tagCondition[:orPos]
		lastPart = tagCondition[orPos + len(alternativeOr):]
		return tagFound(firstPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords) or tagFound(lastPart, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords)
	
	if tagCondition.startswith("!"):
		restOfCondition = tagCondition[1:].strip()
		return not tagFound(restOfCondition, tagList = tagList, logicOperatorsAsWords = logicOperatorsAsWords)
	
	return (tagCondition in tagList)
	
	return tagFoundResult
	
#------------------------------------------------------

def mergeLists(list1, list2, index1, index2):
	
	result = []
	
	list1.sort()
	list2.sort()
	
	for element in list2:
		id2 = element[index2]

#------------------------------------------------------

def getIdXW(idXWall, relations, variance, giveMergedData = False, removeDuplicateUpper = False):
	
	id2XW = []
	
	# no need to sort: mergeInput will do it anyway
	# idXVall.sort()
	# relations.sort()
	
	mergedData = mergeInput(idXWall, relations, removeDuplicateUpper = removeDuplicateUpper)

	position = 0
	id2old = ""
	
	XWlist = []
	while position < len(mergedData):
		
		id2 = mergedData[position][0]
		
		if id2 != id2old and len(XWlist) > 0:
			
			x2w2 = getNextXW(XWlist, variance)
			x2 = x2w2[0]
			w2 = x2w2[1]
			id2XW.append([id2old, x2, w2])
			XWlist = []
		
		else:
			
			XWspecific = [mergedData[position][2], mergedData[position][3]]
			XWlist.append(XWspecific)
			position += 1
		
		id2old = id2
	
	# the last one has not been added, so...
	
	x2w2 = getNextXW(XWlist, variance)
	x2 = x2w2[0]
	w2 = x2w2[1]
	id2XW.append([id2old, x2, w2])
	
	if giveMergedData:
		return [id2XW, mergedData]
	else:
		return id2XW
	
#######################################################

if __name__ == "__main__":
	print
	print """This is stats %s.
	
It is a library used by SanXoT and its satellite programs, a software package
created in the Jesus Vazquez Cardiovascular Proteomics Lab at Centro Nacional
de Investigaciones Cardiovasculares.

Check the help of the other individual programs for more info.
""" % version()
