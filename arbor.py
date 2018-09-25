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
Este sitio escogió el caballero de la Triste Figura para hacer su penitencia,
y así, en viéndole, comenzó a decir en voz alta, como si estuviera sin juicio: 
[...] ¡Oh solitarios árboles, que desde hoy en adelante habéis de hacer
compañía a mi soledad: dad indicio, con el blando movimiento de vuestras ramas,
que no os desagrade mi presencia!

Don Quixote, Part One, Chapter XXV."""

#------------------------------------------------------

# in
# table_allPaths.xls de GOconnect
# outList de SanXoTSqueezer
# para colorear (usando FDR y Z):
#	* ¿outStats de la integración de categoría a all?
#	* ¿outHigher de integración de proteína a categoría?
# descartado: ¿colorear con n y Z de outList? --> no, porque no tiene categorías intermedias

# out
# archivo de texto en DOT que pueda leer GVEdit for Graphviz


# leer archivo allPaths
# quedarse sólo con las relaciones que contengan las categorías de interés -> in: allPaths, outList; out: subList (lista de listas con categorías)
# repartir dichas relationes en grupos de dos para hacer los nodos en createRelations
# 
# parte 1: crear nodos createNodes -> in: subList, criterio coloreador; out: nodesText (texto con parte para nodos, incluyendo colores, si los hay)
# parte 2: escribir relaciones entre nodos createRelations -> in: subList, out: linkText (texto con parte para relaciones)
# parte 3: terminar archivo createGVFile -> in: nodesText, linkText; out: GVFileText
# guardar GVFileText

def printHelp(version = None):
	
	print """
Arbor %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to
generate the tree graph of a set of categories, showing the position of a given
list of categories in the tree, along with category information.

Arbor needs four input files:

     * a stats file, the outStats file from SanXoT (using the -z command); if
	    this is omitted, then the tree will only distinguish the categories
          in the list from the other categories above them (not showing the
          values of the protein within the category).
     * a higher level list to graph (using the -c command)
     * a relations file (using -r command)
     * a list of links between higher level elements, such as the
          table_allPaths.xls from GOconnect (using the -b command)

And delivers three output files:

     * the graph in PNG format (default suffix: "_outTree.png")
     * the DOT language text file used to generate the graph (default suffix:
           "_outTree.gv")
     * a log file (default suffix: "_logFile")

Usage: arbor.py -z[stats file] -r[relations file] -c[higher level list file] -b[links file] [OPTIONS]

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the
                       stats file.
   -b, --biglist       A list of links between higher level elements, such as
                       the table_allPaths.xls from GOconnect. It must be a tab
                       separated values text file, containing any identifier
                       in the first column (this column will not be imported,
                       but originally it was intended to contain protein
                       identifiers for each path), containing in each row (from
                       the second column on) a possible path from top to the
                       most specific element.
   -c, --list=filename The text file containing the higher level elements whose
                       categories we want to relate. If the first element is
                       not taken, it might help saving the file with ANSI
                       format. If a header is used, then it must be in the form
                       "id>n>Z>FDR" or "id>Z>n" (where ">" means "tab").
   -d, --dotfile=filename
                       To use a non-default name for the text file in DOT
                       language, which is used to generate the graph.
   -g, --graphformat=string
                       File format for the similarity graph (default is "png").
   -G, --outgraph=filename
                       To use a non-default name for the graph file.
   -l, --graphlimits=integer
                       To set the +- limits of the most intense red/green
                       colours in the graph (default is 6).
   -L, --logfile=filename
                       To use a non-default name for the log file.
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
   -z, --outstats=filename
                       The outStats file from a SanXoT integration (optional,
                       see above).
					   
   --selectednodecolor=#rrggbb, --selectednodecolour=#rrggbb
   --defaultnodecolor=#rrggbb, --defaultnodecolour=#rrggbb
   --errornodecolor=#rrggbb, --errornodecolour=#rrggbb
   --mincolor=#rrggbb, --mincolour=#rrggbb
   --middlecolor=#rrggbb, --middlecolour=#rrggbb
   --maxcolor=#rrggbb, --maxcolour=#rrggbb
   
""" % version
	
	return

#------------------------------------------------------
	
def getSelectedList(bigList = None, higherElements = None):
	
	selectedList = []
	nodeList = []
	
	for listElement in higherElements:
		
		for i in xrange(len(bigList)):
			for pathNode in bigList[i]:
				
				if pathNode == listElement:
					selectedList.append(bigList[i][1:])
					# [1:] is here, because this way we avoid taking the protein,
					# which is in the first position
					bigList[i] = [] # to avoid rechecking this
					break
	
	return selectedList

#------------------------------------------------------

def getNodeList(selectedList = None):
	
	nodeList = []
	nodeNames = []
	
	for path in selectedList:
		for element in path:
			if not element in nodeList:
				nodeList.append(element)
	
	return nodeList

#------------------------------------------------------

def getArrowList(selectedList = None):
	
	parentChildren = []
	
	for path in selectedList:
		for i in xrange(len(path) - 1):
			if i < len(path):
				group = [path[i], path[i + 1]]
				if not group in parentChildren:
					parentChildren.append(group)
	
	return parentChildren

#------------------------------------------------------

def createNodes(nodeList = None,
				selectedElements = None,
				subData = None,
				ZLimit = 6.0,
				altMax = 5,
				selectedNodeColour = "#ff9090",
				defaultNodeColour = "#ffff80",
				errorNodeColour = "#8080ff",
				minColour = "#00ff00",
				middleColour = "#ffffff",
				maxColour = "#ff0000"):

	nodeListText = ""
	
	for i in xrange(len(nodeList)):
		altText = ""
		NText = ""
		NValue = -1
		node = nodeList[i]
		if node in selectedElements:
			if subData:
				nodePenWidth = 0
				
				elementNumber = -1
				for j in xrange(len(subData[0])):
					if subData[0][j][0] == node:
						elementNumber = j - 2
						break
				
				nodeColour, NValue, altText = stats.getNodeColourList(node,
												elementNumber = elementNumber,
												subData = subData,
												ZLimit = ZLimit,
												maxAltTextLinesPerSide = altMax,
												defaultNodeColour = defaultNodeColour,
												errorNodeColour = errorNodeColour,
												minColour = minColour,
												middleColour = middleColour,
												maxColour = maxColour)
			else:
				nodeColour = selectedNodeColour
				nodePenWidth = 1
		else:
			nodeColour = defaultNodeColour
			nodePenWidth = 1
		
		if NValue > 0:
			NText = "\n(n = %i)" % NValue

		line = """\t%s [label = "%s", tooltip = "%s", style = "rounded, filled, striped", penwidth = "%i", fillcolor = "%s", shape = "box"];\r\n""" % (stats.fixNodeName(node), stats.fixNodeNameLength(node) + NText, altText, nodePenWidth, nodeColour)
		
		nodeListText += line
	
	return nodeListText

#------------------------------------------------------
	
def createGVFileTree(bigList,
					higherElements,
					subData = None,
					ZLimit = 6.0,
					bgColour = "#ffffd8",
					altMax = 5,
					selectedNodeColour = "#ff9090",
					defaultNodeColour = "#ffff80",
					errorNodeColour = "#8080ff",
					minColour = "#00ff00",
					middleColour = "#ffffff",
					maxColour = "#ff0000"):
	
	subList = getSelectedList(bigList, higherElements)
	subList = removeChildren(subList, higherElements)
	arrowList = getArrowList(subList)
	nodeList = getNodeList(subList)
	
	nodesText = createNodes(nodeList,
							higherElements,
							subData = subData,
							ZLimit = ZLimit,
							altMax = altMax,
							defaultNodeColour = defaultNodeColour,
							errorNodeColour = errorNodeColour,
							minColour = minColour,
							middleColour = middleColour,
							maxColour = maxColour)
							
	linksText = createLinks(arrowList)
	
	GVFileText = """digraph categoryGraph {\n\tbgcolor = "%s";\n\n%s\n%s\n}""" % (bgColour, nodesText, linksText)
	
	return GVFileText

#------------------------------------------------------
	
def	createDOTTree(GVFile,
					graphFile,
					DOTProgramLocation = r"%ProgramFiles%\Graphviz2.30\bin",
					imageFormat = "png"):
	DOTIniPath = stats.joinLocationAndFile(os.path.dirname(os.path.realpath(__file__)), "dot.ini")
	DOTProgramLocationCheck = stats.getFromIni(DOTIniPath, "dotlocation")
	if len(DOTProgramLocationCheck) > 0: DOTProgramLocation = DOTProgramLocationCheck
	DOTProgram = stats.joinLocationAndFile(DOTProgramLocation, "dot.exe")
	DOTCommandLine = """"%s" -T%s "%s" -o"%s\"""" % (DOTProgram, imageFormat, GVFile, graphFile)
	
	try:
		subprocess.call(DOTCommandLine)
	except:
		print """
*** ERROR ***
The graph could not be generated, probably because the dot.exe program could
not be found. Please, check:

   1) that you have installed Graphviz,
      which is freely available at http://www.graphviz.org/
   2) that you have included the path of the program folder in the dot.ini
      file (which should be in the same folder as this program)
"""

#------------------------------------------------------

def removeChildren(subList, higherElements):
	
	newSubList = []
	for path in subList:
		lastHigher = 0
		for i in xrange(len(path)):
			if path[i] in higherElements:
				lastHigher = i
		newPath = path[:lastHigher + 1]
		newSubList.append(newPath)
	
	return newSubList

#------------------------------------------------------

def createLinks(linkList = None):
	
	nodeLinkText = ""
	
	for link in linkList:
		nodeParent = link[0]
		nodeChild = link[1]
		line = "\t%s -> %s;\r\n" % (stats.fixNodeName(nodeParent), stats.fixNodeName(nodeChild))
		nodeLinkText += line
	
	return nodeLinkText
	
#------------------------------------------------------

def main(argv):

	version = "v1.06"
	verbose = False
	showGraph = True
	showLegend = True
	analysisName = ""
	graphLimits = 6.0
	defaultAnalysisName = "arbor"
	analysisFolder = ""
	# input files
	inStats = ""
	useSubStats = False # True if inStats (-z) and relationsFile (-r) are provided
	bigListFile = ""
	defaultStatsFile = "stats"
	defaultRelationsFile = "rels"
	defaultTableExtension = ".tsv"
	defaultTextExtension = ".txt"
	defaultGVFileExtension = ".gv"
	relationsFile = ""
	listOfCategoriesFile = ""
	# output files
	defaultListOfCategoriesFile = "ulst"
	defaultBigListFile = "table_allPaths.tsv"
	defaultOutputFile = "outNodes"
	defaultOutputGraphFile = "outTree"
	defaultLogFile = "logFile"
	logFile = ""
	outputFile = ""
	graphFile = ""
	similarityMatrixFile = ""
	graphFileFormat = "png"
	altMax = 5
	
	selectedNodeColour = "#ff9090"
	defaultNodeColour = "#ffff80"
	errorNodeColour = "#8080ff"
	minColour = "#00ff00"
	middleColour = "#ffffff"
	maxColour = "#ff0000"
	
	logList = [["SanXoTGauss " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:p:z:c:d:l:L:b:G:r:g:N:h", ["analysis=", "folder=", "place=", "statsfile=", "list=", "dotfile=", "graphlimits=", "logfile=", "biglist=", "graphfile=", "relfile=", "relationsfile=", "graphformat=", "altmax=", "selectednodecolour=", "selectednodecolor=", "defaultnodecolour=", "defaultnodecolor=", "errornodecolour=", "errornodecolor=", "mincolour=", "mincolor=", "middlecolour=", "middlecolor=", "maxcolour=", "maxcolor=", "help", "egg", "easteregg"])
	except getopt.GetoptError:
		message = "Error while getting parameters."
		print message
		logList.append([message])
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
		elif opt in ("-c", "--list"): # outList from SanXoTSqueezer
			listOfCategoriesFile = arg
		elif opt in ("-d", "--dotfile"):
			dotFile = float(arg)
		elif opt in ("-l", "--graphlimits"):
			graphLimits = float(arg)
		elif opt in ("-L", "--logfile"):
			logFile = arg
		elif opt in ("-d", "--dotfile"):
			outputFile = arg
		elif opt in ("-G", "--graphfile"):
			graphFile = arg
		elif opt in ("-b", "--biglist"): # table_allPaths.xls from GOconnect
			bigListFile = arg
		elif opt in ("-r", "--relfile", "--relationsfile"):
			relationsFile = arg
		elif opt in ("-N", "--altmax"):
			altMax = int(arg)

		elif opt in ("-g", "--graphformat"):
			graphFileFormat = arg.lower().strip()
			if graphFileFormat == "jpeg": graphFileFormat = "jpg"
			if graphFileFormat != "png" and \
				graphFileFormat != "svg" and \
				graphFileFormat != "jpg" and \
				graphFileFormat != "gif":
				print
				print "Warning: graph format \"%s\" is not supported,\npng will be used instead." % graphFileFormat
				print
				graphFileFormat = "png"
		
		elif opt in("--selectednodecolour", "--selectednodecolor"):
			selectedNodeColour = arg
		elif opt in("--defaultnodecolour", "--defaultnodecolor"):
			defaultNodeColour = arg
		elif opt in("--errornodecolour", "--errornodecolor"):
			errorNodeColour = arg
		elif opt in("--mincolour", "--mincolor"):
			minColour = arg
		elif opt in("--middlecolour", "--middlecolor"):
			middleColour = arg
		elif opt in("--maxcolour", "--maxcolor"):
			maxColour = arg
		
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("--egg", "--easteregg"):
			easterEgg()
			sys.exit()

	if len(inStats) > 0 and len(relationsFile) > 0:
		useSubStats = True
		
# REGION: FILE NAMES SETUP

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
		
	if len(os.path.dirname(relationsFile)) == 0 and len(analysisFolder) > 0:
		relationsFile = os.path.join(analysisFolder, relationsFile)
	
	if len(listOfCategoriesFile) == 0:
		listOfCategoriesFile = os.path.join(analysisFolder, analysisName + "_" + defaultListOfCategoriesFile + defaultTextExtension)
	
	if len(os.path.dirname(listOfCategoriesFile)) == 0 and len(os.path.basename(listOfCategoriesFile)) > 0:
		listOfCategoriesFile = os.path.join(analysisFolder, listOfCategoriesFile)
	
	if len(bigListFile) == 0:
		bigListFile = defaultBigListFile
	
	if len(os.path.dirname(bigListFile)) == 0 and len(os.path.basename(bigListFile)) > 0:
		bigListFile = os.path.join(analysisFolder, bigListFile)
	
	# output
	if len(outputFile) == 0:
		outputFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputFile + defaultGVFileExtension)

	if len(graphFile) == 0:
		graphFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputGraphFile + defaultGraphExtension)
	
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
		
	if len(os.path.dirname(outputFile)) == 0 and len(os.path.basename(outputFile)) > 0:
		outputFile = os.path.join(analysisFolder, outputFile)
		
	if len(os.path.dirname(graphFile)) == 0 and len(os.path.basename(graphFile)) > 0:
		graphFile = os.path.join(analysisFolder, graphFile)
		
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)
		
	logList.append([""])
	logList.append(["Input stats file: " + inStats])
	logList.append(["File with categories to check: " + listOfCategoriesFile])
	logList.append(["Output GV table: " + outputFile])
	logList.append(["Output graph table: " + graphFile])
	logList.append(["Output log file: " + logFile])
	logList.append([""])
	
	# pp.pprint(logList)
	# sys.exit()

# END REGION: FILE NAMES SETUP
	
	bigList = stats.load2stringList(bigListFile, removeCommas = True)
	higherElements = stats.load2stringList(listOfCategoriesFile, removeCommas = True)
	
	if higherElements[0] == ['id', 'Z', 'n'] or higherElements[0] == ['id', 'n', 'Z', 'FDR']:
		# this means the list comes from SanXoTSqueezer
		# so the header and the extra columns have to be removed
		higherElements = stats.extractColumns(higherElements[1:], 0)
	else:
		# only removing extra columns and converting list into text
		higherElements = stats.extractColumns(higherElements, 0)
	
	if useSubStats:
		# añadir salida para log ***
		subData = stats.arrangeSubData(inStats = inStats,
						higherElements = higherElements,
						relFile = relationsFile,
						ignoreNaNsInFDR = False)
		
	else:
		subData = None
	
	GVFileText = createGVFileTree(bigList,
						higherElements,
						subData = subData,
						ZLimit = graphLimits,
						altMax = altMax,
						defaultNodeColour = defaultNodeColour,
						errorNodeColour = errorNodeColour,
						minColour = minColour,
						middleColour = middleColour,
						maxColour = maxColour)

	stats.saveTextFile(outputFile, GVFileText)
	
	createDOTTree(outputFile, graphFile, imageFormat = graphFileFormat,)
	
	stats.saveFile(logFile, logList, "LOG FILE")

#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])