import pdb
import math
import sys
import getopt
import stats
import os
from time import strftime

import pprint

pp = pprint.PrettyPrinter(indent=4)

def ZpCalculator(relationsFile,
                 modifiedPeptidesFile,modifiedPeptidesFile1,
                 nonModifiedPep2ProtFile,
                 pep2protein,outname,
                 varFile, varFile1):
	folderout=outname.split("\\")
	OutfolderLocation= "\\".join(folderout[:-1])
	norm_wo_V = []
	norm_wo_W = []
	main_file = []
	main_file1= []
	main_file_FINAL=[]
	Norm_V=[["idinf","\t","X'inf","\t","Vinf","\n"]]
	Norm_W=[["idinf","\t","X'inf","\t","Winf","\n"]]
	W=open(OutfolderLocation+"\peptide2protein_Norm_W.txt", "w")
	V=open(OutfolderLocation+"\peptide2protein_Norm_V.txt", "w")

	dic_seq = stats.load2dictionary(modifiedPeptidesFile, keyNum=0, n1=1, n2=2) ################# wo file ###########
	dic_dis = stats.load2dictionary(nonModifiedPep2ProtFile, keyNum=3, n1=1, n2=4,n3=5,n4=6) ######### protein to all file ########
	dic_seq1 = stats.load2dictionary(modifiedPeptidesFile1, keyNum=0, n1=1, n2=2)################ W file #########
	W_seq = stats.load2dictionary(pep2protein, keyNum=0, n1=6) ###nonmod peptide to protein####
	#print W_seq
	#pdb.set_trace()
	variance, varianceOk = stats.extractVarianceFromVarFile(varFile)
	variance1, variance1Ok = stats.extractVarianceFromVarFile(varFile1)
	x = float(dic_dis[dic_dis.keys()[0]][0])
	x_meanCount= int(dic_dis[dic_dis.keys()[3]][3])
	

	rel_seq = {}
	count_n={}
	count_n1={}
	allRelations = stats.loadRelationsFile(relationsFile)
## to count the descriptions in same for different sequence
### all the calculation for ......WO files........ ##########
	for relation in allRelations:
		Rel_sequence = relation[1]
		Rel_discription = relation[0]  # protein
		rel_seq[Rel_sequence] = Rel_discription
		if Rel_sequence in dic_seq:
			if rel_seq[Rel_sequence] not in count_n:
				count_n[rel_seq[Rel_sequence]]=1
			elif rel_seq[Rel_sequence] in count_n:
				count_n[rel_seq[Rel_sequence]]+=1

	for relation_n in allRelations:
		Rel_sequence = relation_n[1]
		Rel_discription = relation_n[0]  # protein
		if Rel_sequence in dic_seq:
			count=count_n[rel_seq[Rel_sequence]]
			xp = float(dic_seq[Rel_sequence][0])
			vp = float(dic_seq[Rel_sequence][1])
			NormV_VP = float(dic_seq[Rel_sequence][1])
			main_file_des = rel_seq[Rel_sequence]
			wp = float(1 /  (1/vp + variance))  ###(1 / ((1 / vp) + variance)) 
			wq = float(1 / (1/wp + variance1))
			xq="0"
			vq="1"
			x_mean = x
			NormV_xp=float(xp-x_mean)
			NormW_VP=wq
			zp = (xp - x_mean) * (math.sqrt(wq))*math.sqrt(x_meanCount/(x_meanCount-1))
			#print zp
			norm_wo_V.append([str(Rel_sequence),"\t", str(NormV_xp),"\t", str(NormV_VP),"\n"])
			norm_wo_W.append([str(Rel_sequence),"\t", str(NormV_xp),"\t", str(NormW_VP),"\n"])
			main_file.append([main_file_des, xq , vq , Rel_sequence, xp , vp ,x_meanCount,zp])
			
################...........W files ..........############################
	for relation_n in allRelations:
		Rel_sequence = relation_n[1]
		Rel_discription = relation_n[0]
		if Rel_sequence in dic_seq1:
			#count1=count_n1[rel_seq[Rel_sequence]]
			xp1 = float(dic_seq1[Rel_sequence][0])
			vp1 = float(dic_seq1[Rel_sequence][1])
			w_NormV_VP = float(dic_seq1[Rel_sequence][1])
			main_file_des1 = rel_seq[Rel_sequence]
			#pdb.set_trace()
			#pdb.set_trace()
			wp1 = float(1 /  (1/vp1 + variance))  ###(1 / ((1 / vp) + variance)) 
			wq1 = float(1 / (1/wp1 + variance1))
			w_NormW_VP=wp1
			if main_file_des1 in dic_dis and main_file_des1 in W_seq:
				#print W_seq[main_file_des1]
				count1=int(W_seq[main_file_des1][0])
				#count1=int(W_seq[">sp|O00602|FCN1_HUMAN Ficolin-1 OS=Homo sapiens GN=FCN1 PE=1 SV=2"][0])
				#print count1
				#pdb.set_trace()
				#n=int(count1)
				xq1 = float(dic_dis[main_file_des1][1])
				vq1= float(dic_dis[main_file_des1][2])
				w_NormV_xp=float(xp1-xq1)
				if count1 > 1:
					zp1 = (xp1 - xq1) * (math.sqrt(wp1))*math.sqrt(count1/(count1-1))
				else:
					zp1="nan"
				main_file1.append([main_file_des1, xq1 , vq1 , Rel_sequence, xp1 , vp1 , count1 , zp1]) #population_A_B()
				main_file_FINAL=main_file+main_file1
				Norm_V.append([str(Rel_sequence),"\t", str(w_NormV_xp),"\t", str(w_NormV_VP),"\n"])
				Norm_W.append([str(Rel_sequence),"\t", str(w_NormV_xp),"\t", str(w_NormW_VP),"\n"])
				#pdb.set_trace()
	#print len(Norm_V)
	#print len(Norm_W)		
    ## merge another stas file:
	nonMod_V=[]
	nonMod_W=[]
	List_V=[]
	List_W=[]
	with open(pep2protein) as file_new:
		next(file_new)
		for line in file_new:
			n_splits=line.split("\t")
			nonNormV_xp = (float(n_splits[4]) - float(n_splits[1]))
			nonNormV_VP = (1 /  (1/float(n_splits[5]) + variance))
			#nonNormW_VP = (1 /  (1/float(n_splits[5]) + variance))
			nonRel_sequence= str(n_splits[3])
			nonMod_V.append([str(nonRel_sequence),"\t", str(nonNormV_xp),"\t", str(nonNormV_VP),"\n"])
			#nonMod_W=[str(nonRel_sequence),"\t", str(nonNormV_xp),"\t", str(nonNormW_VP),"\n"]
			main_file_FINAL.append([n_splits[0],n_splits[1],n_splits[2],n_splits[3],n_splits[4],n_splits[5],n_splits[6],float(n_splits[7])])
	#print len(nonMod_V)
	List_V=Norm_V + norm_wo_V + nonMod_V
	#print len(List_V)
	for lineV in List_V:
		V.writelines(lineV)
	V.close()

	List_W=Norm_W + norm_wo_W + nonMod_V
	for lineW in List_W:
		W.writelines(lineW)
	W.close()
	mainlist=stats.fdr_calculator(main_file_FINAL)
	return mainlist
#------------------------------------------------------

def printHelp(version=None, advanced=False):
	print """
SanXoTGhost %s is a program made in the Jesus Vazquez Cardiovascular
Proteomics Lab at Centro Nacional de Investigaciones Cardiovasculares,
for highthroughput PTM( Post translation modifications )
quantifiaction analysis.


For example:
sanxotGhost.py -m M1_peptideMwoNMA2proteins_relations.txt
 -M M_peptideM_w_NMA2proteins_relations.txt 
-n n_127_C_q2a_varQC_outStats.xls
-t t_peptideNMA2protein_stats.xls -r R_relationFile.txt 
-V V_peptideNMA2protein_temp_infoFile.txt 
-W W_127_C_q2a_varQC_infoFile.txt 
-o final_out.txt

   -h, --help          Display this help and exit.
   -a, --analysis=string
                       Use a prefix for the output files. If this is not
                       provided, then the prefix will be garnered from the data
                       file.
   -m, --modfile=string
                       The SanXoT data file containing the MODIFIED
                       peptides as well as nonnodified with thier nonmodified
		       counterpart, coming form a protein whcih DOES NOT contain
		       other nonmodified peptide. 
   -M, --modfile1=string
                       The SanXoT data file containing the MODIFIED
                       peptides as well as nonnodified with thier nonmodified
		       counterpart, coming form a protein whcih DOES contain
		       other nonmodified peptide. 
   -n, --nonmodfile=string
                       contains all the nonmodified peptides,The SanXoT outstats
 		       file from peptide to protein integration.
   -t  --pep2pro=string
                       The SanXot outstats file from NONMODIFIED peptide to
                       protein integration.
   -o, --outputfile=string
                       The new outstasts file containing ALL peptides.
   -r, --relfile=string
                       The SanXoT relations file for peptides to proteins.
   -V, --varfile=string
                       The SanXoT logFile containing the variance of an
                       integration from NONMODIFIED peptide to PROTEIN.
   -W, --varfile1=string
                       The SanXoT logFile containing the variance of an
                       integration from PROTEIN TO CATEGORIES               
   -p, --place, --folder=foldername
                       To use a different common folder for the output files.
                       If this is not provided, the the folder used will be the
                       same as the input folder.

""" % version
#------------------------------------------------------

def main(argv):
	version = "v0.08"
	analysisName = ""
	analysisFolder = ""
	relationsFile = ""
	modifiedPeptidesFile = ""
	modifiedPeptidesFile1= ""
	nonModifiedPep2ProtFile = ""
	pep2protein=""
	varFile = ""
	varFile1 = ""
	outputFile = ""
	defaultModifiedPeptidesFile = "modPepFile"
	defaultModifiedPeptidesFile1= "modPepFile1"
	defaultnonModifiedPeptidesFile = "nonmodPepFile"
	defaultpep2protein = "Pep2proteinFile"
	defaultOutput = "ModOutStats"
	defaultOutputInfo = "infoFile"
	defaultRelationsFile = "rels"
	defaultTableExtension = ".xls"
	defaultTextExtension = ".txt"
	defaultGraphExtension = ".png"
	defaultAnalysisName = "ghostanalysis"
	infoFile = ""
	logList = [["SanXoTGhost " + version], ["Start: " + strftime("%Y-%m-%d %H:%M:%S")]]

	try:
		opts, args = getopt.getopt(argv, "a:p:r:m:M:n:t:o:V:W:L:h",
                                   ["analysis=", "folder=", "relfile=", "modfile=", "modfile1=", "nonmodfile=", "pep2pro=","outputfile=",
                                    "varfile=","varFile1=","infofile=", "help"])
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
		if opt in ("-m", "--modfile"):
			modifiedPeptidesFile = arg
		if opt in ("-M", "--modfile1"):
			modifiedPeptidesFile1 = arg
		if opt in ("-n", "--nonmodfile"):
			nonModifiedPep2ProtFile = arg
		if opt in ("-t","--pep2pro"):
			pep2protein=arg
		if opt in ("-o", "--outputfile"):
			outputFile = arg
		if opt in ("-r", "--relfile"):
			relationsFile = arg
		if opt in ("-V", "--varfile"):
			varFile = arg
		if opt in ("-W", "--varfile1"):
			varFile1 = arg
		if opt in ("-L", "--infofile"):
			infoFile= arg
		elif opt in ("-h", "--help"):
			printHelp(version)
		

            
    # REGION: FILE NAMES SETUP
	if len(analysisName) == 0:
		if len(modifiedPeptidesFile) > 0:
			analysisName = os.path.splitext(os.path.basename(modifiedPeptidesFile))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart

	if len(modifiedPeptidesFile) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(modifiedPeptidesFile)) > 0:
			analysisFolder = os.path.dirname(modifiedPeptidesFile)

	if len(analysisName) == 0:
		if len(modifiedPeptidesFile1) > 0:
			analysisName = os.path.splitext(os.path.basename(modifiedPeptidesFile1))[0]
		else:
			analysisName = defaultAnalysisName

	if len(os.path.dirname(analysisName)) > 0:
		analysisNameFirstPart = os.path.dirname(analysisName)
		analysisName = os.path.basename(analysisName)
		if len(analysisFolder) == 0:
			analysisFolder = analysisNameFirstPart

	if len(modifiedPeptidesFile1) > 0 and len(analysisFolder) == 0:
		if len(os.path.dirname(modifiedPeptidesFile1)) > 0:
			analysisFolder = os.path.dirname(modifiedPeptidesFile1)

    # input
	if len(modifiedPeptidesFile) == 0:
		modifiedPeptidesFile = os.path.join(analysisFolder, analysisName + "_" + defaultModifiedPeptidesFile + defaultTableExtension)

	if len(os.path.dirname(modifiedPeptidesFile)) == 0 and len(analysisFolder) > 0:
		modifiedPeptidesFile = os.path.join(analysisFolder, modifiedPeptidesFile)

	if len(modifiedPeptidesFile1) == 0:
		modifiedPeptidesFile1 = os.path.join(analysisFolder, analysisName + "_" + defaultModifiedPeptidesFile1 + defaultTableExtension)

	if len(os.path.dirname(modifiedPeptidesFile1)) == 0 and len(analysisFolder) > 0:
		modifiedPeptidesFile1 = os.path.join(analysisFolder, modifiedPeptidesFile1)
        
	if len(nonModifiedPep2ProtFile) == 0:
		nonModifiedPep2ProtFile = os.path.join(analysisFolder, analysisName + "_" + defaultnonModifiedPeptidesFile + defaultTableExtension)

	if len(os.path.dirname(nonModifiedPep2ProtFile)) == 0 and len(analysisFolder) > 0:
		nonModifiedPep2ProtFile = os.path.join(analysisFolder, nonModifiedPep2ProtFile)
        
	if len(relationsFile) == 0:
		relationsFile = os.path.join(analysisFolder, analysisName + "_" + defaultRelationsFile + defaultTableExtension)

	if len(os.path.dirname(relationsFile)) == 0 and len(analysisFolder) > 0:
		relationsFile = os.path.join(analysisFolder, relationsFile)

	if len(os.path.dirname(varFile)) == 0 and len(os.path.basename(varFile)) > 0:
		varFile = os.path.join(analysisFolder, varFile)
        
	if len(os.path.dirname(varFile1)) == 0 and len(os.path.basename(varFile1)) > 0:
		varFile1 = os.path.join(analysisFolder, varFile1)  
        
	if len(pep2protein) == 0:
		pep2protein = os.path.join(analysisFolder, analysisName + "_" + defaultpep2protein + defaultTableExtension)

	if len(os.path.dirname(pep2protein)) == 0 and len(analysisFolder) > 0:
		pep2protein = os.path.join(analysisFolder, pep2protein)
# ************** reviewed up to here

	# output
	if len(outputFile) == 0:
		outputFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutput + defaultTableExtension)
	else:
		if len(os.path.dirname(outputFile)) == 0:
			outputFile = os.path.join(analysisFolder, outputFile)

	if len(infoFile) == 0:
		infoFile = os.path.join(analysisFolder, analysisName + "_" + defaultOutputInfo + defaultTableExtension)


	logList.append(["Input modifiedPeptideFile " + str(modifiedPeptidesFile)])
	logList.append(["Input modifiedPeptideFile1 " + str(modifiedPeptidesFile1)])
	logList.append(["Input nonMod_PepTOpro_File " + str(nonModifiedPep2ProtFile)])
	logList.append(["Input pep to protein file " + str(pep2protein)])
	logList.append(["Input relations file: " + relationsFile])
	logList.append(["Input varianceFile: " + varFile])
	logList.append(["Input Second_varianceFile: " + varFile1])
	logList.append(["Output stats file: " + outputFile])
	logList.append(["Output info file: " + infoFile])

    # pp.pprint(logList)
    # sys.exit()

    # END REGION: FILE NAMES SETUP
            
            
	outputList = ZpCalculator(relationsFile=relationsFile,
                              modifiedPeptidesFile=modifiedPeptidesFile, modifiedPeptidesFile1=modifiedPeptidesFile1,
                              nonModifiedPep2ProtFile=nonModifiedPep2ProtFile,
                              varFile=varFile, varFile1=varFile1, pep2protein=pep2protein,outname=outputFile)

	header = "idsup\tXsup\tVsup\tidinf\tXinf\tVinf\tn\tZ\tFDR" #"Sequence\tFASTAProteinDescription\tXp\tVp\tcount\tZp" 
    #######("Fix the header for Xp and Vp")
	stats.saveFile(outputFile, outputList, header)

	if len(infoFile) > 0:
		stats.saveFile(infoFile, logList, "INFO FILE")

# ZpCalculator(relationsFile = "Mod_NonMod_relation.txt",
# modifiedPeptidesFile = "Modifoed_xp_vp.xls",
# nonModifiedPep2ProtFile = "Xq.xls",
# varFile = "variance_file.txt")

# sanxotghost -p"C:\cygwin64\final_data" -rMod_NonMod_relation.txt -mModifoed_xp_vp.xls -nXq.xls -Vvariance_file.txt -aexample -oOutput_file2.txt

#######################################################

if __name__ == "__main__":
	main(sys.argv[1:])
