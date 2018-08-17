import pdb
import sys
import getopt
import stats
import os
from scipy.stats import norm
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4)

#######################################################

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

def printHelp(version = None):

	print """
SanXoTgauss %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to
depict the sigmoids of lower level elements compared to their higher levels.
For example: when integrating proteins into categories, the outStats from the
protein confluence will be used along with a list of categories to compare the
sigmoid representing the proteins of each category.

SanXoTgauss needs three input files:

     * a stats file, the outStats file from SanXoT (using the -z command)
     * a higher level list to graph (using the -c command)
     * a relations file (using -r command)

And delivers four output file:

     * the data file used to draw gaussians (default suffix: "_outSigmoids")
     * an extra table with a different arrangement of the previous one (default
          suffix: "_extraTable")
     * the graph (default suffix: "_outGraph")
     * the log file (default suffix: "_logFile")

Usage: sanxotgauss.py -z[stats file] -r[relations file] -c[higher level list file] [OPTIONS]

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the
                       stats file.
   -c, --list=filename The text file containing the higher level elements whose
                       sigmoids we want to graph. If the first element is not
                       taken, it might help saving the file with ANSI format.
   -d, --graphdpi=integer
                       Set a non-default graph size in dpi (dots per inch).
                       Default is 300 dpi.
   -g, --no-graph      Do not show the sigmoids graph (the file will be saved
                       in any case).
   -G, --outgraph=filename
                       To use a non-default name for the graph file.
   -k, --no-legend     Do not show the legend in the graph (useful when the
                       legend covers the graph, in which case we might want to
                       save it twice: one with legend, and again without it).
   -l, --graphlimits=integer
                       To set the +- limits of the Zij graph (default is 6). If
                       you want the limits to be between the minimum and
                       maximum values, you can use -l.
   -L, --logfile=filename
                       To use a non-default name for the log file.
   -o, --outputfile=filename
                       To use a non-default file name for the sigmoid table.
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the stats file folder.
   -r, --relfile, --relationsfile=filename
                       Relations file, with identificators of the higher level
                       in the first column, and identificators of the lower
                       level in the second column.
   -s, --graphfontsize=float
                       Use a non-default value for legend font size. Default
                       is 8.
   -t, --graphtitle=string
                       The graph title (default is "Z plot").
   -T, --minimalgraphticks
                       It will only show the x secondary line for x = 0, and
                       none for the Y axis (useful for publishing).
   -W, --graphlinewidth=float
                       Use a non-default value for the sigmoid line width.
                       Default is 1.0.
   -x, --extratable=filename
                       To use a non-default file name for the extra table.
   -z, --outstats=filename
                       The outStats file from a SanXoT integration.
   -Z, --labelfontsize=float
                       The font size used for the labels in the X and Y axes.
                       (Default is 12.)
   --xlabel=string     Use the selected string for the X label. Default is
                       "Zij". To remove the label, use --xlabel=" ".
   --ylabel=string     Use the selected string for the Y label. Default is
                       "Rank/N". To remove the label, use --ylabel=" ".
""" % version

	return

#------------------------------------------------------

def main(argv):

	version = "v0.23"
	verbose = False
	showGraph = True
	graphLimits = 6.0
	showLegend = True
	graphDPI = 100 # default of Matplotlib's savefig method
	graphLineWidth = 1.0
	graphFontSize = 8
	analysisName = ""
	defaultAnalysisName = "sanxot"
	analysisFolder = ""
	# input files
	inStats = ""
	defaultStatsFile = "stats"
	defaultRelationsFile = "rels"
	defaultTableExtension = ".tsv"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	relationsFile = ""
	upperLevelToGraphFile = ""
	# output files
	defaultUpperLevelToGraphFile = "ulst"
	defaultOutputGraph = "outGraph"
	defaultOutputFile = "outSigmoids"
	defaultExtraTableFile = "outExtra"
	defaultLogFile = "logFile"
	logFile = ""
	graphFile = ""
	outputFile = ""
	extraTableFile = ""
	graphTitle = "Z plot"
	labelFontSize = 12
	minimalGraphTicks = False
	xLabel = "Zij"
	yLabel = "Rank/N"
	
	logList = [["SanXoTGauss " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:p:z:r:c:L:G:o:l:d:W:s:x:t:Z:hgkT", ["analysis=", "folder=", "statsfile=", "relfile=", "list=", "logfile=", "graphfile=", "outputfile=", "graphlimits=", "graphfontsize=", "graphdpi=", "graphlinewidth=", "extratable=", "graphtitle=", "labelfontsize=", "help", "no-graph", "no-legend", "minimalgraphticks", "xlabel=", "ylabel="])
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
		if opt in ("-z", "--statsfile"):
			inStats = arg
		elif opt in ("-r", "--relfile", "--relationsfile"):
			relationsFile = arg
		elif opt in ("-c", "--list"):
			upperLevelToGraphFile = arg
		elif opt in ("-L", "--logfile"):
			logFile = arg
		elif opt in ("-G", "--graphfile"):
			graphFile = arg
		elif opt in ("-g", "--no-graph"):
			showGraph = False
		elif opt in ("-k", "--no-legend"):
			showLegend = False
		elif opt in ("-o", "--outputfile"):
			outputFile = arg
		elif opt in ("-x", "--extratable"):
			extraTableFile = arg
		elif opt in ("-s", "--graphfontsize"):
			graphFontSize = int(arg)
		elif opt in ("-d", "--graphdpi"):
			graphDPI = float(arg)
		elif opt in ("-W", "--graphlinewidth"):
			graphLineWidth = float(arg)
		elif opt in ("-t", "--graphtitle"):
			graphTitle = arg
		elif opt in ("-Z", "--labelfontsize"):
			labelFontSize = float(arg)
		elif opt in ("-l", "--graphlimits"):
			graphLimits = float(arg)
		elif opt in ("-T", "--minimalgraphticks"):
			minimalGraphTicks = True
		elif opt in ("--xlabel"):
			xLabel = arg
		elif opt in ("--ylabel"):
			yLabel = arg
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()

# REGION: FILE NAMES SETUP			

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
	if len(outputFile) == 0:
		outputFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputFile + defaultTableExtension)
	
	if len(extraTableFile) == 0:
		extraTableFile = os.path.join(analysisFolder, analysisName + "_" + defaultExtraTableFile + defaultTableExtension)
		
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultLogFile + defaultTextExtension)
		
	if len(graphFile) == 0:
		graphFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputGraph + defaultGraphExtension)

	if len(os.path.dirname(outputFile)) == 0 and len(os.path.basename(outputFile)) > 0:
		outputFile = os.path.join(analysisFolder, outputFile)

	if len(os.path.dirname(extraTableFile)) == 0 and len(os.path.basename(extraTableFile)) > 0:
		extraTableFile = os.path.join(analysisFolder, extraTableFile)
		
	if len(os.path.dirname(logFile)) == 0 and len(os.path.basename(logFile)) > 0:
		logFile = os.path.join(analysisFolder, logFile)
		
	if len(os.path.dirname(graphFile)) == 0 and len(os.path.basename(graphFile)) > 0:
		graphFile = os.path.join(analysisFolder, graphFile)
		
	logList.append([""])
	logList.append(["Input stats file: " + inStats])
	logList.append(["Relations file: " + relationsFile])
	logList.append(["File with sigmoids to depict: " + upperLevelToGraphFile])
	logList.append(["Output sigmoids table: " + outputFile])
	logList.append(["Output extra table: " + extraTableFile])
	logList.append(["Output log file: " + logFile])
	logList.append(["Output graph file: " + graphFile])
	logList.append([""])

	# pp.pprint(logList)
	# sys.exit()

# END REGION: FILE NAMES SETUP			
	try:
		data, logListExtraInfo = stats.arrangeSubData(inStats = inStats, uFile = upperLevelToGraphFile, relFile = relationsFile, ignoreNaNsInFDR = True)
		logList.append(logListExtraInfo)
		logList.append(["Data files correctly loaded."])
	except getopt.GetoptError:
		logList.append(["Error while getting data files."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	try:
		bigTable, bigTableHeader, extraTable, extraHeader = stats.createBigTable(data)
		logList.append(["Sigmoid table correctly generated."])
	except getopt.GetoptError:
		logList.append(["Error while generating sigmoid table."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	try:
		stats.saveFile(outputFile, bigTable, bigTableHeader)
		logList.append(["Sigmoid table correctly saved."])
	except getopt.GetoptError:
		logList.append(["Error while saving sigmoid table."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	try:
		stats.saveFile(extraTableFile, extraTable, extraHeader)
		logList.append(["Extra table correctly saved."])
	except getopt.GetoptError:
		logList.append(["Error while saving extra table."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	try:
		stats.graphZij(data, graphLimits = graphLimits, graphTitle = graphTitle, graphFile = graphFile, showGraph = showGraph, manySigmoids = True, showLegend = showLegend, dpi = graphDPI, graphFontSize = graphFontSize, lineWidth = graphLineWidth, labelFontSize = labelFontSize, minimalGraphTicks = minimalGraphTicks, xLabel = xLabel, yLabel = yLabel)
		logList.append(["Graph correctly saved."])
	except getopt.GetoptError:
		logList.append(["Error while saving graph."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	stats.saveFile(logFile, logList, "LOG FILE")
	
#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])