from __future__ import division
import pdb
import sys
import getopt
import os
#import gc
import stats
import math
# from lxml import etree
# import xml.dom.minidom as dom
from xml.etree import ElementTree
from time import strftime

import pprint
pp = pprint.PrettyPrinter(indent=4)

conditions = [">=", "<=", "!=", "<>", "==", "!~", "~~", ">", "<"]

#######################################################

def easterEgg():

	print u"""
Estando yo un día en el Alcaná de Toledo, llegó un muchacho a vender unos
cartapacios y papeles viejos a un sedero; y, como yo soy aficionado a leer,
aunque sean los papeles rotos de las calles, llevado desta mi natural
inclinación, tomé un cartapacio de los que el muchacho vendía, y vile con
caracteres que conocí ser arábigos. Y, puesto que, aunque los conocía, no los
sabía leer, anduve mirando si parecía por allí algún morisco aljamiado que los
leyese; [...] le di priesa que leyese el principio, y, haciéndolo ansí,
volviendo de improviso el arábigo en castellano, dijo que decía: Historia de
don Quijote de la Mancha, escrita por Cide Hamete Benengeli, historiador
arábigo.

Don Quixote, Part One, Chapter IX."""

#------------------------------------------------------

def getNodesFromXML(xmlDocument, tableName):

	fieldList = []
	
	table = xmlDocument.getElementsByTagName(tableName)
	
	for nodelist in table:
		childNode = nodelist.childNodes
		for node in childNode:
			if node.nodeType == node.ELEMENT_NODE:
				nName = node.nodeName
				if not nName in fieldList:
					fieldList.append(nName)

	return fieldList

#------------------------------------------------------

def fulfilsCondition(firstPart, condition, secondPart, useNumbers = False):

	if not condition in conditions:
		return False
	
	floatWorks = False
	firstPart_float = 0
	secondPart_float = 0
		
	if useNumbers and "~" not in condition:
		try:
			firstPart_float = float(firstPart)
			secondPart_float = float(secondPart)
			floatWorks = True
		except:
			pass
			
	if floatWorks:
		firstPart = firstPart_float
		secondPart = secondPart_float
		
	if condition == ">=":
		if firstPart >= secondPart:
			return True
		else:
			return False
			
	if condition == "<=":
		if firstPart <= secondPart:
			return True
		else:
			return False
			
	if condition == "~~":
		if secondPart in firstPart:
			return True
		else:
			return False
			
	if condition == ">":
		if firstPart > secondPart:
			return True
		else:
			return False
			
	if condition == "<":
		if firstPart < secondPart:
			return True
		else:
			return False
			
	if condition == "==":
		if firstPart == secondPart:
			return True
		else:
			return False
			
	if condition == "!=" or condition == "<>":
		if firstPart != secondPart:
			return True
		else:
			return False
			
	if condition == "!~":
		if not secondPart in firstPart:
			return True
		else:
			return False
	
	return False
	
#------------------------------------------------------

def findEndParenth(filter, startParenth = 0, curlyBrackets = False):

	openBracket = "("
	closeBracket = ")"
	
	if curlyBrackets:
		openBracket = "{"
		closeBracket = "}"
	
	position = startParenth + 1
	openedParenth = 1
	while position < len(filter):

		if filter[position] == openBracket:
			openedParenth += 1
		
		if filter[position] == closeBracket:
			if openedParenth == 1:
				return position
			
			if openedParenth > 1:
				openedParenth -= 1
		
		position += 1
	
	return -1
	
#------------------------------------------------------

def checkFilter(filter, isXML = True, columns = None, currentRow = [], headers = [], useNumbers = False, logicOperatorsAsWords = False, curlyBrackets = False):
	
	andSymbol = "&&"
	orSymbol = "||"
	openBracket = "("
	closeBracket = ")"
	
	if logicOperatorsAsWords:
		andSymbol = "*and*"
		orSymbol = "*or*"
		
	if curlyBrackets:
		openBracket = "{"
		closeBracket = "}"
	
	filterOk = True
	
	while openBracket in filter and closeBracket in filter:
		startParenth = filter.index(openBracket)
		
		endParenth = findEndParenth(filter, startParenth, curlyBrackets = curlyBrackets)
		if endParenth < startParenth:
			print "\nError, please check that all brackets are properly formed.\n"
			sys.exit(2)
		
		subFilter = filter[startParenth + 1:endParenth].strip()
		preFilter = filter[:startParenth].strip()
		postFilter = filter[endParenth + 1:].strip()
		
		subFilterResult = checkFilter(subFilter,
								isXML = isXML,
								columns = columns,
								currentRow = currentRow,
								headers = headers,
								useNumbers = useNumbers,
								logicOperatorsAsWords = logicOperatorsAsWords,
								curlyBrackets = curlyBrackets)
		
		filter = "%s%s%s" % (preFilter, str(subFilterResult), postFilter)
	
	while andSymbol in filter:
		
		firstPart = filter[:filter.index(andSymbol)].strip()
		lastPart = filter[filter.index(andSymbol) + len(andSymbol):].strip()
		
		firstOk = checkFilter(firstPart,
								isXML = isXML,
								columns = columns,
								currentRow = currentRow,
								headers = headers,
								useNumbers = useNumbers,
								logicOperatorsAsWords = logicOperatorsAsWords,
								curlyBrackets = curlyBrackets)
		
		lastOk = checkFilter(lastPart,
								isXML = isXML,
								columns = columns,
								currentRow = currentRow,
								headers = headers,
								useNumbers = useNumbers,
								logicOperatorsAsWords = logicOperatorsAsWords,
								curlyBrackets = curlyBrackets)
								
		filterOk = lastOk and firstOk
		filter = str(filterOk)
	
	while orSymbol in filter:
	
		firstPart = filter[:filter.index(orSymbol)].strip()
		lastPart = filter[filter.index(orSymbol) + len(orSymbol):].strip()
		
		firstOk = checkFilter(firstPart,
								isXML = isXML,
								columns = columns,
								currentRow = currentRow,
								headers = headers,
								useNumbers = useNumbers,
								logicOperatorsAsWords = logicOperatorsAsWords,
								curlyBrackets = curlyBrackets)
		
		lastOk = checkFilter(lastPart,
								isXML = isXML,
								columns = columns,
								currentRow = currentRow,
								headers = headers,
								useNumbers = useNumbers,
								logicOperatorsAsWords = logicOperatorsAsWords)
								
		filterOk = lastOk or firstOk
		filter = str(filterOk)
	
	while filter.startswith("!"):
		restOfFilter = filter[1:].strip()
		filterOk = not checkFilter(restOfFilter,
								isXML = isXML,
								columns = columns,
								currentRow = currentRow,
								headers = headers,
								useNumbers = useNumbers,
								logicOperatorsAsWords = logicOperatorsAsWords,
								curlyBrackets = curlyBrackets)
		filter = str(filterOk)
	
	if isXML:
		filterOk = checkFilterPartXML(columns, filter, useNumbers = useNumbers)
	else: # then it should be text (tsv)
		filterOk = checkFilterPartTXT(currentRow, headers, filter, useNumbers = useNumbers)
		
		# filterList = filter.split("&&")
		# for filterPart in filterList:
			# filterPart = filterPart.strip()
			
			# if isXML:
				# filterOk = checkFilterPartXML(columns, filterPart) and filterOk
			# else: # then it should be text (tsv)
				# filterOk = checkFilterPartTXT(currentRow, headers, filterPart) and filterOk
			# if not filterOk: break	
	
	return filterOk

#------------------------------------------------------

def checkFilterPartDOM(columns, filter):

	# deprecated version to work with minidom library
	
	filterOk = True
	
	filterVariable = ""
	filterCondition = ""
	filterValue = ""
	
	if len(filter) > 0:
		for condition in conditions:
			if condition in filter:
				filterVariable = filter.split(condition)[0].strip()
				filterCondition = condition
				filterValue = filter.split(condition)[1].strip()
				break
	
	if len(filterVariable) > 0 and len(filterCondition) > 0 and len(filterValue) > 0:
		filterOk = False
		for i in xrange(len(columns)):
			if columns[i].nodeType == columns[i].ELEMENT_NODE:
				nodeNameBrackets = "[" + columns[i].nodeName + "]"
				if nodeNameBrackets == filterVariable:
					cellContents = columns[i].childNodes[0].data
					filterOk = fulfilsCondition(cellContents, filterCondition, filterValue)
					break
	
	return filterOk
	
#------------------------------------------------------

def checkFilterPartTXT(currentRow, headers, filter, useNumbers = False):
	
	# version to work with text files (and not XMLs)
	
	filter = filter.strip()
	if filter == "False": return False
	if filter == "True": return True
		
	filterOk = True
	
	filterVariable = ""
	filterCondition = ""
	filterValue = ""
	
	if len(filter) > 0:
		for condition in conditions:
			if condition in filter:
				filterVariable = filter.split(condition)[0].strip()
				filterCondition = condition
				filterValue = filter.split(condition)[1].strip()
				break
	
	if len(filterVariable) > 0 and len(filterCondition) > 0 and len(filterValue) > 0:
		filterOk = False
		for i in xrange(len(headers)):
			nodeNameBrackets = "[" + headers[i] + "]"
			if nodeNameBrackets == filterVariable:
				cellContents = currentRow[i]
				filterOk = fulfilsCondition(cellContents, filterCondition, filterValue, useNumbers)
				break
	
	return filterOk

#------------------------------------------------------

def checkFilterPartXML(columns, filter, useNumbers = False):
	
	#version to work with ElementTree
	
	filterOk = True
	
	filterVariable = ""
	filterCondition = ""
	filterValue = ""
	
	if len(filter) > 0:
		for condition in conditions:
			if condition in filter:
				filterVariable = filter.split(condition)[0].strip()
				filterCondition = condition
				filterValue = filter.split(condition)[1].strip()
				break
	
	if len(filterVariable) > 0 and len(filterCondition) > 0 and len(filterValue) > 0:
		filterOk = False
		for i in xrange(len(columns)):
			nodeNameBrackets = "[" + columns[i].tag + "]"
			if nodeNameBrackets == filterVariable:
				cellContents = columns[i].text
				filterOk = fulfilsCondition(cellContents, filterCondition, filterValue, useNumbers)
				break
	
	return filterOk
	
#------------------------------------------------------

def printHelp(version = None):

	print """
Aljamia %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to
convert data in xml tables into a tab-separated values archive.

Aljamia needs an XML input file, and:

     * up to four strings to combine information from the xml field.
        Commands: -i, -j, -k and -l. Usage: -i[FirstScan] -j[Sequence]
        It is possible to combine fields: -i[RAWFileName]-[FirstScan]_[Charge]
        (which would deliver something like "sampleA.raw-1029-3").
        Everything outside brackets will be copied unchanged. Note that the
        fields are case sensitive.
     * the name of the table where these fields are (command -t). Default is
        "peptide_match".

And delivers:

     * an output data file with three columns (id, x, v) suitable to work as
        input for SanXoT.

Usage: aljamia.py -x[xml file] -i[fold field] [-j[weight field] -k[id string], ...] [OPTIONS]

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the data
                       file.
   -A, --allow-operations
                       Allow python-style operations for the indicated fields.
                       Example: having Scan = 900, Charge = 3, and using
                           -i"[Scan]-[Charge]" -j"[Scan]-[Charge]" -A"i"
                       Will return "887" and "900-3" i- and j-fields,
                       respectively. By default, no operations are allowed.
   -c, --curly-brackets
                       To use curly brackets, {}, instead of the default
                       parentheses, (), when using the filters (see options -f
                       and -F).
   -d, --allow-duplicates
                       To avoid removal of duplicated relations.
   -f, --filter=string To filter data to import. Use as in these examples:
                       
                           -f"[Charge]==2"
                           -f"[st_excluded]!=excluded", which means
                               st_excluded must NOT be equal to "excluded"
                           -f"[Charge]=2&&[st_excluded]!=excluded", which
                               means charge must be 2, and st_excluded must
                               not be equal to "excluded"
                           -f"[FirstScan]>=1000"
                           -f"[FASTAProteinDescription]~~clathrin", which means
                                FASTAProteinDescription must include "clathrin"
                           -f"[Sequence]!~C", which means
                                Sequence must NOT include "C"
                           -f"[Sequence]!=ABABABABK", which means
                                Sequence must be different than "ABABABABK"
                           -f"!([Sequence]~~C || [Sequence]~~M)", which means
                                Sequence must not (via "!") contain "C" or
                                (via "||") "M". Note you can use parentheses
                           -f"[Sequence]~~C && [Sequence]~~M", wchich means
                                Sequence must contain "C" and (via "&&") "M"
                       
                       Note that the filter is case sensitive.
                       Warning: when using parentheses () generate conflicts
                       in the commandline, the option -c can be used to switch
                       to curly-brackets {} mode.
                       Warning: when using && or || as logical operators
                       generate conflicts in the commandline, the option -w can
                       be used to switch to word operators such as *and* or
                       *or*.
                       Warning: using this argument, the filter is seen as
                       text-only, which means that [Mass] > 3 will not include
                       Mass = 10, as in ASCII order "3" comes after "1". For
                       numerical operations use -F.
                       
   -F, --filter-using-numbers
                       Same as -f, but considering a number everything that
                       looks like a number. Note that this doesn't currently
                       make operations with those numbers, it can only be used
                       for conditionals, such as [Mass] > 565.2
                       
                       Note that whenever an error occurs (for example when
                       text cannot be converted to a number, or when the
                       text-only conditions ~~ or !~ are used), the concerning
                       operation will be treated as text in all cases.
                       
   -i, --c1=string    Identifier for the first column. XML tags must be in
                       square brackets, while the rest of the text will be kept
                       unaltered. Here are some examples using tags such as
                       "FirstScan", "Charge", "Mass" or "Sequence" or "PTM":
                       
                          "ABCD" -> "ABCD" (no tags -> unchanged, to all rows)
                          "FS[FirstScan]_q=[Charge]" -> "FS2991_q=2"
                          "ABCD-[Charge]" -> "ABCD-3"
                          "ABCD_[Charge]_[Mass]" -> "ABCD_3_578.1684"
                          "[Sequence]_[PTM]" -> "SAPEREAVDEK_15.994915"
                       
                       Note that tags are case-sensitive.
                       
   -j, --c2=string    Identifier for the second column (see -i).
   -k, --c3=string    Identifier for the third column (see -i).
   -l, --c4=string    Identifier for the fourth column (see -i).
   --c5=string        Identifier for the fifth column (see -i).
   -L, --logfile=filename
                       To use a non-default name for the log file.
   -o, --output=filename
                       To use a non-default name for the output file.
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the input folder.
   -R, --initialrow=integer
                       To set the position of row with headers (default is 1).
   -t, --table=number  To select fields from a table different than QuiXML's
                       peptide_match (which corresponds to the default, 3).
   -w, --word-operators
                       To use *and* and *or* (including asterisks) as logical
                       operators instead of the default && and || in filters
                       (see options -f and -F).
   -x, --input=filename, --filename=filename
                       Input xml or txt (tsv) file.
""" % version

	return

#------------------------------------------------------

def getDataFromTXT(fileName,
					iField,
					jField,
					kField,
					lField,
					c5Field,
					initialRow = 1,
					filterString = "",
					removeDuplicates = True,
					removeCommas = True,
					allowOperationsInFields = "",
					useNumbers = False,
					logicOperatorsAsWords = False,
					curlyBrackets = False):
	
	result = []
	thisHeader = ""
	
	reader = open(fileName, "r")

	currentRowNumber = 1 # one based!
	for myRow in reader:
	
		if currentRowNumber >= initialRow:
			thisRow = myRow.strip().split("\t")
			if removeCommas:
				for i in xrange(len(thisRow)):
					if thisRow[i].endswith('"') and thisRow[i].startswith('"'):
						thisRow[i] = thisRow[i][1:-1]
			
			if currentRowNumber == initialRow:
				# remove brackets if present
				for i in xrange(len(thisRow)):
					if thisRow[i].startswith('[') and thisRow[i].endswith(']'):
						thisRow[i] = thisRow[i][1:-1]
					thisHeader = thisRow
			else:
				# check for fields
				filterOk = checkFilter(filterString, isXML = False, currentRow = thisRow, headers = thisHeader, useNumbers = useNumbers, logicOperatorsAsWords = logicOperatorsAsWords, curlyBrackets = curlyBrackets)
			
				if filterOk:
					
					dataRow = []
					
					if len(iField) > 0:
						allowOperations = ("i" in allowOperationsInFields)
						iValue = replaceValuesTXT(thisRow, thisHeader, iField, allowOperations)
						dataRow.append(iValue)
					
					if len(jField) > 0:
						allowOperations = ("j" in allowOperationsInFields)
						jValue = replaceValuesTXT(thisRow, thisHeader, jField, allowOperations)
						dataRow.append(jValue)
					
					if len(kField) > 0:
						allowOperations = ("k" in allowOperationsInFields)
						kValue = replaceValuesTXT(thisRow, thisHeader, kField, allowOperations)
						dataRow.append(kValue)
						
					if len(lField) > 0:
						allowOperations = ("l" in allowOperationsInFields)
						lValue = replaceValuesTXT(thisRow, thisHeader, lField, allowOperations)
						dataRow.append(lValue)
						
					if len(c5Field) > 0:
						allowOperations = ("c5" in allowOperationsInFields)
						c5Value = replaceValuesTXT(thisRow, thisHeader, c5Field, allowOperations)
						dataRow.append(c5Value)
						
					result.append(dataRow)
		
		currentRowNumber += 1
		
	if removeDuplicates:
		result = stats.removeDuplicates(result)
		
	return result

#------------------------------------------------------

def getDataFromXML(xmlDocument,
					iField,
					jField,
					kField,
					lField,
					c5Field,
					tableId = 0,
					filterString = "",
					removeDuplicates = True,
					useNumbers = False,
					logicOperatorsAsWords = False,
					curlyBrackets = False):

	result = []

	#pepMatchTable = xmlDocument.getElementsByTagName(tableId) # for deprecated minidom
	pepMatchTable = xmlDocument.getiterator(tableId)

	for pepMatch in pepMatchTable:
		
		#pepMatchColumns = pepMatch.childNodes # for deprecated minidom
		pepMatchColumns = pepMatch.getchildren()
		filterOk = checkFilter(filterString, columns = pepMatchColumns, useNumbers = useNumbers, logicOperatorsAsWords = logicOperatorsAsWords, curlyBrackets = curlyBrackets)
		
		if filterOk:
			
			dataRow = []
			
			if len(iField) > 0:
				iValue = replaceValuesXML(pepMatchColumns, iField)
				dataRow.append(iValue)
			
			if len(jField) > 0:
				jValue = replaceValuesXML(pepMatchColumns, jField)
				dataRow.append(jValue)
			
			if len(kField) > 0:
				kValue = replaceValuesXML(pepMatchColumns, kField)
				dataRow.append(kValue)
				
			if len(lField) > 0:
				lValue = replaceValuesXML(pepMatchColumns, lField)
				dataRow.append(lValue)

			if len(c5Field) > 0:
				c5Value = replaceValuesXML(pepMatchColumns, c5Field)
				dataRow.append(c5Value)

			result.append(dataRow)
			
		#gc.collect()
		# Important:
		# it is better not to use the garbage collector:
		# it takes 0.36 seconds each time (for each peptide_match!)
		# and it does not improve memory handling

	if removeDuplicates:
		result = stats.removeDuplicates(result)
		
	return result

#------------------------------------------------------

def replaceValuesDOM(columns, field):

	# deprecated: it was intended to work with minidom
	
	value = field
	for i in xrange(len(columns)):

		if columns[i].nodeType == columns[i].ELEMENT_NODE:
			
			nodeNameBrackets = "[" + columns[i].nodeName + "]"
			if nodeNameBrackets in value:
				value = value.replace(nodeNameBrackets, columns[i].childNodes[0].data)
				
	return value

#------------------------------------------------------

def replaceValuesTXT(currentRow, headers, field, allowOperations = True):

	# version to work with tab separated values text

	value = field
	for i in xrange(len(headers)):
		nodeNameBrackets = "[" + headers[i] + "]"
		if nodeNameBrackets in value:
			if i >= len(currentRow):
				value = value.replace(nodeNameBrackets, "")
			else:
				value = value.replace(nodeNameBrackets, currentRow[i])
	
	if allowOperations:
		try:
			newValue = eval(value)
			value = str(newValue)
		except:
			pass
				
	return value

#------------------------------------------------------

def replaceValuesXML(columns, field):

	# version to work with ElementTree
	
	value = field
	for i in xrange(len(columns)):
		nodeNameBrackets = "[" + columns[i].tag + "]"
		if nodeNameBrackets in value:
			value = value.replace(nodeNameBrackets, columns[i].text)
				
	return value

#------------------------------------------------------

def findErrors(xmlDocument, tableId, iField, jField, kField, lField, c5Field):

	errors = []
	tagList = getNodesFromXML(xmlDocument, tableId)
	
	if len(c5Field) > 0 and len(lField) == 0:
		errors.append("Error: c4 field cannot be empty if you are using c5. Please use -l command.")
	if len(lField) > 0 and len(kField) == 0:
		errors.append("Error: c3 field cannot be empty if you are using c4. Please use -k command.")
	if len(kField) > 0 and len(jField) == 0:
		errors.append("Error: c2 field cannot be empty if you are using c3. Please use -j command.")
	if len(iField) == 0:
		errors.append("Error: c1 field cannot be empty. Please use -i command.")

	return errors

#------------------------------------------------------

def main(argv):

	version = "v1.16"
	fileName = ""
	outFile = ""
	iField = ""
	jField = ""
	kField = ""
	lField = ""
	c5Field = ""
	analysisName = ""
	filterString = ""
	useNumbers = False
	logicOperatorsAsWords = False # False = Python-style operators (&&, ||), True = word-like operators (\and\ \or\)
	curlyBrackets = False # False = normal brackets (), True = curly brackets {}
	analysisFolder = ""
	defaultFileName = "QuiXML"
	defaultOutputFile = "table"
	defaultOutputLog = "log"
	defaultTableExtension = ".tsv"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	defaultXMLExtension = ".xml"
	defaultAnalysisName = "aljamia"
	removeDuplicates = True
	allowOperationsInFields = ""
	tableId = "peptide_match" # default for QuiXML
	initialRow = 1 # for xls coming from QuiXML should be 25
	logFile = ""
	logList = [["Aljamia " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]
	
	try:
		opts, args = getopt.getopt(argv, "a:p:x:o:i:j:k:l:t:R:L:f:F:A:cdwh", ["input=", "filename=", "place=", "folder=", "outfile=", "c1=", "c2=", "c3=", "c4=", "c5=", "table=", "initialrow=", "logfile=", "filter=", "allow-operations=", "curly-brackets", "allow-duplicates", "word-operators", "help", "egg", "easteregg"])
	except getopt.GetoptError:
		logList.append(["Error while getting parameters."])
		stats.saveFile(logFile, logList, "LOG FILE")
		sys.exit(2)
	
	if len(opts) == 0:
		printHelp(version)
		sys.exit()
		
	for opt, arg in opts:
		if opt in ("-a", "--analysis"):
			analysisName = arg
		if opt in ("-p", "--place", "--folder"):
			analysisFolder = arg
		if opt in ("-x", "--input", "--filename"):
			fileName = arg
		if opt in ("-o", "--output"):
			outFile = arg
		elif opt in ("-i", "--c1"):
			iField = arg.strip()
		elif opt in ("-j", "--c2"):
			jField = arg.strip()
		elif opt in ("-k", "--c3"):
			kField = arg.strip()
		elif opt in ("-l", "--c4"):
			lField = arg.strip()
		elif opt in ("--c5"):
			c5Field = arg.strip()
		elif opt in ("-t", "--table"):
			tableId = int(arg) # *** check this: int or string?
		elif opt in ("-R", "--initialrow"):
			initialRow = int(arg)
		elif opt in ("-L", "--logfile"):
			logFile = arg
		elif opt in ("-f", "--filter"):
			filterString = arg
			useNumbers = False
		elif opt in ("-F", "--filter-using-numbers"):
			filterString = arg
			useNumbers = True
		elif opt in ("-A", "--allow-operations"):
			allowOperationsInFields = str(arg).strip()
		elif opt in ("-d", "--allow-duplicates"):
			removeDuplicates = False
		elif opt in ("-c", "--curly-brackets"):
			curlyBrackets = True
		elif opt in ("-w", "--word-operators"):
			logicOperatorsAsWords = True
		elif opt in ("-h", "--help"):
			printHelp(version)
			sys.exit()
		elif opt in ("--egg", "--easteregg"):
			easterEgg()
			sys.exit()

			
# REGION: FILE NAMES SETUP
	
	if len(analysisName) == 0:
		if len(fileName) > 0:
			analysisName = os.path.splitext(os.path.basename(fileName))[0]
		else:
			analysisName = defaultAnalysisName
	
	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart
			
	if len(fileName) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(fileName)) > 0:
			analysisFolder = os.path.dirname(fileName)
	# input
	if len(fileName) == 0:
		fileName = os.path.join(analysisFolder, analysisName + "_" + defaultFileName + defaultXMLExtension)
		
	if len(os.path.dirname(fileName)) == 0:
		fileName = os.path.join(analysisFolder, fileName)
	
	# output
	if len(outFile) == 0:
		outFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputFile + defaultTableExtension)
	else:
		if len(os.path.dirname(outFile)) == 0:
			outFile = os.path.join(analysisFolder, outFile)
	
	if len(logFile) == 0:
		logFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputLog + defaultTextExtension)
	
	logList.append(["Input file: " + fileName])
	logList.append(["Output file: " + outFile])
	logList.append(["Log file: " + logFile])
	
# END REGION: FILE NAMES SETUP

	# errorsFound = findErrors(xmlDocument, tableId, iField, jField, kField, lField)
	
	# if len(errorsFound) > 0:
		# for error in errorsFound:
			# print error
		# sys.exit()
	# else:
		# pass

	if os.path.splitext(fileName)[1] == ".xml":

		try:
			#xmlDocument = dom.parse(fileName)
			xmlDocument = ElementTree.parse(fileName).getroot()
		except:
			print "Error while reading xml file."
			logList.append(["Error while reading xml file."])
			stats.saveFile(logFile, logList, "LOG FILE")
			sys.exit(2)
		
		resultingData = getDataFromXML(xmlDocument,
										Field,
										jField,
										kField,
										lField,
										c5Field,
										tableId = tableId,
										filterString = filterString,
										removeDuplicates = removeDuplicates,
										useNumbers = useNumbers,
										logicOperatorsAsWords = logicOperatorsAsWords,
										curlyBrackets = curlyBrackets)
		
	else: # then it should be a tsv
		resultingData = getDataFromTXT(fileName,
										iField,
										jField,
										kField,
										lField,
										c5Field,
										filterString = filterString,
										removeDuplicates = removeDuplicates,
										initialRow = initialRow,
										allowOperationsInFields = allowOperationsInFields,
										useNumbers = useNumbers,
										logicOperatorsAsWords = logicOperatorsAsWords,
										curlyBrackets = curlyBrackets)
	
	iTab = ""
	if len(iField) > 0: iTab = "%s\t" % iField
	jTab = ""
	if len(jField) > 0: jTab = "%s\t" % jField
	kTab = ""
	if len(kField) > 0: kTab = "%s\t" % kField
	lTab = ""
	if len(lField) > 0: lTab = "%s\t" % lField
	c5Tab = ""
	if len(c5Field) > 0: c5Tab = "%s\t" % c5Field
	
	header = iTab + jTab + kTab + lTab + c5Tab
	header = header[:len(header) - 1]
	
	stats.saveFile(outFile, resultingData, header)
	
	if len(logFile) > 0:
		stats.saveFile(logFile, logList, "LOG FILE")

#######################################################

if __name__ == "__main__":
    main(sys.argv[1:])
	
	

# some code lines useful to check slow points
# from datetime import datetime
# timeold = time1
# now = datetime.now()
# time1 = str(float(now.strftime("%M")) * 60 + float(now.strftime("%S.%f")))
# now = datetime.now()
# time2 = str(float(now.strftime("%M")) * 60 + float(now.strftime("%S.%f")))
# now = datetime.now()
# time3 = str(float(now.strftime("%M")) * 60 + float(now.strftime("%S.%f")))
# span21 = float(time1) - float(time2)
# span32 = float(time3) - float(time2)
# spanBig = float(time1) - float(timeold)
# print
# print str(counter) + ", " + iValue + ", " + jValue
# print time1 + ", " + time2 + ", " + time3
# print str(span21) + ", " + str(span32), ", big: " + str(spanBig)