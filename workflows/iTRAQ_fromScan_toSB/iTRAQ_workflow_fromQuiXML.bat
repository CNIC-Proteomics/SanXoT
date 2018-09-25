echo off
cls

rem *********************************************
rem ************* INPUT ARGUMENTS ***************
rem *********************************************

echo *** General options ***
set /p programFolder=Program folder: 
set /p workingFolder=Working folder: 
echo :
echo *** QuiXML file options ***
set /p QuiXMLFile=QuiXMLFile (or, better, the XLS associated): 
set /p FirstIon=First reporter ion: 
set /p SecondIon=Second reporter ion: 
echo :
echo *** Systems Biology options *** 
echo *** NOTE1: these files must be in the working folder
echo *** NOTE3: paste only the file name without the full path
echo *** NOTE3: please, make sure the protein identifiers used
echo ***        are the same as in the QuiXML file
echo ***        (usually, the FASTAProteinDescription)
set /p GOconnectFile=GOconnectFile (relations for categories): 
set /p GOconnectPaths=GOconnectFile (all paths): 
set /p MinimumProteins=Minimum number of proteins in category: 
set /p MaxFDR=Maximum FDR of category: 

rem *********************************************
rem ************* DEFINE VARIABLES **************
rem *********************************************

echo :
echo starting...
set ext=exe
set xml2tsv=%programFolder%\xml2tsv.%ext%
set klibrate=%programFolder%\klibrate.%ext%
set sanxot=%programFolder%\sanxot.%ext%
set sanxotsieve=%programFolder%\sanxotsieve.%ext%
set sanxotsqueezer=%programFolder%\sanxotsqueezer.%ext%
set sanxotgauss=%programFolder%\sanxotgauss.%ext%
set sanson=%programFolder%\sanson.%ext%
set arbor=%programFolder%\arbor.%ext%
set aljamia=%programFolder%\aljamia.%ext%

set scanLevel=scan
set peptideLevel=peptide
set proteinLevel=protein
set categoryLevel=category
set categoryToGrandMeanLevel=categoryGrandMean
set proteinToGrandMeanLevel=proteinGrandMean
set spIntegration=scan2peptide
set pqIntegration=peptide2protein
set qbIntegration=protein2category
set spRels=scan2peptide_relations
set pqRels=peptide2proteins_relations
set XsColumn=q_Xs_%FirstIon%_%SecondIon%
set VsColumn=q_Vs_%FirstIon%_%SecondIon%

rem *********************************************
rem ********* PART 0: creation of files *********
rem *********************************************

rem extract scan data file
%aljamia% -x%QuiXMLFile% -p%workingFolder% -a%scanLevel% -o%scanLevel%_uncalibrated.xls -f"[st_excluded]!=excluded" -i"[RAWFileName]-[FirstScan]-[Charge]" -j"[%XsColumn%]" -k"[%VsColumn%]" -R24

rem extract relations files
%aljamia% -x%QuiXMLFile% -p%workingFolder% -a%spRels% -o%spRels%.xls -i"[Sequence]" -j"[RAWFileName]-[FirstScan]-[Charge]" -R24
%aljamia% -x%QuiXMLFile% -p%workingFolder% -a%pqRels% -o%pqRels%.xls -i"[FASTAProteinDescription]" -j"[Sequence]" -R24

rem *********************************************
rem *********** PART 1: integrations ************
rem ************ up to protein level ************
rem *********************************************

rem ********* calibration (k calculation)
%klibrate% -d%scanLevel%_uncalibrated.xls -p%workingFolder% -r%spRels%.xls -a%scanLevel%Cal -o%scanLevel%.xls -g

rem ********* scan to pep
rem get original variance (prior to outlier removal)
%sanxot% -d%scanLevel%.xls -p%workingFolder% -r%spRels%.xls -a%spIntegration%_temp -g
rem remove outliers
%sanxotsieve% -d%scanLevel%.xls -p%workingFolder% -r%spRels%.xls -V%spIntegration%_temp_infoFile.txt -a%spRels%
rem reintegrate, using old variance
%sanxot% -d%scanLevel%.xls -p%workingFolder% -r%spRels%_cleaned.xls -a%spIntegration% -o%peptideLevel%.xls -V%spIntegration%_temp_infoFile.txt -fg

rem ********* pep to prot
rem get original variance (prior to outlier removal)
%sanxot% -d%peptideLevel%.xls -p%workingFolder% -r%pqRels%.xls -a%pqIntegration%_temp -g
rem remove outliers
%sanxotsieve% -d%peptideLevel%.xls -p%workingFolder% -r%pqRels%.xls -V%pqIntegration%_temp_infoFile.txt -a%pqRels%
rem reintegrate, using old variance
%sanxot% -d%peptideLevel%.xls -p%workingFolder% -r%pqRels%_cleaned.xls -a%pqIntegration% -o%proteinLevel%.xls -V%pqIntegration%_temp_infoFile.txt -fg

rem *********************************************
rem ****** PART 2: systems biology triangle *****
rem ************* (removing outliers) ***********
rem *********************************************

rem ********* SB triangle
rem ********* q to GO
rem get original variance (prior to outlier removal)
%sanxot% -d%proteinLevel%.xls -r%GOconnectFile% -p%workingFolder% -a%qbIntegration%_temp_varN -g
rem remove outliers
%sanxotsieve% -d%proteinLevel%.xls -r%GOconnectFile% -p%workingFolder% -V%qbIntegration%_temp_varN_infoFile.txt -a%qbIntegration%_varN -n%GOconnectFile%_cleaned.xls
rem reintegrate, using old variance
%sanxot% -d%proteinLevel%.xls -r%GOconnectFile%_cleaned.xls -p%workingFolder% -a%qbIntegration%_varN -o%categoryLevel%.xls -V%qbIntegration%_temp_varN_infoFile.txt -fg

rem ********* GO to all
%sanxot% -d%categoryLevel%.xls -p%workingFolder% -a%categoryToGrandMeanLevel%_varN -o%categoryToGrandMeanLevel%.xls -Cg -v1
%sanxot% -d%categoryLevel%.xls -p%workingFolder% -a%categoryToGrandMeanLevel%_var0 -o%categoryToGrandMeanLevel%_var0.xls -v0 -Cfg

rem ********* q to all
%sanxot% -d%proteinLevel%.xls -p%workingFolder% -a%proteinToGrandMeanLevel% -o%proteinToGrandMeanLevel%.xls -V%qbIntegration%_temp_varN_infoFile.txt -Cfg

rem *********************************************
rem ********* PART 2b: creation of graphs *******
rem ************* (removing outliers) ***********
rem *********************************************

rem ********* SanXoTSqueezer creates the list of changing categories
%sanxotsqueezer% -l%qbIntegration%_varN_outStats.xls -u%categoryToGrandMeanLevel%_var0_outStats.xls -n%MinimumProteins% -f%MaxFDR% -p%workingFolder% -a%categoryLevel%Squeezed

rem ********* SanXoTGauss creates the graph of coloured sigmoids
%sanxotgauss% -p%workingFolder% -a%categoryLevel%Gaussians -z%proteinToGrandMeanLevel%_outStats.xls -r%GOconnectFile%_cleaned.xls -c%categoryLevel%Squeezed_outList.xls -d1000 -s5 -g

rem ********* Sanson creates the similarity graphs with clusters
%sanson% -p%workingFolder% -a%categoryLevel%Similarities -z%proteinToGrandMeanLevel%_outStats.xls -r%GOconnectFile%_cleaned.xls -c%categoryLevel%Squeezed_outList.xls

rem ********* Arbor creates the tree graph
%arbor% -p%workingFolder% -a%categoryLevel%Arbor -z%proteinToGrandMeanLevel%_outStats.xls -r%GOconnectFile%_cleaned.xls -c%categoryLevel%Squeezed_outList.xls -b%GOconnectPaths%

rem *********************************************
rem ****** PART 3: systems biology triangle *****
rem ************* (INCLUDING outliers) **********
rem *********************************************

rem ********* GO to all
%sanxot% -d%qbIntegration%_temp_varN_higherLevel.xls -p%workingFolder% -a%categoryToGrandMeanLevel%_iOuts_varN -o%categoryToGrandMeanLevel%_iOuts.xls -Cg -v1
%sanxot% -d%qbIntegration%_temp_varN_higherLevel.xls -p%workingFolder% -a%categoryToGrandMeanLevel%_iOuts_var0 -o%categoryToGrandMeanLevel%_iOuts_var0.xls -v0 -Cfg


rem *********************************************
rem ********* PART 3b: creation of graphs *******
rem ************* (INCLUDING outliers) **********
rem *********************************************

rem ********* SanXoTSqueezer creates the list of changing categories
%sanxotsqueezer% -l%qbIntegration%_temp_varN_outStats.xls -u%categoryToGrandMeanLevel%_iOuts_var0_outStats.xls -n%MinimumProteins% -f%MaxFDR% -p%workingFolder% -a%categoryLevel%Squeezed_iOuts

rem ********* SanXoTGauss creates the graph of coloured sigmoids
%sanxotgauss% -p%workingFolder% -a%categoryLevel%Gaussians_iOuts -z%proteinToGrandMeanLevel%_outStats.xls -r%GOconnectFile% -c%categoryLevel%Squeezed_iOuts_outList.xls -d1000 -s5 -g

rem ********* Sanson creates the similarity graphs with clusters
%sanson% -p%workingFolder% -a%categoryLevel%Similarities_iOuts -z%proteinToGrandMeanLevel%_outStats.xls -r%GOconnectFile% -c%categoryLevel%Squeezed_iOuts_outList.xls

rem ********* Arbor creates the tree graph
%arbor% -p%workingFolder% -a%categoryLevel%Arbor_iOuts -z%proteinToGrandMeanLevel%_outStats.xls -r%GOconnectFile% -c%categoryLevel%Squeezed_iOuts_outList.xls -b%GOconnectPaths%

echo on