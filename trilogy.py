__author__ = "nbagwan"
import pdb
import os
import ntpath
import time
from optparse import OptionParser

start_time = time.time()

# usage = "usage: %mainMethod -P -B -X  -F -O"
version = """ trilogy 0.03
is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares, used to
convert data into relations tables into a tab-separated values archive.

Written by Navratan Bagwan.
"""

usage = """-a paramterTest -i .\data\testParameter.txt -c Corr_Seq-mass -C fastaDescription -n "[-0.000232]|[1.001701]&D=NonMod" -p .\data -t "[15.994862]=Oxidation|PTMs" -s Scan -f FileName"""

parser = OptionParser(usage=usage,version=version)

parser.add_option("-a", "--analysis", action="store", type="string", dest="analysis", help="Use a prefix for the output files. If this is not "
                                                                                           "provided, then no prefix will be garnered.", default=" ")

parser.add_option("-p", "--place", action="store", type="string", dest="outputFolder", help="Provide the output folder location, Id this not"
                                                                                            "provided rhen ouput files will be careated in the"
                                                                                            "same location as input file.", default = " ")

parser.add_option("-i", "--inputFile", action="store", type="string", dest="inputfile", help="Enter the path for inputfile, any tab-separated file can "
                                                                                             "be used as a input. Example: SHIFTS output or Aljamia output")

parser.add_option("-c", "--peptideHeader", action="store", type="string", dest="peptideColumn", help="Identifier for the peptide coloumn")

parser.add_option("-C", "--proteinHeader", action="store", type="string", dest="proteinColumn", help="Identifier for the protein/FastaDescription column")

parser.add_option("-s", "--ScanHeader", action="store", type="string", dest="scanColumn", help="Identifier for the scan coloumn")

parser.add_option("-f", "--RawfileHeader", action="store", type="string", dest="rawColumn", help="Identifier for the raw filename coloumn")

parser.add_option("-n", "--NonmodMass", action="store", type="string", dest="NMapexMass", help="This parameter allows to TAG non-modified peptides."
                                                                                               "Tagging can be done in a very flexible manner by"
                                                                                               "using different Tagging options in combination."
                                                                                               "Some defualt tagging options are also included"
                                                                                               "Check for exmaple option below 1) [-0.000232]|[1.001701]&!D=NonMod                  "
                                                                                               "multiple things can be considered to a Null-hypothesis"
                                                                                               "in eg.1, [-0.000232] and [1.001701] both are considered"
                                                                                               "as NH, seprated by a |. In addition, additional conditions"
                                                                                               "can be used as [1.001701]&!D, means,[1.001701] should"
                                                                                               "be in peptide but D should not be. anythying after = will used as tag for NH")

parser.add_option("-t", "--PTMtags", action="store", type="string", dest="ptmTAGS", help="This parameter allows to TAG modified peptides."
                                                                                               "Tagging can be done in a very flexible manner by"
                                                                                               "using different Tagging options in combination."
                                                                                               "Some defualt tagging options are also included example 1) [15.994862]=Oxidation,[0.010924]=c13|PTMs ,"
                                                                                         " in this eg multiple things are considered as modification and all of them have differet label, however"
                                                                                         "for the things which are not in input can also be tagged as modification by using |")

(options, args) = parser.parse_args()

if options.analysis:
    analysis = options.analysis
else:
    parser.error("Use a prefix for the output files else the name will taken from input files")

if options.inputfile:
    inputfile = options.inputfile
else:
    parser.error("input file for mkaing relation file")

if options.peptideColumn:
    peptideColumn = options.peptideColumn
else:
    parser.error("header for peptide coloumn")

if options.proteinColumn:
    proteinColumn = options.proteinColumn
else:
    parser.error("header for protein coloumn")

if options.NMapexMass:
    NMapexMass = options.NMapexMass
else:
    parser.error("NM mass as cometPTM")

if options.outputFolder:
    outputFolder = options.outputFolder
else:
    parser.error("NM mass as cometPTM")

if options.ptmTAGS:
    #print options.ptmTAGS
    ptmTAGS = options.ptmTAGS
else:
    parser.error("provide PTM tags")

if options.scanColumn:
    scanColumn = options.scanColumn
else:
    parser.error("provide the scan coloumn")

if options.rawColumn:
    rawColumn = options.rawColumn
else:
    parser.error("provide the rawfile column")


def createDic(filename, keycol, valcol, scan, rawfilename):
    count = 0
    dic = {}
    with open(filename, "r") as f:
        next(f)
        for lines in f:
            splits = lines.split("\t")
            if splits[keycol].strip() in dic:
                dic[splits[keycol].strip()].append([splits[valcol].strip(), splits[scan].strip(), splits[rawfilename].strip()])
                count += 1
            else:
                dic[splits[keycol].strip()] = [[splits[valcol].strip(), splits[scan].strip(), splits[rawfilename].strip()]]
                count += 1
    return dic


def checksubstring(list, substring):
    counts = 0
    for elements in list:
        if substring in elements:
            counts = counts + 1

    return counts


def checkPresenceOfSeq(stringList, sequence2check):
    stringOrList = stringList.split("|")
    for each in stringOrList:
        AndList = each.split("&")
        AndCount = 0
        for eachSeq in AndList:
            if eachSeq[0] == "!":
                if eachSeq[1:] not in sequence2check:
                    AndCount += 1
            else:
                if eachSeq in sequence2check:
                    AndCount += 1
        if AndCount == len(AndList):
            return 1
    return 0


def nullhypothesisFilter(NULL_IDs, seqList):
    count = 0

    NH_split = NULL_IDs.split("=")

    if len(NH_split) != 1:
        NH_tagename = NH_split[1]
    else:
        NH_tagename = "Null-Hypothesis"

    for seq in seqList:
        count += checkPresenceOfSeq(stringList=NH_split[0], sequence2check=seq[0].strip())
    return count


def eachSequenceCheck(NULL_IDs, sequence):
    NH_split = NULL_IDs.split("=")
    if len(NH_split) != 1:
        NH_tagename = NH_split[1]
    else:
        NH_tagename = "Null-Hypothesis"

    stringOrList = NH_split[0].split("|")

    for each in stringOrList:
        AndList = each.split("&")
        AndCount = 0
        for eachSeq in AndList:
            if eachSeq[0] == "!":
                if eachSeq[1:] not in sequence:
                    AndCount += 1
            else:
                if eachSeq in sequence:
                    AndCount += 1
        if AndCount == len(AndList):
            return 1, NH_tagename
    return 0


def eachSequenceForPTMtags(PTMids, sequence):
    # pdb.set_trace()
    # # print PTMids

    countinue = True
    if "|" not in PTMids.strip():
        NH_tagename = PTMids.strip()
        countinue =False
    if not countinue:
        return NH_tagename

    if countinue:
        if len(PTMids.strip()) ==0:
            NH_tagename = "Modified peptide"
        else:
            NH_split = PTMids.split("|")
            if len(NH_split) != 1:
                NH_tagename = NH_split[1]
            else:
                NH_tagename = "Modified peptide"

        if NH_tagename != "Modified peptide":
            stringOrList = NH_split[0].split(",")
            output_name = ""
            for each in stringOrList:
                if each.split("=")[0].strip() in sequence:
                    output_name += str(each.split("=")[1].strip())
                    output_name += str(" ")

            if len(output_name) < 2:
                return NH_tagename
            else:
                return output_name

        else:
            return NH_tagename




def relation_seprator(analysis, RelationFile, pepCol, protCol, nonModifiedIds, outputpath, PTMids, scanCol, rawFileCol):

    sepration = "/"
    if len(outputpath.strip()) == 0:
        outputpath = os.path.dirname(RelationFile)
        if len(analysis.strip()) == 0:
            peptide2proteinOUT = str(outputpath) + sepration  + "peptide2protein-rels.txt"
            protein2all = str(outputpath) + sepration +  "protein2All-rels.txt"
            scan2peptide = str(outputpath) + sepration + "scan2peptide-rels.txt"
        else:
            peptide2proteinOUT = outputpath + sepration + str(analysis) + "_peptide2protein-rels.txt"
            protein2all = outputpath + sepration + str(analysis) + "_protein2All-rels.txt"
            scan2peptide = outputpath + sepration + str(analysis) + "_scan2peptide-rels.txt"
    else:
        if len(analysis.strip()) == 0:
            peptide2proteinOUT = outputpath.strip() + sepration + "peptide2protein-rels.txt"
            protein2all = outputpath.strip() + sepration + "protein2All-rels.txt"
            scan2peptide = outputpath.strip() + sepration + "scan2peptide-rels.txt"
        else:
            peptide2proteinOUT = outputpath.strip() + sepration + str(analysis) + "_peptide2-protein-rels.txt"
            protein2all = outputpath.strip() + sepration + str(analysis) + "_protein2All-rels.txt"
            scan2peptide = outputpath.strip() + sepration + str(analysis) + "_scan2peptide-rels.txt"

    w = open(peptide2proteinOUT, "w")
    w1 = open(protein2all, "w")
    w2 = open(scan2peptide, "w")

    with open(RelationFile, "r") as rf:
        pep2pro = []
        pro2all = ["idsup" + "\t" + "idinf" + "\t" + "tag" + "\n"]
        scan2pep = ["idsup" + "\t" + "idinf" + "\t" + "tag" + "\n"]

        header = rf.readline().strip()
        peptideInd = header.split("\t").index(pepCol)
        proteinInd = header.split("\t").index(protCol)
        scanInd = header.split("\t").index(scanCol)
        rawInd = header.split("\t").index(rawFileCol)

        next(rf)
        protPep_relationDic = createDic(filename=RelationFile, keycol=proteinInd, valcol=peptideInd, scan=scanInd, rawfilename=rawInd)
        for EachProtein in protPep_relationDic:

            NM_count = 0
            PTM_count = 0
            # print EachProtein
            # print protPep_relationDic[EachProtein]
            # pdb.set_trace()
            checkCount = nullhypothesisFilter(NULL_IDs=nonModifiedIds, seqList=protPep_relationDic[EachProtein])
            # checkCount = checksubstring(protPep_relationDic[EachProtein], nonModifiedIds)
            if checkCount > 1:
                for EachSeq in protPep_relationDic[EachProtein]:

                    nonMOD_retrunType = eachSequenceCheck(NULL_IDs=nonModifiedIds, sequence=EachSeq[0].strip())

                    if nonMOD_retrunType == 0:
                        ptmTag_output = eachSequenceForPTMtags(PTMids=PTMids, sequence=EachSeq[0].strip())


                        pep2pro.append(EachProtein + "\t" + EachSeq[0].strip() + "\t" + ptmTag_output + "\n")
                        pro2all.append("1" + "\t" + EachProtein + "\t" + ptmTag_output + "\n")
                        scan2pep.append(EachSeq[0].strip() + "\t" + EachSeq[2].strip() + "_"+ EachSeq[1].strip() + "\t"+ ptmTag_output + "\n")
                    else:
                        tempList = list(nonMOD_retrunType)
                        pep2pro.append(EachProtein + "\t" + EachSeq[0].strip() + "\t" + tempList[1].strip() + "\n")
                        pro2all.append("1" + "\t" + EachProtein + "\t" + tempList[1].strip() + "\n")
                        scan2pep.append(EachSeq[0].strip() + "\t" + EachSeq[2].strip() + "_"+ EachSeq[1].strip() + "\t"+ tempList[1].strip() + "\n")

            else:
                # print protPep_relationDic[EachProtein]
                for EachSeq in protPep_relationDic[EachProtein]:
                    nonMOD_retrunType = eachSequenceCheck(NULL_IDs=nonModifiedIds, sequence=EachSeq[0].strip())
                    if nonMOD_retrunType == 0:
                        ptmTag_output = eachSequenceForPTMtags(PTMids=PTMids, sequence=EachSeq[0].strip())
                        pep2pro.append(EachProtein + "_" + EachSeq[0].strip() + "\t" + EachSeq[0].strip() + "\t" + ptmTag_output + "\n")
                        pro2all.append("1" + "\t" + EachProtein + "_" + EachSeq[0].strip() + "\t" + ptmTag_output + "\n")
                        scan2pep.append(EachSeq[0].strip() + "\t" + EachSeq[2].strip() + "_"+ EachSeq[1].strip() + "\t"+ ptmTag_output + "\n")
                        # if nonModifiedIds in EachSeq:
                        # pep2pro.append(EachProtein + "_" + EachSeq + "\t" + EachSeq + "\t" + "NM" + "\n")
                        # pro2all.append("1" + "\t" + EachProtein + "_" + EachSeq + "\t" + "NM" + "\n")
                    else:
                        tempList = list(nonMOD_retrunType)
                        pep2pro.append(EachProtein + "_" + EachSeq[0].strip() + "\t" + EachSeq[0].strip() + "\t" + tempList[1].strip() + "\n")
                        pro2all.append("1" + "\t" + EachProtein + "_" + EachSeq[0].strip() + "\t" + tempList[1].strip() + "\n")
                        scan2pep.append(EachSeq[0].strip() + "\t" + EachSeq[2].strip() + "_" + EachSeq[1].strip() + "\t" + tempList[1].strip() + "\n")

                        # pep2pro.append(EachProtein + "_" + EachSeq + "\t" + EachSeq + "\t" + "PTM" + "\n")
                        # pro2all.append("1" + "\t" + EachProtein + "_" + EachSeq + "\t" + "PTM" + "\n")

    pep2pro_WOduplicate = list(set(pep2pro))
    w.writelines("idsup" + "\t" + "idinf" + "\t" + "tag" + "\n")
    for p2p in pep2pro_WOduplicate:
        w.writelines(p2p)
    w.close()

    for p2a in pro2all:
        w1.writelines(p2a)
    w1.close()

    for s2p in scan2pep:
        w2.writelines(s2p)
    w2.close()


# relation_seprator(analysis="nav",RelationFile=r"E:\Users\nbagwan\Desktop\trilogy\data\IsotopCorrection_TargetData_withSequence-massTag.txt",pepCol="Corr_Seq-mass", protCol="fastaDescription"
#                   , nonModifiedIds="[-0.000232]", outputpath= "")

if __name__ == "__main__":
    relation_seprator(analysis=analysis, RelationFile=inputfile, pepCol=peptideColumn, protCol=proteinColumn,
                      nonModifiedIds=NMapexMass, outputpath=outputFolder, PTMids=ptmTAGS, scanCol=scanColumn,
                      rawFileCol=rawColumn)

print("---%s seconds ---" % (time.time() - start_time))
