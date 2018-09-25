__author__ = 'nbagwan'

############ input ##############################
"""
-D C:/Users/surya/Desktop/ProjectData/Script/coding/python/Mappit/Navratan/errorsolv/inputfolder
-a [.xls]
-f peptideAll2protein_lowerNormV.xls
"""


import os
from optparse import OptionParser
import pdb


usage = "usage: %prog -D pathfolder -a File_extension -f FileName -o outputName"

parser = OptionParser(usage=usage)

parser.add_option("-D", "--pathfolder", action="store", type="string", dest="Dir", help="Enter the path of folder")
#parser.add_option("-d", "--subdirs", action="store", type="string", dest="SubDir",help="Enter Subdir True or False")
parser.add_option("-a", "--FileExt", action="store", type="string", dest="Argumets", help="Enter file extension")
parser.add_option("-f", "--file", action="store", type="string", dest="FileName", help="Enter file name")
parser.add_option("-o", "--Outfile", action= "store", type="string", dest="OutDir", help="enter the path of the output folder")
#pdb.st_trace()

(options, args) = parser.parse_args()

if options.Dir: #### belog to parser(dest)
	Dir = options.Dir
else:
	parser.error("enter Directory name -h")

#if options.SubDir:
#	SubDir=options.SubDir
#else:
#	parser.error("enter Sub directory name  -h")

if options.Argumets:
	Argumets = options.Argumets
else:
	parser.error("enter the arguments -h")

if options.FileName:
	FileName = options.FileName
else:
	parser.error("enter the file name -h")

if options.OutDir:
	OutDir=options.OutDir
else:
	parser.error("enter the output folder -o")


## to define which kind of separation is used.................................###

separations="/"



### methods##############

def dir_list(dir_name, subdir, args,fn):
    '''Return a list of file names in directory 'dir_name'
    If 'subdir' is True, recursively access subdirectories under 'dir_name'.
    Additional arguments, if any, are file extensions to add to the list.
    Example usage: fileList = dir_list(r'H:\TEMP', False, 'txt', 'py', 'dat', 'log', 'jpg')
    '''
    fileList = []
#    print os.listdir(dir_name)
    for file in os.listdir(dir_name): ####
#        dirfile = os.path.join(dir_name, file)
        dirfile=dir_name+separations+file
        # print dirfile
        # print os.path.split(dirfile)
#        print dirfile
        if os.path.isfile(dirfile):
            if len(args) == 0:
                fileList.append(dirfile)
            else:
                if os.path.splitext(dirfile)[1][1:] in args and os.path.split(dirfile)[1] == fn:
                    fileList.append(dirfile)
#                    print dirfile

                    # recursively access file names in subdirectories
        elif os.path.isdir(dirfile) and subdir:
            # print "Accessing directory:", dirfile
            fileList += dir_list(dirfile, subdir, args,fn)
            #print fileList
    return fileList


def combine_files(dir,fileList):
    rels1 = [["idinf","\t","X'inf","\t","Vinf","\n"]]
    rels2 = [["idsup","\t","idinf","\n"]]
    W = open(dir+separations+"Rep_higherLevel.xls", "w")
    V = open(dir+separations+"Rep_relations.xls", "w")
    #f = open(fn, 'w')
    for fn in fileList:
	foldname=os.path.split(os.path.split(os.path.split(fn)[0])[0])[1]
	#print foldname
	with open(fn) as file_new:
		next(file_new)
        	for line in file_new:
            #pdb.set_trace()
            		if line != "\n":
                		splits = line.split("\t")
                		rels1.append(
                    [foldname + "_" + splits[0].strip(), "\t", splits[1].strip(), "\t", splits[2].strip(), "\n"])
                		rels2.append([splits[0].strip(), "\t", foldname + "_" + splits[0].strip(), "\n"])

    for ln2 in rels2:
        V.writelines(ln2)
    V.close()

    for ln in rels1:
        W.writelines(ln)
    W.close()







if __name__ == '__main__':
    #search_dir =
    combine_files(dir=OutDir,fileList=dir_list(dir_name=Dir, subdir=True, args=Argumets, fn=FileName))
